from typing import List
from tools.consts import Direction, EXPANDED_CELL, SCREENSHOT_COST
from tools.helper import is_valid


class CellState:
    """Base class for all objects on the arena, such as cells, obstacles, etc"""

    def __init__(self, x, y, direction: Direction = Direction.NORTH, screenshot_id=-1, penalty=0):
        self.x = x
        self.y = y
        self.direction = direction
        # If screenshot_od != -1, the snapshot is taken at that position is for the obstacle with id = screenshot_id
        self.screenshot_id = screenshot_id
        self.penalty = penalty  # Penalty for the view point of taking picture

    def cmp_position(self, x, y) -> bool:
        """Compare given (x,y) position with cell state's position

        Args:
            x (int): x coordinate
            y (int): y coordinate

        Returns:
            bool: True if same, False otherwise
        """
        return self.x == x and self.y == y

    def is_eq(self, x, y, direction):
        """Compare given x, y, direction with cell state's position and direction

        Args:
            x (int): x coordinate
            y (int): y coordinate
            direction (Direction): direction of cell

        Returns:
            bool: True if same, False otherwise
        """
        return self.x == x and self.y == y and self.direction == direction

    def __repr__(self):
        return "Cellstate(x: {}, y: {}, direction: {}, screenshot: {})".format(self.x, self.y, self.direction.name, self.screenshot_id)

    def set_screenshot(self, screenshot_id):
        """Set screenshot id for cell

        Args:
            screenshot_id (int): screenshot id of cell
        """
        self.screenshot_id = screenshot_id

    def get_dict(self):
        """Returns a dictionary representation of the cell

        Returns:
            dict: {x,y,direction,screeshot_id}
        """
        return {'x': self.x, 'y': self.y, 'd': self.direction, 's': self.screenshot_id}


class Obstacle(CellState):
    """Obstacle class, inherited from CellState"""

    def __init__(self, x: int, y: int, direction: Direction, obstacle_id: int):
        super().__init__(x, y, direction)
        self.obstacle_id = obstacle_id

    def __eq__(self, other):
        """Checks if this obstacle is the same as input in terms of x, y, and direction

        Args:
            other (Obstacle): input obstacle to compare to

        Returns:
            bool: True if same, False otherwise
        """
        return self.x == other.x and self.y == other.y and self.direction == other.direction

    def get_view_state(self, retrying) -> List[CellState]:
        """
        Constructs the list of CellStates from which the robot can view the image on the obstacle properly.
        Currently checks a T shape of grids in front of the image
        "TODO: tune the grid values based on testing

        Returns:
            List[CellState]: Valid cell states where robot can be positioned to view the symbol on the obstacle
        """
        cells = []
        offset = 2 * EXPANDED_CELL
        # If the obstacle is facing north, then robot's cell state must be facing south
        if self.direction == Direction.NORTH:
            if not retrying:
                positions = [(self.x, self.y + offset), (self.x - 1, self.y + 1 + offset),
                             (self.x + 1, self.y + 1 + offset), (self.x, self.y + 1 + offset)]
                costs = [0, SCREENSHOT_COST, SCREENSHOT_COST, 5]
            else:
                positions = [(self.x, self.y + 1 + offset), (self.x - 1, self.y + 2 + offset),
                             (self.x + 2, self.y + 1 + offset), (self.x, self.y + 2 + offset)]
                costs = [0, SCREENSHOT_COST, SCREENSHOT_COST, 5]

            for idx, pos in enumerate(positions):
                if is_valid(*pos):
                    cells.append(CellState(*pos, Direction.SOUTH,
                                 self.obstacle_id, costs[idx]))

        # If obstacle is facing south, then robot's cell state must be facing north
        elif self.direction == Direction.SOUTH:

            if not retrying:
                positions = [(self.x, self.y - offset), (self.x + 1, self.y - 1 - offset),
                             (self.x - 1, self.y - 1 - offset), (self.x, self.y - 1 - offset)]
                costs = [0, SCREENSHOT_COST, SCREENSHOT_COST, 5]
            else:
                positions = [(self.x, self.y - 1 - offset), (self.x + 1, self.y - 2 - offset),
                             (self.x - 1, self.y - 2 - offset), (self.x, self.y - 2 - offset)]
                costs = [0, SCREENSHOT_COST, SCREENSHOT_COST, 5]
            for idx, pos in enumerate(positions):
                if is_valid(*pos):
                    cells.append(CellState(*pos, Direction.NORTH,
                                 self.obstacle_id, costs[idx]))

        # If obstacle is facing east, then robot's cell state must be facing west
        elif self.direction == Direction.EAST:
            if not retrying:
                positions = [(self.x + offset, self.y), (self.x + 1 + offset, self.y + 1),
                             (self.x + 1 + offset, self.y - 1), (self.x + 1 + offset, self.y)]
                costs = [0, SCREENSHOT_COST, SCREENSHOT_COST, 5]
            else:
                positions = [(self.x + 1 + offset, self.y), (self.x + 2 + offset, self.y + 1),
                             (self.x + 2 + offset, self.y - 1), (self.x + 2 + offset, self.y)]
                costs = [0, SCREENSHOT_COST, SCREENSHOT_COST, 5]

            for idx, pos in enumerate(positions):
                if is_valid(*pos):
                    cells.append(CellState(*pos, Direction.WEST,
                                 self.obstacle_id, costs[idx]))

        # If obstacle is facing west, then robot's cell state must be facing east
        elif self.direction == Direction.WEST:
            if not retrying:
                position = [(self.x - offset, self.y), (self.x - 1 - offset, self.y + 1),
                            (self.x - 1 - offset, self.y - 1), (self.x - 1 - offset, self.y)]
                costs = [0, SCREENSHOT_COST, SCREENSHOT_COST, 5]
            else:
                position = [(self.x - 1 - offset, self.y), (self.x - 2 - offset, self.y + 1),
                            (self.x - 2 - offset, self.y - 1), (self.x - 2 - offset, self.y)]
                costs = [0, SCREENSHOT_COST, SCREENSHOT_COST, 5]
            for idx, pos in enumerate(position):
                if is_valid(*pos):
                    cells.append(CellState(*pos, Direction.EAST,
                                 self.obstacle_id, costs[idx]))
        return cells

    def get_obstacle_id(self):
        return self.obstacle_id


