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
        self.wheel_speed = (0, 0, 0, 0)
        self.orientation = 0

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
        #TODO connect wheel_speed change to an automatic update of self.motor.setMotor..
        self.wheel_speed = (0, 0, 0, 0)
        self.motor.setMotorModel(*self.wheel_speed)
    
    def update_wheels(self, event):
        if event.key == ord('w'):
            self.wheel_speed = (1500, 1500, 1500, 1500)
        elif event.key == ord('s'):
            self.wheel_speed = (-1500, -1500, -1500, -1500)
    
    def move(self, event=None, speed=None):
        if event:
            self.update_wheels(event)
        elif speed:
            self.wheel_speed = speed
        self.motor.setMotorModel(*self.wheel_speed)

    def custom_rotate(self, degrees):
        starting_or = self.orientation
        power = 2500
        duration = abs(degrees)/360 * 2
        start_time = time.time()
        if degrees > 0:
            self.motor.setMotorModel(*((-power+500), (-power+500), power, power))
        elif degrees < 0:
            self.motor.setMotorModel(*(power, power, (-power+500), (-power+500)))
        while (time.time() - start_time) < duration:
            continue
        self.halt()
        self.orientation += degrees
        self.orientation = self.orientation % 360
        print(f'orientation change: {starting_or} --> {self.orientation}')