from Kit.Motor import Motor
from Kit.servo import Servo
from Kit.Line_Tracking import *
from Kit.Ultrasonic import Ultrasonic
import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
import pygame
import time
import numpy as np
from core.utils import create_text
from collections import deque
from core.odometer import Odometer
from core.objdet import ObjDetModel
from core.utils import *
from routing.search import AStar
from routing.maze import Gridworld
import os
import math
import matplotlib.pyplot as plt


class Vehicle:
    def __init__(self, initial_coordinates=None):
        self.motor = Motor()
        self.servo = Servo()
        self.servo_angles = self.servo.initial
        self.ultrasonic_sensors = Ultrasonic()
        self.infrared_sensors = Line_Tracking()
        self.odometer = Odometer(initial_coordinates)
        self.left_sensor = False
        self.middle_sensor = False
        self.right_sensor = False
        self.key_states = {}
        self.ultrasonic_threshold = {'backup': 5, 'avoid': 20} 
        self.max_ultrasonic_distance = 40
        self._init_camera()
        self.objdet = ObjDetModel()
        self.gps = AStar()
        self.optimal_path = None

    def _init_camera(self):
        self.camera = Picamera2()
        self.camera.start()
        time.sleep(1)
        print("Camera Initialized")
    
    def _reset_servo(self):
        self.servo._init_angles(prior=self.servo_angles)

    def get_vision(self):
        return self.camera.capture_array('main')[:, :, :3].transpose(1, 0, 2)

    def halt(self):
        self.wheel_speed = (0, 0, 0, 0)
        self.motor.setMotorModel(*self.wheel_speed)
    
    def _gather_single_reading(self, adjust=False) -> dict:
        x, y, yaw = self.odometer.get_vehicle_state()
        if adjust:
            yaw = self._adjust_for_servo_angle(yaw=yaw, servo_angle=self.servo_angles[0])
        distance = self.ultrasonic_sensors.get_distance()
        reading = {'x_y_yaw': (x, y, yaw), 'distance': distance}
        return reading 
    
    def _adjust_for_servo_angle(self, yaw, servo_angle):
        return yaw + servo_angle 
    
    def _gather_readings(self) -> list[dict]:
        initial_servo_angles = self.servo_angles
        readings = []
        self.adjust_servo(direction='left', degrees=90)
        for i in range(180):
            self.adjust_servo(direction='right', degrees=1)
            readings.append(self._gather_single_reading())
        self.adjust_servo(direction='left', degrees=90)
        return readings
    
    def adjust_servo(self, direction, degrees):
        initial_angle = self.servo_angles[0]
        delta = (1 if direction == 'right' else -1)
        total_delta = 0
        while total_delta < abs(degrees):
            self.servo_angles[0] += delta
            self.servo.setServoPwm('0', self.servo_angles[0])
            total_delta += 1
        
    def gather_servo_sweep_coords(self) -> list[int]:
        '''pivot the servo to sweep the environment and gather a collection
        of ultrasonic sensor readings
        '''
        readings = self._gather_readings()
        coords = self._transform_readings_to_coordinates(readings)
        return coords
    
    def _transform_readings_to_coordinates(self, readings):
        '''
        Transform a batch of readings to a batch of coordinates
        `reading[i] format: {"x_y_yaw": (int, int, int), "distance": int}
        where
        "x_y_yaw" was the state of the vehicle at time of reading
        "distance" is the signal measured from that state
        '''
        res = []
        for reading in readings:
            coord = self.get_object_coordinates(reading_provided=reading)
            if coord:
                res.append(coord)
        return res

    def move(self, event, cm):
        if not any([event, cm]):
            return self.odometer.get_vehicle_state(), []
        else:
            key_map = {ord('w'): 'forward', ord('s'): 'backward', ord('a'): 'left', ord('d'): 'right'}
            direction = key_map[event.key]
            duration = 0
            if direction == 'left':
                obstacle_coords = self.custom_rotate(degrees=30)
            elif direction == 'right':
                obstacle_coords = self.custom_rotate(degrees=-30)
            else:
                obstacle_coords, duration = self._move(direction, cm)
            
            current_position = self.odometer.data.copy()
            current_position['duration'] = duration
            current_position['direction'] = direction 
            self.odometer._all_prior_vehicle_states.append(current_position)
            return self.odometer.get_vehicle_state(), obstacle_coords

    def _move(self, direction, cm):
        '''moves vehicle one centimeter'''
        power_map = {'forward': 1500, 'backward': -1500}
        power = power_map[direction]
        duration = 0.45 * (cm / 23)
        start_time = time.time()
        self.motor.setMotorModel(*(power, power, power, power))
        readings = []
        while (time.time() - start_time) < duration:
            readings.append(self._gather_single_reading())
        self.halt()
        self.odometer.update_vehicle_state(direction, cm)
        return self._transform_readings_to_coordinates(readings), duration
    
    def _move_for_duration(self, duration, direction):
        '''moves vehicle one centimeter'''
        power = 1500
        cm = round((23 * duration) / 0.45)
        start_time = time.time()
        self.motor.setMotorModel(*(power, power, power, power))
        readings = []
        while (time.time() - start_time) < duration:
            readings.append(self._gather_single_reading())
        self.halt()
        self.odometer.update_vehicle_state(direction=direction, units=cm)
        return self._transform_readings_to_coordinates(readings), duration
        

    def custom_rotate(self, degrees):
        def get_rotate_wheel_power(degrees):
            if degrees > 0:
                return ((-power + 500), (-power + 500), power, power)
            else:
                return (power, power, (-power + 500), (-power + 500))
        power = 3000
        duration = abs(degrees)/360 * 2
        start_time = time.time()
        self.motor.setMotorModel(*get_rotate_wheel_power(degrees))
        readings = []
        while (time.time() - start_time) < duration:
            readings.append(self._gather_single_reading())

        self.halt()
        self.odometer.update_vehicle_yaw(degrees)
        return self._transform_readings_to_coordinates(readings)

    def get_coordinates(self):
        x, y, yaw = self.odometer.get_vehicle_state()
        return (x, y)

    def get_object_coordinates(self, reading_provided=None) -> tuple:
        '''Obtain the proper (x,y) coords to plot ultrasonic reading
        (post-reading and/or real time)
        '''
        #logic to handle readings gathered from servo_sweep
        if reading_provided:
            x, y, yaw = reading_provided['x_y_yaw']
            distance = reading_provided['distance']
            angle_radians = math.radians(yaw)
            delta_x = x - (distance * math.sin(angle_radians))
            delta_y = y - (distance * math.cos(angle_radians))
            delta_x, delta_y = round(delta_x), round(delta_y)
            return (delta_x, delta_y)
        #logic to handle real time ultrasonic sensor reading
        if not reading_provided:
            x, y, yaw = self.odometer.get_vehicle_state()
            distance = self.ultrasonic_sensors.get_distance()
            angle_radians = math.radians(yaw)
            delta_x = x - (distance * math.sin(angle_radians))
            delta_y = y - (distance * math.cos(angle_radians))
            delta_x, delta_y = round(delta_x), round(delta_y)
            return (delta_x, delta_y)
    
    def _get_ultrasonic_beam_coords(self, degrees):
        x1, y1, yaw = self.odometer.get_vehicle_state()
        endx, endy = self._get_max_ultrasonic_distance_coords(x1, y1, yaw+degrees)
        return [(x1, y1), (endx, endy)]
    
    def _get_max_ultrasonic_distance_coords(self, x, y, yaw):
        distance = self.max_ultrasonic_distance
        angle_radians = math.radians(yaw)
        delta_x = x - (distance * math.sin(angle_radians))
        delta_y = y - (distance * math.cos(angle_radians))
        delta_x, delta_y = round(delta_x), round(delta_y)
        return (delta_x, delta_y)
        
    def realtime_ultrasonic_sweep(self, window):
        initial_servo_angles = self.servo_angles
        self.adjust_servo(direction='left', degrees=90)
        time.sleep(1)
        window.draw_ultrasonic_beam(coords=self._get_ultrasonic_beam_coords(degrees=90))
        for i in range(181):
            if i % 10 == 0:
                reading = self._gather_single_reading(adjust=True)
                coords = self.get_object_coordinates(reading)
                window.update_obstacle_location(coords)
            if i % 3 == 0 or i == 180:
                window.draw_ultrasonic_beam(coords=self._get_ultrasonic_beam_coords(degrees=90-i))
            self.adjust_servo(direction='right', degrees=1)
        self.adjust_servo(direction='left', degrees=90) 
        window.update_vehicle_obstacle_readings(self.odometer.get_vehicle_state(), [])
        
    def detect_objects(self):
        return self.objdet.predict(self.get_vision())
    
    def _determine_yaw_delta(self, xy_coord):
        '''
         x,  y (starting coordinate)
        _x, _y (target coordinates)
        dx, dy (delta between coordinates)
        '''
        x, y, yaw = self.odometer.get_vehicle_state()
        _x, _y = xy_coord
        dx = (_x - x)
        dy = (_y - y)
        desired_yaw = math.atan2(dy, dx)
        delta_yaw = (desired_yaw - yaw)
        delta_yaw_degrees = math.degrees(delta_yaw)
        return (_x, _y), delta_yaw_degrees

    def _move_to_coordinate(self, target_coord) -> None:
        target_x, target_y = target_coord 
        while True:
            self._move(direction='foward', cm=23)
            x, y, yaw = self.odometer.get_vehicle_state()
            if x == target_x and y == target_y:
                break
        
    def follow_route(self, route)-> None:
        '''Given a route of coordinate pair (x,y) steps, the vehicle
        will move to each coordinate until coordinate list is empty'''
        while route:
            target_x, target_y, _ = list(route.pop(0).values())
            target_coord, delta_yaw_degrees = self._determine_yaw_delta(xy_coord=(target_x, target_y)) #TODO 
            self.custom_rotate(degrees=delta_yaw_degrees)
            self._move_to_coordiate(target_coord)
    
    def return_to_origin(self) -> None:
        #TODO USE THIS AS TEMPLATE TO CREATE PATH FROM COORD TO COORD)
        # get route to origin
        route_to_origin = self.odometer._all_prior_vehicle_states[::-1]
        # I have my route to origin and my vehicle state is at the current vehicle position
        # all yaws in route to origin are the angles at which the movement forward was made --> - yaw will reverse step
        while len(route_to_origin) > 0:
            #1. get the coordinate i landed at and the yaw that got me there
            #2. adjust my current yaw such that its the negative of the yaw that got me there (- yaw)
            #3. Move unit
            x, y, forward_yaw, duration, direction = list(TESTING_route_to_origin.pop(0).values())
            opp_direction = ('forward' if direction == 'backward' else 'backward')
            current_vehicle_orientation = self.odometer.data['yaw']
            desired_vehicle_orientation = current_vehicle_orientation - 180
            delta_vehicle_orientation = (current_vehicle_orientation + desired_vehicle_orientation) % 360
            self.custom_rotate(degrees=delta_vehicle_orientation)
            if duration:
                self._move_for_duration(duration=duration, direction=opp_direction)
        self.halt()
        self.custom_rotate(180)
    
    def calculate_optimal_path(self, grid, start_coord, target_coord) -> None:
        self.gps.initialize_grid(grid)
        self.optimal_path = self.gps(start_coord, target_coord)


