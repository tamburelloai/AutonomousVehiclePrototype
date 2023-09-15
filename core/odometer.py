import numpy as np
from enum import Enum
import math
import sys
import os


class WheelInfo:
    def __init__(self):
        self.WHEEL_DIAMETER = 6.6
        self.WHEEL_TIRE_WIDTH = 2.6
        self.MOTOR_AXLE_DIAMETER = 0  # cm

class CarInfo:
    def __init__(self):
        self.width_left_to_right =  18
        self.length_head_to_tail = 22

class Odometer:
    def __init__(self, initial_coordinates=None):
        self.wheel_info = WheelInfo()
        self.car_info = CarInfo()
        self.data = {
            'x_coord': 0,
            'y_coord': 0,
            'yaw': 0,
        }
        if initial_coordinates:
            x, y = initial_coordinates
            self.data['x_coord'] = x
            self.data['y_coord'] = y
    
    def get_datastring(self):
        return f"X: {self.data['x_coord']} | Y: {self.data['y_coord']} | YAW: {self.data['yaw']}"

    def get_vehicle_state(self):
        return list(self.data.values())

    def update_vehicle_state(self, direction, units):
        angle_radians = math.radians(self.data['yaw'])
        delta_x = -(units * math.sin(angle_radians))
        delta_y = -(units * math.cos(angle_radians))
        if direction == 'forward':
            self.data['x_coord'] += round(delta_x)
            self.data['y_coord'] += round(delta_y)
        else:
            self.data['x_coord'] -= round(delta_x)
            self.data['y_coord'] -= round(delta_y)

    def update_vehicle_yaw(self, degrees):
        prev = self.data['yaw']
        updated = (prev + degrees)
        if updated >= 360:
            updated = updated % 360
        elif updated <= -360:
            updated = updated % 360
        self.data['yaw'] = updated
        os.system('clear')
        print(self.get_datastring())

    def get_wheel_signs(self, wheel_movement):
        '''Determines the type of movement just recorded based
        on the wheel rotation information (wheel_movement)
        wheel_movement: (tuple(int)) Four integers containing the power sent to each wheel
        '''
        signs = np.where(wheel_movement > 0)
        if all(signs): return 1
        elif not any(signs): -1
        else: return 0

    def get_movement_type(self, wheel_movement):
        assert isinstance(wheel_movement, np.ndarray)
        movement = self.get_wheel_signs(wheel_movement)
        if movement == MovementType.FORWARD:
            pass
        elif movement == MovementType.ROTATING:
            pass
        elif movement == MovementType.BACKWARD:
            pass

    def __call__(self, wheel_movement):
        '''Record odometry data and update values'''
        movement_type = self.get_movement_type(wheel_movement)
        pass

class MovementType(Enum):
    FORWARD  = 1
    ROTATING = 0
    BACKWARD = -1
