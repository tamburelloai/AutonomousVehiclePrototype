import pygame
import math
from core.utils import Constant, Color
from advanced_mapping.grid import Grid
import cv2
from collections import defaultdict


pygame.init()


class MainWindow:
    def __init__(self):
        self.screen = pygame.display.set_mode((Constant.WIDTH, Constant.HEIGHT))
        self.prior_positions = []
        self.all_found_obstacle_coordinates = []
        self._load_icons()
        self._set_modes()
        self.font = pygame.font.Font(None, 36)
        self.obstacle_cache = defaultdict(int)
        self.dashcam_display_offset = (Constant.GRID_WIDTH+1, 0)
        self.optimal_path_array = None
    
    def _set_modes(self) -> None:
        self.mode = {}
        self.mode['object_detection'] = {'status': False}
        self.mode['mapping'] = {'status': False}
        self.mode['search'] = {'status': False}
        self.mode['control_mode'] = {'status': 'manual'}
        
    def _load_icons(self) -> None:
        self.car_icon = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/car_icon.png'), (30, 30))
        self.car_rect = self.car_icon.get_rect()
        self.object_detection_icon_on = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/object_detection_on.png'), (250, 30))
        self.object_detection_icon_off = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/object_detection_off.png'), (250, 30))
        self.mapping_icon_on = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/mapping_on.png'), (250, 30))
        self.mapping_icon_off = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/mapping_off.png'), (250, 30))
        self.astar_icon = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/astar.png'), (250, 30))
        self.r2o_icon = pygame.transform.scale(pygame.image.load('/home/pi/Freenove/Code/Server/assets/return_to_origin.png'), (250, 30))
     
    def update_dashcam(self, dashcam_view):
        resized_image = cv2.resize(dashcam_view, (Constant.DASHCAM_WIDTH-1, Constant.DASHCAM_HEIGHT))
        image_surface = pygame.surfarray.make_surface(resized_image)
        self.screen.blit(image_surface, self.dashcam_display_offset)
    
    def draw_gui_boundaries(self):
        pygame.draw.line(self.screen, Color.OFFWHITE, (0, Constant.GRID_HEIGHT), (Constant.WIDTH, Constant.GRID_HEIGHT), Constant.LINEWIDTH)
        
    def draw_mapping_grid(self):
        for x in range(0, Constant.GRID_WIDTH, Constant.CELL_SIZE):
            pygame.draw.line(self.screen, Color.OFFWHITE, (x, 0), (x, Constant.GRID_HEIGHT), Constant.LINEWIDTH)
        for y in range(0, Constant.GRID_HEIGHT, Constant.CELL_SIZE):
            pygame.draw.line(self.screen, Color.OFFWHITE, (0, y), (Constant.GRID_WIDTH, y), Constant.LINEWIDTH)
    
    def draw_options(self):
        base_x_offset = 60
        base_y_offset = Constant.GRID_HEIGHT + 10
        additional_x_offset = 300
        additional_y_offset = 40
        if self.mode['object_detection']['status']:
            self.screen.blit(self.object_detection_icon_on, (base_x_offset, base_y_offset))
        else:
            self.screen.blit(self.object_detection_icon_off, (base_x_offset, base_y_offset))
        
        if self.mode['mapping']['status']:
            self.screen.blit(self.mapping_icon_on, (base_x_offset + additional_x_offset, base_y_offset))
        else:
            self.screen.blit(self.mapping_icon_off,(base_x_offset + additional_x_offset, base_y_offset))
            
        self.screen.blit(self.astar_icon, (base_x_offset, base_y_offset + additional_y_offset))
        self.screen.blit(self.r2o_icon, (base_x_offset + additional_x_offset, base_y_offset + additional_y_offset))
    
    def draw_vehicle_state(self, vehicle_state):
        x, y, yaw = vehicle_state
        x_offset = Constant.GRID_WIDTH + 10
        y_offset = 50
        coord_location = (x_offset, y_offset)
        yaw_location = (x_offset, y_offset + 50)
        vehicle_info = f'GRID LOCATION: ({x}, {y}) [{yaw}]'
        self.screen.blit(self.font.render(vehicle_info, True, Color.WHITE), (Constant.GRID_WIDTH + 5, Constant.DASHCAM_HEIGHT + 5)) 
    
    def draw_autonomous_manual(self):
        control_mode = self.mode['control_mode']['status']
        color = Color.DARKBLUE if control_mode == 'manual' else Color.LIGHTBLUE
        self.screen.blit(self.font.render("CONTROL MODE: ", True, Color.WHITE), (Constant.GRID_WIDTH + 5, Constant.DASHCAM_HEIGHT + 30)) 
        self.screen.blit(self.font.render(control_mode.upper(), True, color), (Constant.GRID_WIDTH + 220, Constant.DASHCAM_HEIGHT + 30)) 
    
    def draw_best_path(self, optimal_path):
        #TODO
        pass
    
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
        car_icon = pygame.transform.rotate(self.car_icon, yaw)
        if yaw == 0:
            self.screen.blit(car_icon, (x-15, y))
        elif yaw % 45 == 0:
            self.screen.blit(car_icon, (x-15, y-15))
        elif yaw % 30 == 0:
            self.screen.blit(car_icon, (x-20, y-20))
                
            
        self.prior_positions.append((x,y))
        self.draw_vehicle_state(vehicle_state)
        
    def update_obstacle_location(self, coordinates):
        if not coordinates:
            return
        x, y = coordinates
        obstacle = pygame.draw.rect(self.screen, Color.RED, (x, y, Constant.CELL_SIZE, Constant.CELL_SIZE))
        self.all_found_obstacle_coordinates.append(coordinates)  # Store the rect in the list

    def _redraw_all_found_obstacles(self):
        for (x, y) in self.all_found_obstacle_coordinates:
            pygame.draw.rect(self.screen, Color.RED, (x, y, Constant.CELL_SIZE, Constant.CELL_SIZE))

    def draw_servo_sweep_coords(self, coordinates_list) -> None:
        for coordinates in coordinates_list:
            self.update_obstacle_location(coordinates) 
            
    def draw_ultrasonic_beam(self, coords):
        '''Start and ending coordinates for ultrasonic reading'''
        coords_start, coords_end = coords
        pygame.draw.line(self.screen, Color.GREEN, coords_start, coords_end, Constant.LINEWIDTH)
        pygame.display.flip()
    
    def _draw_bounding_box(self, pred):
        x0, y0, xN, yN = pred[:-1]
        class_name = pred[-1]
                
        original_height = 640
        original_width = 480
        new_width = 350
        new_height = 350

        # Calculate scaling factors
        x_scale = new_width / original_width
        y_scale = new_height / original_height

        # Scale the coordinates to fit the new image size (350x350)
        x0_350 = int(x0 * x_scale)
        y0_350 = int(y0 * y_scale)
        xN_350 = int(xN * x_scale)
        yN_350 = int(yN * y_scale)

        # Calculate width and height on the new image
        width_350 = xN_350 - x0_350
        height_350 = yN_350 - y0_350
        
        # Draw the rectangle on the new image (350x350)
        pygame.draw.rect(self.screen, (0, 255, 0), (x0_350+Constant.GRID_WIDTH, 
                                                    y0_350+ (Constant.HEIGHT - Constant.DASHCAM_HEIGHT - 98), 
                                                    width_350, height_350), 2)  # 2 is the width of the outline
        text_surface = self.font.render(class_name, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x0_350,y0_350)  # You can adjust the text position here
        self.screen.blit(text_surface, text_rect)
           
    def draw_bounding_boxes(self, preds):
        for pred in preds:
            self._draw_bounding_box(pred)

    def debug_print(self):
        print(self.prior_positions)
    
    def flip(self, vehicle_state, obstacle_coords, dashcam_view, objects_detected):
        self.screen.fill((0, 0, 0))
        self.draw_mapping_grid()
        self.draw_gui_boundaries()
        if self.mode['mapping']['status'] == True:
            self.update_vehicle_obstacle_readings(vehicle_state, obstacle_coords)
        self.update_dashcam(dashcam_view)
        if self.mode['object_detection']['status'] == True:
            self.draw_bounding_boxes(objects_detected)
        self.draw_options()
        self.draw_autonomous_manual()
        #self.debug_print()
        pygame.display.flip()





