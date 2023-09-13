
import pygame
import os
import sys
from picamera2 import Picamera2
import time
from core.vehicle import Vehicle
import numpy as np
import pickle

colors = {
        'gray': (169, 169, 169),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'black': (0, 0, 0),
        'yellow': (255, 255, 0)
        }

def get_image_surface(arr: np.ndarray):
    return pygame.surfarray.make_surface(arr)

def pickle_servo_angles(servo_angles):
    with open("servo_angles.pickle", "wb") as f:
        pickle.dump(servo_angles, f)

def display_dashcam(screen, vehicle, screenW, screenH, camW, camH):
    xDelta = 0
    yDelta = (screenH - camH)
    image_surface = get_image_surface(vehicle.get_vision())
    screen.blit(image_surface, (xDelta,yDelta))


if __name__ == "__main__":
    try:
        screenW, screenH = 950, 700
        camW, camH = 640, 480
        vehicle = Vehicle()
        pygame.init()
        screen = pygame.display.set_mode((screenW, screenH))
        session = True
        while session:
            screen.fill((0, 0, 0))
            #display_dashcam(screen, vehicle, screenW, screenH, camW, camH)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pickle_servo_angles(vehicle.servo_angles)
                    pygame.quit()
                    session = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [ord(x) for x in 'wasd']:
                        vehicle.move(event)
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        vehicle._update_servo(event)
                    if event.key == ord('r'):
                        vehicle.reset_servo()
                    if event.key == pygame.K_COMMA:
                        vehicle._look_left(screen)
                    if event.key == pygame.K_PERIOD:
                        vehicle._look_right(screen)
                    if event.key == ord('o'):
                        vehicle.custom_rotate(degrees=int(input('enter degrees: ')))
                else:
                    vehicle.halt()


    except KeyboardInterrupt:
        pickle_servo_angles(vehicle.servo_angles)



