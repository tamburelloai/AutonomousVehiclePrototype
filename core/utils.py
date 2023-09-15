import pygame
import numpy as np


def create_text(text, offset):
    font = pygame.font.Font(None, 36)  # You can specify the font and size
    text = font.render(text, True, (255, 255, 255))  # Render the text
    text_rect = text.get_rect()  # Get the text's rectangle
    text_rect.center = offset  # Set the text's position (centered)
    return (text, text_rect)

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

class Constant:
    GRID_WIDTH, GRID_HEIGHT = 650, 650 
    WIDTH, HEIGHT = 1000, 750 
    DASHCAM_WIDTH = DASHCAM_HEIGHT = (WIDTH - GRID_HEIGHT)
    GRID_SIZE = 650 
    CELL_SIZE = GRID_WIDTH // GRID_SIZE
    LINEWIDTH = 1
    CAMERA_RESOLUTION = (640, 480)
    CAMERA_FPS = 30

class Color:
    WHITE = (255, 255, 255)
    OFFWHITE = (50, 50, 50)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    