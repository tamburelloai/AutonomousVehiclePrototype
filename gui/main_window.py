import pygame
import math

pygame.init()


class MainWindow:
    def __init__(self):
        self.screen = pygame.display.set_mode((Constant.WIDTH, Constant.HEIGHT))
        self.draw_mapping_grid()
        self.car_icon = pygame.transform.scale(pygame.image.load('/home/pi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server/car_icon.png'), (30, 30))
        self.car_rect = self.car_icon.get_rect()
        self.prior_positions = []
        
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
        self.update_vehicle_position(vehicle_state)
        self.update_vehicle_path()
        if object_coords:
            self.update_obstacle_location(object_coords)
    
    def update_vehicle_path(self):
        for (x, y) in self.prior_positions:
            pygame.draw.rect(self.screen, Color.BLUE, (x, y, Constant.CELL_SIZE, Constant.CELL_SIZE))
    
    def update_vehicle_position(self, vehicle_state):
        x, y, yaw = vehicle_state
        print(f'updating vehicle position to {x, y}')
        car_icon = pygame.transform.rotate(self.car_icon, yaw)
        self.screen.fill((0, 0, 0))
        self.draw_mapping_grid()
        self.screen.blit(car_icon, (x-15, y-15))
        self.prior_positions.append((x,y))
        
    def update_obstacle_location(self, coordinates):
        x, y = coordinates
        print(f'updating obstacle position to {x, y}')
        pygame.draw.rect(self.screen, Color.RED, (x, y, Constant.CELL_SIZE, Constant.CELL_SIZE))
    
    def draw_servo_sweep_coords(self, coordinates_list) -> None:
        for coordinates in coordinates_list:
            self.update_obstacle_location(coordinates) 
           
class Constant:
    WIDTH, HEIGHT = 650, 650 
    GRID_SIZE = 100
    CELL_SIZE = WIDTH // GRID_SIZE
    LINEWIDTH = 1

class Color:
    WHITE = (255, 255, 255)
    OFFWHITE = (50, 50, 50)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
