"""
The A* algorithm combines features of uniform-cost search and pure heuristic search to
efficiently compute optimal solutions.

The A* algorithm is a best-first search algorithm in which the cost associated with a
node is f(n) = g(n) + h(n), where g(n) is the cost of the path from the initial state to
node n and h(n) is the heuristic estimate or the cost or a path from node n to a goal.

The A* algorithm introduces a heuristic into a regular graph-searching algorithm,
essentially planning ahead at each step so a more optimal decision is made. For this
reason, A* is known as an algorithm with brains.

https://en.wikipedia.org/wiki/A*_search_algorithm
"""
import numpy as np


class Cell:
    """
    Class cell represents a cell in the world which have the properties:
    position: represented by tuple of x and y coordinates initially set to (0,0).
    parent: Contains the parent cell object visited before we arrived at this cell.
    g, h, f: Parameters used when calling our heuristic function.
    """

    def __init__(self):
        self.position = (0, 0)
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

    """
    Overrides equals method because otherwise cell assign will give
    wrong results.
    """

    def __eq__(self, cell):
        return self.position == cell.position

    def showcell(self):
        print(self.position)


class Gridworld:
    """
    Gridworld class represents the  external world here a grid M*M
    matrix.
    world_size: create a numpy array with the given world_size default is 5.
    """

    def __init__(self, world:np.ndarray = None):
        self.w = world
        self.world_x_limit = world.shape[0]
        self.world_y_limit = world.shape[1]

    def show(self):
        print(self.w)

    def _is_valid_coordinate(self, x, y):
        return all([0 <= x < self.world_x_limit,
                    0 <= y < self.world_y_limit
                    ])

    def _is_traversable(self, x, y):
        if self._is_valid_coordinate(x, y):
            #TODO implement such that considering the current yaw, get the coords to left and right of vehicle coord
            # TODO: and make sure that they are not 4 either ===> Finds wide enough space for the car to traverse
            return self.w[x, y] != Constant.OBSTACLE_INDICATOR
        else:
            return False

    def get_neigbors(self, cell):
        """
        Return the neighbours of cell
        """
        neughbour_cord = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        current_x = cell.position[0]
        current_y = cell.position[1]
        neighbours = []
        for n in neughbour_cord:
            x = current_x + n[0]
            y = current_y + n[1]
            if self._is_traversable(x, y):
                c = Cell()
                c.position = (x, y)
                c.parent = cell
                neighbours.append(c)
        return neighbours


class AStar:
    def __init__(self, grid:np.ndarray) -> None:
        self.world = None
        self.traversed_grid = None
        self.rgb_image = None


    def initialize_grid(self, grid:np.ndarray) -> None:
        self.world = Gridworld(grid)

    def _init_grid_cell(self, coordinates:tuple):
        cell = Cell()
        cell.position = coordinates
        return cell

    def _add_path_to_grid(self) -> None:
        for (x, y) in self.optimal_path:
            self.world.w[x, y] = Constant.PATH_INDICATOR

    def _get_traversed_grid(self) -> None:
        traversed_grid = self.world.w
        if len(traversed_grid.shape) == 3:
            traversed_grid = traversed_grid.squeeze()
        assert len(traversed_grid.shape) == 2
        self.traversed_grid = traversed_grid

    def _init_image(self) -> tuple:
        self._get_traversed_grid()
        M, N = self.traversed_grid.shape
        self.rgb_image = np.zeros((M, N, 3))
        return (M, N)

    def build_optimal_path_image(self) -> None:
        self._add_path_to_grid()
        M, N = self._init_image()
        for i in range(M):
            for j in range(N):
                if self.traversed_grid[i, j] == 0:
                    r, g, b = 0, 0, 0
                elif self.traversed_grid[i, j] == 1:
                    r, g, b = 0, 0, 254
                elif self.traversed_grid[i, j] == 4:
                    r, g, b = 254, 0, 0
                self.rgb_image[i, j, :] = (r, g, b)
        self.rgb_image = self.rgb_image.astype(int)

    def search(self, start:Cell, goal:Cell) -> None:
        """
        Implementation of a start algorithm.
        world : Object of the world object.
        start : Object of the cell as  start position.
        stop  : Object of the cell as goal position.
        """
        _open = []
        _closed = []
        _open.append(start)
        while _open:
            min_f = np.argmin([n.f for n in _open])
            current = _open[min_f]
            _closed.append(_open.pop(min_f))
            if current == goal:
                break
            for n in self.world.get_neigbors(current):
                for c in _closed:
                    if c == n:
                        continue
                n.g = current.g + 1
                x1, y1 = n.position
                x2, y2 = goal.position
                n.h = (y2 - y1) ** 2 + (x2 - x1) ** 2
                n.f = n.h + n.g
                for c in _open:
                    if c == n and c.f < n.f:
                        continue
                _open.append(n)
        path = []
        while current.parent is not None:
            path.append(current.position)
            current = current.parent
        path.append(current.position)
        self.optimal_path = path[::-1]
        print(f'Optimal path from {start.position} to {goal.position} calculated')

    def __call__(self, start_coord:tuple, target_coord:tuple):
        start_cell = self._init_grid_cell(start_coord)
        target_cell = self._init_grid_cell(target_coord)
        self.search(start_cell, target_cell)
        self.build_optimal_path_image()



if __name__ == "__main__":
    mock_grid = np.zeros((5, 5))
    mock_grid[1, 1] = 4
    print(mock_grid)
    world = Gridworld(mock_grid)
    astar = AStar(world=world)

    # Start position and goal
    start = Cell()
    start.position = (0, 0)
    goal = Cell()
    goal.position = (4, 4)

    print(f"path from {start.position} to {goal.position}")
    res = astar.search(start, goal)
    #   Just for visual reasons.
    for i in res:
        world.w[i] = 1
    print(world.w)
