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
import os


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
        self._init_camera()

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
    
    def _gather_readings(self) -> list[dict]:
        def adjust_for_servo_angle(yaw, servo_angle):
            return yaw
         
        def gather_reading()-> dict:
            x, y, yaw = self.odometer.get_vehicle_state()
            yaw = adjust_for_servo_angle(yaw=yaw, servo_angle=self.servo_angles[0])
            distance = self.ultrasonic_sensors.get_distance()
            reading = {'x_y_yaw': (x, y, yaw), 'distance': distance}
            return reading
        
        initial_servo_angles = self.servo_angles
        readings = []
        self.adjust_servo(direction='left', degrees=90)
        for i in range(180):
            self.adjust_servo(direction='right', degrees=1)
            readings.append(gather_reading())
        return readings
        
        
        readings = self.servo.cycle()
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
        key_map = {ord('w'): 'forward', ord('s'): 'backward', ord('a'): 'left', ord('d'): 'right'}
        direction = key_map[event.key]
        if direction == 'left':
            self.custom_rotate(degrees=30)
        elif direction == 'right':
            self.custom_rotate(degrees=-30)
        else:
            self._move(direction, cm)
        os.system('clear')
        return self.odometer.get_vehicle_state(), self.get_object_coordinates()

    def _move(self, direction, cm):
        '''moves vehicle one centimeter'''
        power_map = {'forward': 1500, 'backward': -1500}
        power = power_map[direction]
        duration = 0.45 * (cm / 23)
        start_time = time.time()
        self.motor.setMotorModel(*(power, power, power, power))
        while (time.time() - start_time) < duration:
            continue
        self.halt()
        self.odometer.update_vehicle_state(direction, cm)

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
        while (time.time() - start_time) < duration:
            continue
        self.halt()
        self.odometer.update_vehicle_yaw(degrees)

    def get_coordinates(self):
        x, y, yaw = self.odometer.get_vehicle_state()
        return (x, y)

    def get_object_coordinates(self, reading_provided=None) -> tuple:
        '''Obtain the proper (x,y) coords to plot ultrasonic reading
        (post-reading and/or real time)
        '''
        def bad_distance_signal(distance):
            '''returns true if distance in acceptable range (1, 40)'''
            return any([(distance <= 0), (distance >= 40)]) 
        #logic to handle readings gathered from servo_sweep
        if reading_provided:
            x, y, yaw = reading_provided['x_y_yaw']
            distance = reading_provided['distance']
            if bad_distance_signal(distance):
                return None
            angle_radians = math.radians(yaw)
            delta_x = x + (distance * math.cos(angle_radians))
            delta_y = y + (distance * math.sin(angle_radians))
            delta_x, delta_y = round(delta_x), round(delta_y)
            return (delta_x, delta_y)
        #logic to handle real time ultrasonic sensor reading
        if not reading_provided:
            x, y, yaw = self.odometer.get_vehicle_state()
            distance = self.ultrasonic_sensors.get_distance()
            if bad_distance_signal(distance):
                return None
            angle_radians = math.radians(yaw)
            delta_x = x + (distance * math.cos(angle_radians))
            delta_y = y + (distance * math.sin(angle_radians))
            delta_x, delta_y = round(delta_x), round(delta_y)
            return (delta_x, delta_y)
        