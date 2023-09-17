import pygame
from numpy import array
import pygame
import sys
import numpy as np
import matplotlib.pyplot as plt
from search import AStar, Gridworld, Cell
plt.ion()








class Constant:
    GRID_WIDTH, GRID_HEIGHT = 650, 650
    WIDTH, HEIGHT = 1000, 750
    DASHCAM_WIDTH = DASHCAM_HEIGHT = (WIDTH - GRID_WIDTH)
    GRID_SIZE = 25
    CELL_SIZE = GRID_WIDTH // GRID_SIZE
    LINEWIDTH = 1
    CAMERA_RESOLUTION = (640, 480)
    CAMERA_FPS = 30


def draw_mapping_grid():
    for x in range(0, Constant.GRID_WIDTH, Constant.CELL_SIZE):
        pygame.draw.line(screen, (255, 255, 255), (x, 0), (x, Constant.GRID_HEIGHT), Constant.LINEWIDTH)
    for y in range(0, Constant.GRID_HEIGHT, Constant.CELL_SIZE):
        pygame.draw.line(screen, (255, 255, 255), (0, y), (Constant.GRID_WIDTH, y), Constant.LINEWIDTH)


class GridImage:
    def __init__(self):
        self.grid_size = Constant.GRID_SIZE
        self.grid_values = self._init_empty_grid()
        self.covered_cells = set()

    def _init_empty_grid(self):
        return np.zeros((Constant.GRID_SIZE, Constant.GRID_SIZE))

    def __call__(self, new_covered_cells):
        tmp_grid_values = self._init_empty_grid()
        for covered_cell in new_covered_cells:
            tmp_grid_values[covered_cell] = 1
        self.grid_values = self.grid_values + tmp_grid_values
        self.covered_cells.add(new_covered_cells)

    def show(self):
        plt.imshow(self.grid_values[..., np.newaxis])


# Define a Button class
class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event) -> np.ndarray:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    return self.action()

# Define a function to be called when the button is clicked
def button_action():
    covered_cells_image = np.zeros((Constant.GRID_SIZE, Constant.GRID_SIZE))
    for covered_cell in covered_cells:
        covered_cells_image[covered_cell] = 4
    fig1, ax1 = plt.subplots()
    ax1.imshow(covered_cells_image[..., np.newaxis])
    return covered_cells_image


def update_covered_cells(rect):
    # Calculate the range of rows and columns covered by the rectangle
    start_col = rect.left // Constant.CELL_SIZE
    end_col = rect.right // Constant.CELL_SIZE
    start_row = rect.top // Constant.CELL_SIZE
    end_row = rect.bottom // Constant.CELL_SIZE

    # Add the cell indices to the covered_cells set
    for col in range(start_col, end_col + 1):
        for row in range(start_row, end_row + 1):
            if (0 <= row < Constant.GRID_SIZE) and (0 <= col < Constant.GRID_SIZE):
                covered_cells.add((row, col))




if __name__ == '__main__':
    pygame.init()
    # Create a button
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    button_width = 200
    button = Button("PLOT IMAGE", Constant.GRID_WIDTH - button_width - 10, 10, button_width, 20, action=button_action)
    covered_cells = set()
    grid_image = GridImage()

    screen = pygame.display.set_mode((Constant.GRID_WIDTH, Constant.GRID_HEIGHT))
    fps = pygame.time.Clock()
    rectangle_selection = 0
    rectangles_storage = []
    while True:
        draw_mapping_grid()
        for event in pygame.event.get():
            raw_grid = button.handle_event(event)
            if raw_grid is not None:
                world = Gridworld(raw_grid)
                astar = AStar(world=world)
                start = Cell()
                start.position = (0, 0)
                goal = Cell()
                N = raw_grid.shape[0] - 1
                goal.position = (N, N)
                print(f"path from {start.position} to {goal.position}")
                optimal_path_coords = astar.search(start, goal)
                print('PATH FOUND')
                best_path_img_arr = convert_to_image(optimal_path=optimal_path_coords, world=world)
                fig2, ax2 = plt.subplots()
                ax2.imshow(best_path_img_arr)


                # convert to string
                for row in range(0, world.w.shape[0]):
                    row_string = list(map(str, world.w[row, :].astype(int).tolist()))
                    row_string = ''.join(row_string)
                    # row_string = row_string.replace('0', '4')
                    print(row_string)


                #reset grid
                covered_cells = set()
                screen.fill((0, 0, 0))
                draw_mapping_grid()

            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    rectangle_selection, rectangle_width, rectangle_height = 1, 1, 1
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                    rectangle_left = int(pygame.mouse.get_pos()[0]) - int((rectangle_width))
                    rectangle_right = int(pygame.mouse.get_pos()[1]) - int((rectangle_height))
                    rectangle_main = pygame.Rect(rectangle_left, rectangle_right, int(rectangle_width), int(rectangle_height))
            elif event.type == pygame.MOUSEMOTION:
                if rectangle_selection:
                    if event.buttons[0]:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                        rectangle_main.w += event.rel[0]
                        rectangle_main.h += event.rel[1]
            elif event.type == pygame.MOUSEBUTTONUP:
                rectangle_selection, rectangle_width, rectangle_height = 1, 1, 1
                pygame.draw.rect(screen, (0, 255, 255), rectangle_main, 2, 3)
                array(rectangles_storage.append(rectangle_main))
                pygame.display.flip()
                update_covered_cells(rectangle_main)
        button.draw()
        pygame.display.flip()
        fps.tick(60)