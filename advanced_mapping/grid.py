import numpy as np

class Grid:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.grid_values = np.zeros((grid_size, grid_size), dtype=int)
    
    def update_grid_values(self, obstacle_coords):
        obstacle_coords = np.array(obstacle_coords)
        valid_coords_mask = self._get_coord_mask(obstacle_coords)
        obstacle_coords = obstacle_coords[valid_coords_mask]
        self.grid_values[obstacle_coords[:, 0], obstacle_coords[:, 1]] = 1
    
    def _get_coord_mask(self, obstacle_coords):
        return (
            (obstacle_coords[:, 0] >= 0) & \
            (obstacle_coords[:, 0] < self.grid_size) & \
            (obstacle_coords[:, 1] >= 0) & \
            (obstacle_coords[:, 1] < self.grid_size)
        )
    
    def reset_grid(self):
        self.grid_values = np.zeros((self.grid_size, self.grid_size), dtype=int)

    def __repr__(self):
        return self.grid_values.__repr__()
   