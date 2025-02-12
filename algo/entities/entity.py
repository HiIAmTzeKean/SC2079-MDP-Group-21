from typing import List
from algo.tools.consts import EXPANDED_CELL, SCREENSHOT_COST, TOO_CLOSE_COST, PADDING, HEIGHT, WIDTH
from algo.tools.movement import Direction


class CellState:
    """Base class for all objects on the arena, such as cells, obstacles, etc"""

    def __init__(self, x, y, direction: Direction = Direction.NORTH, screenshot_id=None, penalty=0):
        self.x = x
        self.y = y
        self.direction = direction
        # If screenshot_id != None, the snapshot is taken at that position is for obstacle with obstacle_id = screenshot_id
        self.screenshot_id = screenshot_id if screenshot_id else None
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
        offset = PADDING * EXPANDED_CELL

        # If the obstacle is facing north, then robot's cell state must be facing south
        if self.direction == Direction.NORTH:
            positions = [
                # robot camera is directly in front of obstacle
                (self.x, self.y + offset),
                # robot camera is left of obstacle
                (self.x - 1, self.y + 2 + offset),
                # robot camera is right of obstacle
                (self.x + 1, self.y + 2 + offset),
                (self.x, self.y + 2 + offset),
            ]
            costs = [
                TOO_CLOSE_COST,         # robot camera is directly in front of obstacle
                SCREENSHOT_COST,        # robot camera is left of obstacle
                SCREENSHOT_COST,        # robot camera is right of obstacle
                0,                      # robot camera is positioned just nice
            ]

            for idx, pos in enumerate(positions):
                if self.is_valid_position(*pos):
                    cells.append(
                        CellState(*pos, Direction.SOUTH,
                                  self.obstacle_id, costs[idx])
                    )

        # If obstacle is facing south, then robot's cell state must be facing north
        elif self.direction == Direction.SOUTH:
            positions = [
                (self.x, self.y - offset),
                (self.x + 1, self.y - 2 - offset),
                (self.x - 1, self.y - 2 - offset),
                (self.x, self.y - 1 - offset),
            ]
            costs = [
                TOO_CLOSE_COST,
                SCREENSHOT_COST,
                SCREENSHOT_COST,
                0,
            ]

            for idx, pos in enumerate(positions):
                if self.is_valid_position(*pos):
                    cells.append(
                        CellState(*pos, Direction.NORTH,
                                  self.obstacle_id, costs[idx])
                    )

        # If obstacle is facing east, then robot's cell state must be facing west
        elif self.direction == Direction.EAST:
            positions = [
                (self.x + offset, self.y),
                (self.x + 2 + offset, self.y + 1),
                (self.x + 2 + offset, self.y - 1),
                (self.x + 2 + offset, self.y),
            ]
            costs = [
                TOO_CLOSE_COST,
                SCREENSHOT_COST,
                SCREENSHOT_COST,
                0,
            ]

            for idx, pos in enumerate(positions):
                if self.is_valid_position(*pos):
                    cells.append(
                        CellState(*pos, Direction.WEST,
                                  self.obstacle_id, costs[idx])
                    )

        # If obstacle is facing west, then robot's cell state must be facing east
        elif self.direction == Direction.WEST:
            positions = [
                (self.x - offset, self.y),
                (self.x - 2 - offset, self.y + 1),
                (self.x - 2 - offset, self.y - 1),
                (self.x - 2 - offset, self.y),
            ]
            costs = [
                TOO_CLOSE_COST,
                SCREENSHOT_COST,
                SCREENSHOT_COST,
                0,
            ]

            for idx, pos in enumerate(positions):
                if self.is_valid_position(*pos):
                    cells.append(
                        CellState(*pos, Direction.EAST,
                                  self.obstacle_id, costs[idx])
                    )
        return cells

    def get_obstacle_id(self):
        return self.obstacle_id

    def is_valid_position(self, center_x: int, center_y: int):
        """Checks if given position is within bounds

        Inputs
        ------
        center_x (int): x-coordinate
        center_y (int): y-coordinate

        Returns
        -------
        bool: True if valid, False otherwise
        """
        return 0 < center_x < WIDTH - 1 and 0 < center_y < HEIGHT - 1


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
        turn_padding = EXPANDED_CELL * PADDING
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
        """
        Checks if the robot can make 2 half-turns from x, y to new_x, new_y
        Logic:
            find the longer axis for the movement, and add padding to the shorter axis.
            Check if the obstacle is within the padded area
        """
        # create a path with padding from x, y to new_x, new_y and check if it is reachable
        if not self.is_valid_coord(x, y) or not self.is_valid_coord(new_x, new_y):
            return False
        padding = PADDING * EXPANDED_CELL

        # ensure that new_x > x so we can compare to obstacle coordinates later
        if new_x < x:
            new_x, x = x, new_x
        if new_y < y:
            new_y, y = y, new_y

        for obs in self.obstacles:
            if abs(x-new_x) > abs(y-new_y):
                # x is the longer axis
                # Use padding for the shorter y-axis to account for small vertical deviations when robot is moving mostly horizontally
                if x <= obs.x <= new_x and y - padding <= obs.y <= new_y + padding:
                    return False
            else:
                # y is the longer axis
                # Use padding for the shorter x-axis to account for small horizontal deviations when robot is moving mostly vertically
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

    def find_obstacle_by_id(self, obstacle_id: int) -> Obstacle:
        """
        Return obstacle object by its id
        """
        for obstacle in self.obstacles:
            if obstacle.obstacle_id == obstacle_id:
                return obstacle
        return None
