from Motor import Motor
from servo import Servo
from Line_Tracking import *
from Ultrasonic import Ultrasonic
import picamera2
import time
from picamera2 import Picamera2
import pygame
import time
import numpy as np
from utils import create_text
from collections import deque


class Vehicle:
    def __init__(self):
        self.motor = Motor()
        self.servo = Servo()
        self.servo_angles = self.servo.initial
        self.ultrasonic_sensors = Ultrasonic()
        self.infrared_sensors = Line_Tracking()
        self.left_sensor = False
        self.middle_sensor = False
        self.right_sensor = False
        self.wheel_speed = (0, 0, 0, 0)
        self.key_states = {}
        self.ultrasonic_threshold = {'backup': 5, 'avoid': 20} 
        self._init_swiviel_states()
        self._init_camera()
    
    def _init_camera(self):
        self.camera = Picamera2()
        self.camera.start()
        time.sleep(1)
        print("Camera Initialized")
    
    def _init_swiviel_states(self):
         self.swivel_state = {
            'leftright': 0,
            'updown': 0
            }
         self.swivel_dir = 'left'

    def reset_servo(self):
        self.servo._init_angles(prior=self.servo_angles)

    def get_vision(self):
        return self.camera.capture_array('main')[:, :, :3].transpose(1, 0, 2)

    def get_ultrasonic_data_string(self):
        return f'OBSTACLE DISTANCE: {self.ultrasonic_sensors.get_distance()} CM'

    def _update_servo(self, event):
        if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
            if event.key == pygame.K_LEFT:
                self.servo_angles[0] -= 1
            else:
                self.servo_angles[0] += 1
            self.servo.setServoPwm('0', self.servo_angles[0])

        if event.key in [pygame.K_DOWN, pygame.K_UP]:
            if event.key == pygame.K_DOWN:
                self.servo_angles[1] += 1
            else:
                self.servo_angles[1] -= 1
            self.servo.setServoPwm('1', self.servo_angles[1])
        time.sleep(0.10)
        print(self.servo_angles)

    def halt(self):
        self.wheel_speed = (0, 0, 0, 0)
        self.motor.setMotorModel(*self.wheel_speed)
    
    def line_is_detected(self):
        return all([self.left_sensor, self.middle_sensor, self.right_sensor])
        
    def get_infrared_data(self):
        line = self.infrared_sensors
        if GPIO.input(line.IR01)!=True and GPIO.input(line.IR02)==True and GPIO.input(line.IR03)!=True:
            self.infrared_sensors.found_line = True
            self.middle_sensor = True
            return True
        elif GPIO.input(line.IR01)!=True and GPIO.input(line.IR02)!=True and GPIO.input(line.IR03)==True:
            self.infrared_sensors.found_line = True
            self.right_sensor = True
            return True
        elif GPIO.input(line.IR01)==True and GPIO.input(line.IR02)!=True and GPIO.input(line.IR03)!=True:
            self.infrared_sensors.found_line = True
            self.left_sensor = True
            return True
        else:
            self.infrared_sensors.found_line = False
            self.line_location = "NO LINE DETECTED"
            return False


    def _can_go_forward(self):
        reading = self.ultrasonic_sensors.get_distance() 
        while reading == 0:
            reading = self.ultrasonic_sensors.get_distance()
        print(f'reading: {reading} | threshold: {self.ultrasonic_threshold["avoid"]}')
        return reading > self.ultrasonic_threshold['avoid']
    
    def _needs_to_reverse(self):
        return self.ultrasonic_sensors.get_distance() <= self.ultrasonic_threshold['backup']
    
    def _reverse(self, duration=0.5):
        start = time.time()
        self.motor.setMotorModel(-1000, -1000, -1000, -1000)
        while True:
            if (time.time() - start) > duration:
                break
        self.halt()
        return

    def _program_exit_requested(self): 
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == ord('q'):
                return True
        return False
    
    def _try_reverse(self, screen):
        self._auto_turn_around(screen)
        if self._get_distances(screen):
            return True
        return False

    def begin_roomba_mode(self, screen):
        print("BEGINNING ROOMBA PROGRAM")
        while True:
            if self._program_exit_requested():
                self.halt()
                return
            if self._can_go_forward():
                self.motor.setMotorModel(1000, 1000, 1000, 1000)
            else:
                self.halt()
                acceptable = False
                if self._try_reverse(screen):
                    acceptable = True
                while not acceptable:
                    self._rotate(screen, seconds=0.2)
                    acceptable = self._get_distances(screen)
            image_surface = pygame.surfarray.make_surface(self.get_vision())
            screen.blit(image_surface, (0,0))
            screen.blit(*create_text(self.get_ultrasonic_data(), offset=(400, 300)))
            screen.blit(*create_text("ROOMBA MODE", offset=(400, 300)))
            pygame.display.flip()
                

    def _get_distances(self, ):
        acceptable = False
        prev = self.servo_angles[0]
        i = 0
        while i < 15:
            distance = self.ultrasonic_sensors.get_distance()
            if distance > self.ultrasonic_threshold['avoid']:
                return True
            self.servo_angles[0] -= 1
            self.servo.setServoPwm('0', self.servo_angles[0])
            i += 1
        i = 0
        while i < 30:
            distance = self.ultrasonic_sensors.get_distance()
            if distance > self.ultrasonic_threshold['avoid']:
                return True
            self.servo_angles[0] += 1
            self.servo.setServoPwm('0', self.servo_angles[0])
            i += 1
        i = 0
        while i < 15:
            distance = self.ultrasonic_sensors.get_distance()
            if distance > self.ultrasonic_threshold['avoid']:
                return True
            self.servo_angles[0] -= 1
            self.servo.setServoPwm('0', self.servo_angles[0])
            i += 1
        return False 

    def _rotate(self, pivot_amount):
        if pivot_amount < 0:
            wheel_speed = (-1500, -1500, 2000, 2000)
        else:
            wheel_speed = (2000, 2000, -1500, -1500)
        duration = abs(pivot_amount / 60)
        print(duration)
        start = time.time()
        self.motor.setMotorModel(*wheel_speed)
        while True:
            if (time.time() - start) > duration:
                break
        self.halt()
        return 

    def _auto_turn_around(self, screen=None):
        '''360 deg spin.'''
        choice = np.random.randint(0, 2)
        if choice == 0:
            wheel_speed = (2000, 2000, -1500, -1500)
        else:
            wheel_speed = (-1500, -1500, 2000, 2000)
        start_time = time.time()
        while (time.time() - start_time) < 1.25:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == ord('q'):
                    self.halt()
                    return
            self.motor.setMotorModel(*wheel_speed)
        self.halt()
        return

    def _update_sensors(self):
        return 
    
    def _auto_reverse(self, screen):
        '''backup roughly 10 cm'''
        start_time = time.time()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == ord('q'):
                    self.halt()
                    return
            if self.ultrasonic_sensors.get_distance() < self.ultrasonic_threshold:
                self._update_sensors()
                self._update_screen(screen)
                self.motor.setMotorModel(-1000, -1000, -1000, -1000)
            if time.time() - start_time < 1:
                self._update_sensors()
                self._update_screen(screen)
                self.motor.setMotorModel(-1000, -1000, -1000, -1000)

            else:
                self.halt()
                return

    def _look_left(self):
        self.reset_servo()
        prev = self.servo_angles[0]
        i = 0
        while i < 45:
            self.servo_angles[0] -= 5
            self.servo.setServoPwm('0', self.servo_angles[0])
            i += 5
            time.sleep(0.00125)
        distance = self.ultrasonic_sensors.get_distance()
        self.servo_angles[0] = prev
        self.servo.setServoPwm('0', self.servo_angles[0])
        return distance
    
    def _look_right(self):
            self.reset_servo()
            prev = self.servo_angles[0]
            i = 0
            while i < 45:
                self.servo_angles[0] += 5
                self.servo.setServoPwm('0', self.servo_angles[0])
                i += 5
                time.sleep(0.00125)
            distance = self.ultrasonic_sensors.get_distance()
            self.servo_angles[0] = prev
            self.servo.setServoPwm('0', self.servo_angles[0])
            return distance
    

    def _update_screen(self, screen):
        image_surface = pygame.surfarray.make_surface(self.get_vision())
        screen.blit(image_surface, (0,0))
        screen.blit(*create_text(self.get_ultrasonic_data_string(), offset=(400, 300)))
        screen.blit(*create_text("ROOMBA MODE", offset=(400, 300)))
        pygame.display.flip()
    
        
        
            
        
        
        


    def begin_autonomous_line_tracking(self):
        end_count = 0
        while True:
            ### Provided by robot car company
            self.infrared_sensors.LMR=0x00
            if GPIO.input(self.infrared_sensors.IR01)==True:
                self.infrared_sensors.LMR=(self.infrared_sensors.LMR | 4)
            if GPIO.input(self.infrared_sensors.IR02)==True:
                self.infrared_sensors.LMR=(self.infrared_sensors.LMR | 2)
            if GPIO.input(self.infrared_sensors.IR03)==True:
                self.infrared_sensors.LMR=(self.infrared_sensors.LMR | 1)

            if self.infrared_sensors.LMR==2:
                self.motor.setMotorModel(800,800,800,800)
            elif self.infrared_sensors.LMR==4:
                self.motor.setMotorModel(-1500,-1500,2500,2500)
            elif self.infrared_sensors.LMR==6:
                self.motor.setMotorModel(-2000,-2000,4000,4000)
            elif self.infrared_sensors.LMR==1:
                self.motor.setMotorModel(2500,2500,-1500,-1500)
            elif self.infrared_sensors.LMR==3:
                self.motor.setMotorModel(4000,4000,-2000,-2000)
            elif self.infrared_sensors.LMR==7:
                self.motor.setMotorModel(0, 0, 0, 0)
            elif self.infrared_sensors.LMR == 0:
                end_count += 1

            if end_count == 50000:
                print("EXITING")
                break
            if self.infrared_sensors.LMR != 0:
                end_count = 0
        return




