import pygame
import math

pygame.init()


class MainWindow:
    def __init__(self):
        self.screen = pygame.display.set_mode((Constant.WIDTH, Constant.HEIGHT))
        self.draw_mapping_grid()
        
    def draw_mapping_grid(self):
        for x in range(0, Constant.WIDTH, Constant.CELL_SIZE):
            pygame.draw.line(self.screen, Color.OFFWHITE, (x, 0), (x, Constant.HEIGHT), Constant.LINEWIDTH)
        for y in range(0, Constant.HEIGHT, Constant.CELL_SIZE):
            pygame.draw.line(self.screen, Color.OFFWHITE, (0, y), (Constant.WIDTH, y), Constant.LINEWIDTH)
            
    def get_screen_center(self):
        return (Constant.WIDTH // 2, Constant.HEIGHT // 2)
    
    def fill_grid_cell(self, x, y):
        cell_x = x * Constant.CELL_SIZE
        cell_y = y * Constant.CELL_SIZE
    
    def update_vehicle_obstacle_readings(self, vehicle_state, object_coords):
        coordinates = vehicle_state[:-1]
        self.update_vehicle_position(coordinates)
        self.update_arrow_position(coordinates)
        if object_coords:
            self.update_obstacle_location(object_coords)
    
    
    def update_vehicle_position(self, coordinates):
        x, y = coordinates
        print(f'updating vehicle position to {x, y}')
        pygame.draw.rect(self.screen, Color.GREEN, (x, y, Constant.CELL_SIZE, Constant.CELL_SIZE))
        
    def update_arrow_position(self, coordinates):
        x, y = coordinates
        stalk_length = 100
        pygame.draw.rect(self.screen, Color.BLUE, (x, y, 1, stalk_length))
      
    def update_obstacle_location(self, coordinates):
        x, y = coordinates
        print(f'updating obstacle position to {x, y}')
        pygame.draw.rect(self.screen, Color.RED, (x, y, Constant.CELL_SIZE, Constant.CELL_SIZE))
           
class Constant:
    WIDTH, HEIGHT = 650, 650 
    GRID_SIZE = 100
    CELL_SIZE = WIDTH // GRID_SIZE
    LINEWIDTH = 1

class Color:
    WHITE = (255, 255, 255)
    OFFWHITE = (150, 150, 150)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
