import pygame
import math
from core.utils import Constant, Color
from advanced_mapping.grid import Grid
import cv2


pygame.init()


class MainWindow:
    def __init__(self):
        self.screen = pygame.display.set_mode((Constant.WIDTH, Constant.HEIGHT))
        #self.draw_mapping_grid()
        self.prior_positions = []
        self._all_found_obstacles = []
        self._load_icons()
        self._set_modes()
        self.font = pygame.font.Font(None, 36)
    
    def _set_modes(self) -> None:
        self.mode = {}
        self.mode['object_detection'] = {'status': False}
        self.mode['mapping'] = {'status': False}
        
    def _load_icons(self) -> None:
        self.car_icon = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/car_icon.png'), (30, 30))
        self.car_rect = self.car_icon.get_rect()
        self.object_detection_icon_on = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/object_detection_on.png'), (250, 30))
        self.object_detection_icon_off = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/object_detection_off.png'), (250, 30))
        self.mapping_icon_on = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/mapping_on.png'), (250, 30))
        self.mapping_icon_off = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/mapping_off.png'), (250, 30))
     
    def update_dashcam(self, dashcam_view):
        resized_image = cv2.resize(dashcam_view, (Constant.DASHCAM_WIDTH-1, Constant.DASHCAM_HEIGHT))
        image_surface = pygame.surfarray.make_surface(resized_image)
        self.screen.blit(image_surface, (Constant.GRID_WIDTH+1, (Constant.HEIGHT - Constant.DASHCAM_HEIGHT - 98)))
        
    def draw_mapping_grid(self):
        for x in range(0, Constant.GRID_WIDTH, Constant.CELL_SIZE):
            pygame.draw.line(self.screen, Color.OFFWHITE, (x, 0), (x, Constant.GRID_HEIGHT), Constant.LINEWIDTH)
        for y in range(0, Constant.GRID_HEIGHT, Constant.CELL_SIZE):
            pygame.draw.line(self.screen, Color.OFFWHITE, (0, y), (Constant.GRID_WIDTH, y), Constant.LINEWIDTH)
    
    def draw_text_options(self):
        if self.mode['object_detection']:
            self.screen.blit(self.object_detection_icon_on, (10, Constant.GRID_HEIGHT + 10))
        else:
            self.screen.blit(self.object_detection_icon_off, (10, Constant.GRID_HEIGHT + 10))
        if self.mode['mapping']:
            self.screen.blit(self.mapping_icon_on, (310, Constant.GRID_HEIGHT + 10))
        else:
            self.screen.blit(self.mapping_icon_off, (310, Constant.GRID_HEIGHT + 10))
    
    def draw_vehicle_state(self, vehicle_state):
        x, y, yaw = vehicle_state
        x_offset = Constant.GRID_WIDTH + 10
        y_offset = 50
        coord_location = (x_offset, y_offset)
        yaw_location = (x_offset, y_offset + 50)
        vehicle_coord = f'GRID LOCATION: ({x}, {y})'
        vehicle_yaw   = f'          YAW: {yaw}'
        self.screen.blit(self.font.render(vehicle_coord, True, Color.WHITE), coord_location) 
        self.screen.blit(self.font.render(vehicle_yaw, True, Color.WHITE), yaw_location) 
    
    def draw_prior_positions(self):
        pygame.draw.lines(self.screen, Color.BLUE, False, self.prior_positions, 1)

    def get_grid_center(self):
        return (Constant.GRID_WIDTH // 2, Constant.GRID_HEIGHT // 2)
    
    def fill_grid_cell(self, x, y):
        cell_x = x * Constant.CELL_SIZE
        cell_y = y * Constant.CELL_SIZE
    
    def initialize_vehicle_in_map(self, vehicle_state):
        self.update_vehicle_position(vehicle_state)
        
    def update_vehicle_obstacle_readings(self, vehicle_state, obstacle_coords):
        self.update_vehicle_position(vehicle_state)
        self.update_vehicle_path()
        self._redraw_all_found_obstacles()
        for coordinates in obstacle_coords:
            self.update_obstacle_location(coordinates) 
    
    # def _path_loop_formed(self):
    #     '''check if loop is formed from prior positions containing a duplicate'''
    #     if len(self.prior_positions) != len(set(self.prior_positions)):
    #         repeated_coordinate = self.prior_positions.pop(-1)
    #         first_index = self.prior_positions.index(repeated_coordinate) #first appearance of now repeated coordinate
    #         loop = self.prior_positions[first_index:]
    #         loop.append(repeated_coordinate)
    #         return loop
    #     return None
    
    # def _object_free_area(self, loop):
    #     #assert no values for coordinates between within looped area
    #     pass
    
    # def _check_safe_zone_found(self):
    #     loop = self._path_loop_formed()
    #     if loop and self._object_free_area(loop):
    #         return loop
    #     return False
    
    def update_vehicle_path(self):
        #safe_zone_found = self._check_safe_zone_found()
        #if safe_zone_found:
        #    self._fill_safe_zone(safe_zone_found)
        #    self.prior_positions = []
        #else:
            #pygame.draw.lines(self.screen, Color.BLUE, False, self.prior_positions, 1)
        pygame.draw.lines(self.screen, Color.BLUE, False, self.prior_positions, 1)
            
    def update_vehicle_position(self, vehicle_state):
        x, y, yaw = vehicle_state
        print(f'updating vehicle position to {x, y}')
        car_icon = pygame.transform.rotate(self.car_icon, yaw)
        self.screen.fill((0, 0, 0))
        #self.draw_mapping_grid()
        self.screen.blit(car_icon, (x-15, y-15))
        self.prior_positions.append((x,y))
        self.draw_vehicle_state(vehicle_state)
        
    def update_obstacle_location(self, coordinates):
        x, y = coordinates
        print(f'updating obstacle position to {x, y}')
        obstacle = pygame.draw.rect(self.screen, Color.RED, (x, y, Constant.CELL_SIZE, Constant.CELL_SIZE))
        self._all_found_obstacles.append(obstacle)  # Store the rect in the list

    def _redraw_all_found_obstacles(self):
        for obstacle in self._all_found_obstacles:
            pygame.draw.rect(self.screen, Color.RED, obstacle)  # Redraw all stored obstacle rects
    
    def draw_servo_sweep_coords(self, coordinates_list) -> None:
        for coordinates in coordinates_list:
            self.update_obstacle_location(coordinates) 
            
    def draw_ultrasonic_beam(self, coords):
        '''Start and ending coordinates for ultrasonic reading'''
        coords_start, coords_end = coords
        pygame.draw.line(self.screen, Color.GREEN, coords_start, coords_end, Constant.LINEWIDTH)
        pygame.display.flip()
        
    def debug_print(self):
        print(self.prior_positions)
           

