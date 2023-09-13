
import pygame
import os
import sys
from picamera2 import Picamera2
import time
from core.vehicle import Vehicle
import numpy as np
import pickle
from core.utils import create_text


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

def display_ultrasonic_sensor_data(screen, vehicle, screenW, screenH, camW, camH):
    threshold = vehicle.ultrasonic_threshold
    sensor_reading = vehicle.ultrasonic_sensors.get_distance()
    display_empty_bar(screen, vehicle, screenW, screenH, camW, camH, max_val=100, min_val=0)
    xDelta = camW + 10
    yDelta = screenH - camH + 10
    rect_W = screenW - (camW + 20)
    rect_H = 25
    pygame.draw.rect(screen, colors['red'], (xDelta, yDelta, rect_W - sensor_reading, rect_H))
    
    font = pygame.font.Font(None, 20)
    text_color = colors['gray']
    sensor_text = font.render(str(sensor_reading), True, text_color)
    screen.blit(sensor_text, (xDelta + (rect_W-sensor_reading-20), yDelta + (rect_H // 2)))


def display_empty_bar(screen, vehicle, screenW, screenH, camW, camH, **kwargs):
    xDelta = camW + 10
    yDelta = screenH - camH + 10
    rect_W = screenW - (camW + 20)
    rect_H = 25
    pygame.draw.rect(screen, colors['gray'], (xDelta, yDelta, rect_W, rect_H))
    font = pygame.font.Font(None, 20)
    text_color = colors['white']
    min_val_text = font.render(str(kwargs.get('min_val')), True, text_color)
    max_val_text = font.render(str(kwargs.get('max_val')), True, text_color)
    screen.blit(max_val_text, (xDelta, yDelta + rect_H +5))
    screen.blit(min_val_text, (xDelta + rect_W - 10, yDelta + rect_H + 5))




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
            display_dashcam(screen, vehicle, screenW, screenH, camW, camH)
            display_ultrasonic_sensor_data(screen, vehicle, screenW, screenH, camW, camH)
            if vehicle.infrared_sensors.found_line:
                screen.blit(*create_text("PRESS SPACEBAR TO BEGIN AUTO LINE TRACK", offset=(200, 100)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pickle_servo_angles(vehicle.servo_angles)
                    pygame.quit()
                    session = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [ord(x) for x in 'wasd']:
                        vehicle._update_wheels(event)
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        vehicle._update_servo(event)
                    if event.key == ord('r'):
                        vehicle.reset_servo()
                    if event.key == pygame.K_SPACE:
                        vehicle.begin_autonomous_line_tracking()
                        vehicle.halt()
                    if event.key == ord('m'):
                        vehicle.begin_roomba_mode(screen)
                        print('exiting roomba mode')
                    if event.key == pygame.K_COMMA:
                        vehicle._look_left(screen)
                    if event.key == pygame.K_PERIOD:
                        vehicle._look_right(screen)
                elif event.type == pygame.KEYUP:
                    if event.key in vehicle.key_states:
                        del vehicle.key_states[event.key]
            if not vehicle.key_states:
                vehicle.halt()


    except KeyboardInterrupt:
        pickle_servo_angles(vehicle.servo_angles)