class Grid:
    """
    Grid object that contains the size of the grid and a list of obstacles
    """

    def __init__(self, size_x: int, size_y: int):
        """
        Args:
            size_x (int): Size of the grid in the x direction
            size_y (int): Size of the grid in the y direction
        """
        self.size_x = size_x
        self.size_y = size_y
        self.obstacles: List[Obstacle] = []

    def add_obstacle(self, obstacle: Obstacle):
        """Add a new obstacle to the Grid object, ignores if duplicate obstacle

        Args:
            obstacle (Obstacle): Obstacle to be added
        """
        # Loop through the existing obstacles to check for duplicates
        to_add = True
        for ob in self.obstacles:
            if ob == obstacle:
                to_add = False
                break

        if to_add:
            self.obstacles.append(obstacle)

    def reset_obstacles(self):
        """
        Resets the obstacles in the grid
        """
        self.obstacles = []

    def get_obstacles(self):
        """
        Returns the list of obstacles in the grid
        """
        return self.obstacles

    def reachable(self, x: int, y: int, turn=False, preturn=False) -> bool:
        """Checks whether the given x,y coordinate is reachable/safe. Criterion is as such:
        - Must be at least 4 units away in total (x+y) from the obstacle
        - Greater distance (x or y distance) must be at least 3 units away from obstacle

        Args:
            x (int): x coordinate
            y (int): y coordinate
            turn (bool): Should be set to True when checking coordinates while turning
            preturn (bool): Should be set to True when checking coordinates before turning
        """
        turn_padding = EXPANDED_CELL + 2
        if not self.is_valid_coord(x, y):
            return False

        for ob in self.obstacles:
            if abs(ob.x - x) + abs(ob.y - y) <= 2:
                return False

            if turn:
                if max(abs(ob.x - x), abs(ob.y - y)) < turn_padding:
                    return False
            if preturn:
                if max(abs(ob.x - x), abs(ob.y - y)) < turn_padding + 1:
                    return False
            if not turn and not preturn:
                if max(abs(ob.x - x), abs(ob.y - y)) < 2:
                    return False

        return True

    def half_turn_reachable(self, x: int, y: int, new_x: int, new_y: int) -> bool:
        # create a path with padding from x, y to new_x, new_y and check if it is reachable
        if not self.is_valid_coord(x, y) or not self.is_valid_coord(new_x, new_y):
            return False
        padding = 2 * EXPANDED_CELL
        if new_x < x:
            new_x, x = x, new_x
        if new_y < y:
            new_y, y = y, new_y
        for obs in self.obstacles:

            if abs(x-new_x) > abs(y-new_y):
                # x is the longer axis. Use padding only for the y-axis
                if x <= obs.x <= new_x and y - padding <= obs.y <= new_y + padding:
                    return False
            else:
                # y is the longer axis. Use padding only for the x-axis
                if x - padding <= obs.x <= new_x + padding and y <= obs.y <= new_y:
                    return False
        return True

    def is_valid_coord(self, x: int, y: int) -> bool:
        """
        Checks if given position is within bounds
        """
        if x < 1 or x >= self.size_x - 1 or y < 1 or y >= self.size_y - 1:
            return False

        return True

    def is_valid_cell_state(self, state: CellState) -> bool:
        """
        Checks if given state is within bounds
        """
        return self.is_valid_coord(state.x, state.y)

    def get_view_obstacle_positions(self, retrying) -> List[List[CellState]]:
        """
        This function return a list of desired states for the robot to achieve based on the obstacle position and direction.
        The state is the position that the robot can see the image of the obstacle and is safe to reach without collision
        :return: [[CellState]]
        """

        optimal_positions = []
        for obstacle in self.obstacles:
            # skip objects that have SKIP as their direction
            if obstacle.direction == Direction.SKIP:
                continue
            else:
                view_states = [view_state for view_state in obstacle.get_view_state(retrying) if
                               self.reachable(view_state.x, view_state.y)]
            optimal_positions.append(view_states)
        return optimal_positions
