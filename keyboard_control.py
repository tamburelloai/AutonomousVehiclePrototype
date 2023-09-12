import pygame
import os
import sys
from picamera2 import Picamera2
import time

cam = Picamera2()
cam.start()
time.sleep(1)



pygame.init()
screen_W, screen_H =  640, 480
screen = pygame.display.set_mode((screen_W, screen_H))

def keyboard_control(): 
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    PWM.setMotorModel(1000, 1000, 1000, 1000)
                if event.key == pygame.K_DOWN  or event.key == ord('s'):
                    PWM.setMotorModel(-1000, -1000, -1000, -1000)
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    PWM.setMotorModel(-1500, -1500, 2000, 2000)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    PWM.setMotorModel(2000, 2000, -1500, -1500)
            elif event.type == pygame.KEYUP:
                PWM.setMotorModel(0, 0, 0, 0)

        arr = cam.capture_array('main')[:, :, :3].transpose(1, 0, 2)
        image_surface = pygame.surfarray.make_surface(arr)
        screen.blit(image_surface, (0, 0))
        pygame.display.flip()



if __name__ == '__main__':
    from Motor import *            
    PWM=Motor()          
    print("initializing keyboard control...")
    keyboard_control()
