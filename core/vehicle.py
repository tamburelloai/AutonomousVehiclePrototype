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

class Vehicle:
    def __init__(self):
        self.motor = Motor()
        self.servo = Servo()
        self.servo_angles = self.servo.initial
        self.ultrasonic_sensors = Ultrasonic()
        self.infrared_sensors = Line_Tracking()
        self.odometer = Odometer()
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

    def move(self, event, units=1):
        key_map = {ord('w'): 'forward', ord('s'): 'backward'}
        direction = key_map[event.key]
        self._move(direction, units)

    def _move(self, direction, units):
        power_map = {'forward': 1000, 'backward': -1000}
        power = power_map[direction]
        duration = 1 * units
        start_time = time.time()
        self.motor.setMotorModel(*(power, power, power, power))
        while (time.time() - start_time) < duration:
            continue
        self.halt()
        self.odometer.update_vehicle_state(direction, units)

    def custom_rotate(self, degrees):
        def get_rotate_wheel_power(degrees):
            if degrees > 0:
                return ((-power + 500), (-power + 500), power, power)
            else:
                return (power, power, (-power + 500), (-power + 500))
        power = 2500
        duration = abs(degrees)/360 * 2
        start_time = time.time()
        self.motor.setMotorModel(*get_rotate_wheel_power(degrees))
        while (time.time() - start_time) < duration:
            continue
        self.halt()
        self.odometer.update_vehicle_yaw(degrees)

