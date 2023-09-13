import pygame
from picamera2 import Picamera2
from core.vehicle import Vehicle
import numpy as np
from Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi.Code.Server.utils import create_text, pickle_servo_angles
import numpy as np
import sys
import time


def update_screen_roomba_mode(screen):
    screen.fill((0, 0, 0))
    screen.blit(*create_text("ROOMBA MODE", offset=(50, 50)))
    screen.blit(*create_text("Press any key to exit", offset=(50, 150)))
    
if __name__ == "__main__":
    try:
        screenW, screenH = 250, 250
        vehicle = Vehicle()
        vehicle.reset_servo()
        pygame.init()
        screen = pygame.display.set_mode((screenW, screenH))
        session = True
        while session:
            print(vehicle.ultrasonic_sensors.get_distance())
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    vehicle.halt()
                    pickle_servo_angles(vehicle.servo_angles)
                    pygame.quit()
                    session = False
                    break
            if vehicle._can_go_forward():
                vehicle.motor.setMotorModel(1000, 1000, 1000, 1000)
            else:
                vehicle.halt()
                safe = False
                vehicle.servo_angles[0] -= 45
                pivot_amount = -45
                vehicle.servo.setServoPwm('0', vehicle.servo_angles[0])
                while not safe:
                    vehicle.servo_angles[0] += 5
                    pivot_amount += 5
                    vehicle.servo.setServoPwm('0', vehicle.servo_angles[0])
                    safe = vehicle._can_go_forward()
                    print('found safe to go forward')
                vehicle.reset_servo()
                vehicle._rotate(pivot_amount)
            update_screen_roomba_mode(screen)            
            pygame.display.flip()
            
    except KeyboardInterrupt:
        vehicle.halt()
        pickle_servo_angles(vehicle.servo_angles)



