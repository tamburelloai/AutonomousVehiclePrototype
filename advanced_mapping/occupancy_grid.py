class OccupancyGrid(Grid):
    #Initializes occupancy grid
    def __init__(self, data, height, width, resolution, origin):
        Grid.__init__(self, data, height, width, resolution, origin)

        #Creates the sets for obstacles and empty cells (for faster obstacle expansion and frontier searching)
        self.obstacles = set()
        self.empty = set()

        self.costGrid = None

    #Gets neighbors of the specific cell
    def getNeighbors(self, cell, includeObstacles=False):
        neighborList = []

        (x, y) = cell

        for i in range(0, 3):
            for j in range(0, 3):
                neighborCell = (x - 1 + j, y - 1 + i)

                if includeObstacles:
                    if self.isWithinGrid(neighborCell) and cell != neighborCell:
                        neighborList.append(neighborCell)
                else:
                    if self.isWithinGrid(neighborCell) and cell != neighborCell and self.getCellValue(neighborCell) != CellType.Obstacle:
                        neighborList.append(neighborCell)

        return neighborList

    #Gets neighbors of the specific cell
    def getNeighborValues(self, cell):
        neighbors = self.getNeighbors(cell, True)
        neighborValues = []

        for neighbor in neighbors:
            neighborValue = self.getCellValue(neighbor)
            neighborValues.append(neighborValue)

        return neighborValues

    #Gets neighbors and their respective values as list of tuples
    def getNeighborValuePairs(self, cell):
        neighbors = self.getNeighbors(cell, True)
        neighborValuePairs = []

        for neighbor in neighbors:
            neighborValue = self.getCellValue(neighbor)
            neighborValuePair = (neighbor, neighborValue)

            neighborValuePairs.append(neighborValuePair)

        return neighborValuePairs

    #Scales map to a new resolution
    def scale(self, scaleFactor, cacheEmptyCells=True, cacheObstacleCells=True):
        self.obstacles.clear()
        self.empty.clear()

        if type(scaleFactor) != int:
            raise Exception("The scale factor should be an integer!")

        if scaleFactor < 1:
            raise Exception("New resolution should be larger than the old resolution!")

        ng_data = [] #ng stands for NewGrid
        ng_resolution = self.resolution * scaleFactor

        #Round up the new width and height
        ng_width = -(-self.width // scaleFactor)
        ng_height = -(-self.height // scaleFactor)

        ng_row = -1

        skip = False

        for i in range(0, self.height):
            temp_ng_row = i // scaleFactor

            #We do this check in order to make sure that we append only one row per n old cells, where n is the scaleFactor
            if ng_row != temp_ng_row:
                ng_row = temp_ng_row
                ng_data.append([])

            ng_column = -1

            for j in range(0, self.width):
                temp_ng_column = j // scaleFactor

                #We do this check in order to make sure that we append only one row per n old cells, where n is the scaleFactor
                if ng_column != temp_ng_column:
                    ng_column = temp_ng_column
                    ng_data[ng_row].append(-2) # -2 indicates that the new cell has no value assigned to it yet
                    skip = False

                if (ng_column, ng_row) in self.obstacles:
                    skip = True

                if skip:
                    continue

                currentCellValue = self.getCellValue((j, i))

                ng_oldCellValue = ng_data[ng_row][ng_column]

                if (currentCellValue == CellType.Obstacle):
                    ng_data[ng_row][ng_column] = CellType.Obstacle
                    if cacheObstacleCells:
                        self.obstacles.add((ng_column, ng_row))
                    if cacheEmptyCells and ng_oldCellValue == CellType.Empty:
                        self.empty.remove((ng_column, ng_row))

                elif (currentCellValue == CellType.Unexplored):
                    if ng_oldCellValue != CellType.Obstacle:
                        ng_data[ng_row][ng_column] = CellType.Unexplored
                        if cacheEmptyCells and ng_oldCellValue == CellType.Empty:
                            self.empty.remove((ng_column, ng_row))

                else: #empty cell
                    if ng_oldCellValue != CellType.Obstacle and ng_oldCellValue != CellType.Unexplored:
                        ng_data[ng_row][ng_column] = CellType.Empty
                        if cacheEmptyCells:
                            self.empty.add((ng_column, ng_row))

        self.data = ng_data
        self.height = ng_height
        self.width = ng_width
        self.resolution = ng_resolution

        (x, y) = self.origin
        self.cellOrigin = (x + ng_resolution/2, y + ng_resolution/2)

    #Expands the obstacles
    def expandObstacles(self):
        newObstacles = set()

        if not self.obstacles: #If the obstacle set is empty, then iterate through the entire map and find obstacles
            Grid.populateSetWithCells(self, self.obstacles, CellType.Obstacle)

        for obstacleCell in self.obstacles:
            neighborCells = self.getNeighbors(obstacleCell)

            for neighborCell in neighborCells:
                self.setCellValue(neighborCell, CellType.Obstacle)
                newObstacles.add(neighborCell)

        self.obstacles = self.obstacles.union(newObstacles)

        if self.empty: #If the empty cell cache is not empty, then remove empty cells that turned into obstacles after expansion
            self.empty = self.empty - self.obstacles

    #Adds cost grid to allow local cost map processing
    def addCostGrid(self, costGrid):
        self.costGrid = costGrid

        if (self.resolution != costGrid.resolution):
            raise Exception("Current implemenation does not support the addition of the cost grid that has different "
                            "resolution than the occupancy grid.")

        #Warning: The offset calculation
        self.costGridCellOffset = (int((costGrid.cellOrigin[0] - self.cellOrigin[0]) / self.resolution),
                                   int((costGrid.cellOrigin[1] - self.cellOrigin[1]) / self.resolution))

    #Gets heuristic relevant to the current grid
    def getHeuristic(self, currentCell, destinationCell):
        (currentX, currentY) = currentCell
        (destinationX, destinationY) = destinationCell

        return math.sqrt((currentX - destinationX) ** 2 +
                         (currentY - destinationY) ** 2)

    #Gets path cost relevant to the current grid
    def getPathCost(self, currentCell, destinationCell):
        cost = 0

        (currentX, currentY) = currentCell
        (destinationX, destinationY) = destinationCell

        xDiff = abs(currentX - destinationX)
        yDiff = abs(currentY - destinationY)

        if (xDiff > 1 or xDiff < 0) or (yDiff > 1 or yDiff < 0):
            raise Exception("getPathCost: The function estimates the cost only for adjacent cells!")

        if xDiff + yDiff == 2:
            cost += 1.4
        elif xDiff + yDiff == 1:
            cost += 1

        if self.costGrid != None:
            #find the corresponding cell in costGrid
            costGridCell = (currentCell[0] - self.costGridCellOffset[0], currentCell[1] - self.costGridCellOffset[1])

            #add the additional cost if the cell is in costmap
            if self.costGrid.isWithinGrid(costGridCell):
                cost += self.costGrid.getCellValue(costGridCell)

        return cost