
import pygame
import os
import sys
from picamera2 import Picamera2
from picamera.array import PiRGBArray
import time
from core.vehicle import Vehicle
from gui.main_window import MainWindow
import numpy as np
import pickle
from core.utils import Constant, Color
import threading


def get_image_surface(arr: np.ndarray):
    return pygame.surfarray.make_surface(arr)

def pickle_servo_angles(servo_angles):
    with open("servo_angles.pickle", "wb") as f:
        pickle.dump(servo_angles, f)
        

if __name__ == "__main__":
    try:
        screenW, screenH = 950, 700
        camW, camH = 640, 480
        window = MainWindow()
        vehicle = Vehicle(initial_coordinates=(window.get_grid_center()))
        window.initialize_vehicle_in_map(vehicle_state=vehicle.odometer.get_vehicle_state())

        session = True
        while session:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pickle_servo_angles(vehicle.servo_angles)
                    pygame.quit()
                    session = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [ord(x) for x in 'wasd']:
                        vehicle_state, obstacle_coords = vehicle.move(event, cm=23)
                        window.update_vehicle_obstacle_readings(vehicle_state, obstacle_coords)
                    if event.key == pygame.K_SPACE:
                        object_coords = vehicle.gather_servo_sweep_coords()
                        window.draw_servo_sweep_coords(object_coords)
                        vehicle.realtime_servo_sweep(window)
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
                    if event.key == ord('u'):
                        vehicle.realtime_ultrasonic_sweep(window)
                    if event.key == ord('t'):
                        if window.mode['object_detection']:
                            window.mode['object_detection'] = False
                        else:
                            window.mode['object_detection'] = True
                        pygame.display.flip()
                    if event.key == ord('m'):
                        if window.mode['mapping']:
                            window.mode['mapping'] = False
                        else:
                            window.mode['mapping'] = True
                        
                        pygame.display.flip()
                else:
                    vehicle.halt()
            window.update_dashcam(dashcam_view=vehicle.get_vision())
            window.draw_text_options()
            window.debug_print()
            pygame.display.flip()

    except KeyboardInterrupt:
        pickle_servo_angles(vehicle.servo_angles)



