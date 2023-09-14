import numpy as np
from enum import Enum


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
    def __init__(self):
        self.wheel_info = WheelInfo()
        self.car_info = CarInfo()
        self.starting_position = (0, 0)


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
