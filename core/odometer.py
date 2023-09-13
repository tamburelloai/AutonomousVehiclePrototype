import numpy as np
from enum import Enum


class Odometer:
    def __init__(self):
        self.WHEElBASE = 0 #cm
        self.WHEEL_DIAMETER  = 0 #cm
        self.MOTOR_AXLE_DIAMETER = 0 #cm
        self.WHEEL_INFO_cm = {
            'wheelbase': 15,
            'diameter': 5,
            'Dpwr': np.pi * 5
        }
        self.CAR_INFO_cm = {
            'width': 15,  # front wheel (left) to front wheel (right)
            'length': 21  # rear wheels to front wheels
        }
        self.starting_position = (0, 0)

    def get_wheel_signs(self, wheel_movement):
        signs = np.where(wheel_movement > 0)
        if all(signs): # all positive signs ==> forward
           return 1
        elif not any(signs): #all negative signs ==> backward
            return -1
        else: #mixture positive/negative signs ==> rotating
            return 0

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
        #record odometry data given wheel movement
        pass


class MovementType(Enum):
    FORWARD = 1
    ROTATING = 0
    BACKWARD = -1
