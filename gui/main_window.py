import pygame
from enum import Enum

class Constant(Enum):
    WIDTH, HEIGHT = 800, 800
    GRID_SIZE = 100
    CELL_SIZE = WIDTH // GRID_SIZE

class Color(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
     
class MainWindow:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((Constant.WIDTH, Constant.HEIGHT))
    
    def draw_mapping_grid(self):
        def build_grid():
            for x in range(0, Constant.WIDTH, Constant.CELL_SIZE):
                pygame.draw.line(self.screen, Constant.BLACK, (x, 0), (x, Constant.HEIGHT))
            for y in range(0, Constant.HEIGHT, Constant.CELL_SIZE):
                pygame.draw.line(self.screen, Constant.BLACK, (0, y), (Constant.WIDTH, y))

       
     