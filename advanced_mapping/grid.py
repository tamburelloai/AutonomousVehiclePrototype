import numpy as np


class Grid:
    def __init__(self):
        self.grid_values = np.zeros(size=(100, 100))

    def _expand_grid(self):
        pass

    def update_grid_values(self):
        pass

    def reset_grid(self):
        self.grid_values = np.zeros(size=(100, 100))


