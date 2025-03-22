from typing import Union
from algo.tools.consts import SCREENSHOT_COST, DISTANCE_COST, PADDING, TURN_PADDING, MID_TURN_PADDING, ARENA_HEIGHT, ARENA_WIDTH, OFFSET, MIN_CLEARANCE, OBSTACLE_SIZE
from algo.tools.movement import Direction
from math import sqrt


class CellState:
    """Base class for all objects on the arena, such as cells, obstacles, etc"""

    def __init__(self, x: int, y: int, direction: Direction = Direction.NORTH, screenshot_id: Union[int, None] = None, penalty: int = 0):
        self.x: int = x
        self.y: int = y
        self.direction: Direction = direction
        # If screenshot_id != None, the snapshot is taken at that position is for obstacle with obstacle_id = screenshot_id
        self.screenshot_id: Union[int, None] = screenshot_id
        self.penalty: int = penalty  # Penalty for the view point of taking picture

    def is_eq(self, x: int, y: int, direction: Direction) -> bool:
        """
        Compare given x, y, direction with this cell state's position and direction
        """
        return self.x == x and self.y == y and self.direction == direction

    def __repr__(self) -> str:
        """String representation of cell state"""
        return "Cellstate(x: {}, y: {}, direction: {}, screenshot: {})".format(self.x, self.y, Direction(self.direction), self.screenshot_id)

    def set_screenshot(self, screenshot_id: int) -> None:
        self.screenshot_id = screenshot_id

    def get_dict(self) -> dict[str, Union[int, None]]:
        """
        Returns a dictionary representation of the cell
        """
        return {'x': self.x, 'y': self.y, 'd': self.direction, 's': self.screenshot_id}


class Obstacle(CellState):
    """Obstacle class, inherited from CellState"""

    def __init__(self, x: int, y: int, direction: Direction, obstacle_id: int) -> None:
        super().__init__(x, y, direction)
        self.obstacle_id: int = obstacle_id

    def __eq__(self, other: object) -> bool:
        """
        Checks if this obstacle is the same as input obstacle in terms of x, y, and direction
        """
        return self.x == other.x and self.y == other.y and self.direction == other.direction

    def get_view_state(self) -> list[CellState]:
        """
        Constructs the list of CellStates from which the robot can view the image on the obstacle properly.
        Currently checks a T shape of grids in front of the image
        TODO: Tune the possible view states based on testing. More view states means a longer algo runtime

        Returns:
            list[CellState]: Valid cell states where robot can be positioned to view the symbol on the obstacle
        """
        cells = []

        # If the obstacle is facing north, then robot's cell state must be facing south
        if self.direction == Direction.NORTH:
            positions = [
                # robot camera is left of obstacle
                (self.x - 1, self.y + MIN_CLEARANCE + OBSTACLE_SIZE + OFFSET),
                # robot camera is right of obstacle
                (self.x + 1, self.y + MIN_CLEARANCE + OBSTACLE_SIZE + OFFSET),
                # robot camera is positioned just nice from obstacle
                (self.x, self.y + MIN_CLEARANCE + 1 + OBSTACLE_SIZE + OFFSET),
                # robot camera is close to obstacle
                (self.x, self.y + MIN_CLEARANCE + OBSTACLE_SIZE + OFFSET),
            ]
            costs = [
                SCREENSHOT_COST + DISTANCE_COST,        # robot camera is left of obstacle
                SCREENSHOT_COST + DISTANCE_COST,        # robot camera is right of obstacle
                0,                                      # robot camera is positioned just nice
                DISTANCE_COST,                          # robot camera is close to obstacle
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
                (self.x + 1, self.y - MIN_CLEARANCE - OBSTACLE_SIZE - OFFSET),
                (self.x - 1, self.y - MIN_CLEARANCE - OBSTACLE_SIZE - OFFSET),
                (self.x, self.y - MIN_CLEARANCE - 1 - OBSTACLE_SIZE - OFFSET),
                (self.x, self.y - MIN_CLEARANCE - OBSTACLE_SIZE - OFFSET),
            ]
            costs = [
                SCREENSHOT_COST + DISTANCE_COST,
                SCREENSHOT_COST + DISTANCE_COST,
                0,
                DISTANCE_COST,
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
                (self.x + MIN_CLEARANCE + OBSTACLE_SIZE + OFFSET, self.y + 1),
                (self.x + MIN_CLEARANCE + OBSTACLE_SIZE + OFFSET, self.y - 1),
                (self.x + MIN_CLEARANCE + 1 + OBSTACLE_SIZE + OFFSET, self.y),
                (self.x + MIN_CLEARANCE + OBSTACLE_SIZE + OFFSET, self.y),
            ]
            costs = [
                SCREENSHOT_COST + DISTANCE_COST,
                SCREENSHOT_COST + DISTANCE_COST,
                0,
                DISTANCE_COST,
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
                (self.x - MIN_CLEARANCE - OBSTACLE_SIZE - OFFSET, self.y + 1),
                (self.x - MIN_CLEARANCE - OBSTACLE_SIZE - OFFSET, self.y - 1),
                (self.x - MIN_CLEARANCE - 1 - OBSTACLE_SIZE - OFFSET, self.y),
                (self.x - MIN_CLEARANCE - OBSTACLE_SIZE - OFFSET, self.y),
            ]
            costs = [
                SCREENSHOT_COST + DISTANCE_COST,
                SCREENSHOT_COST + DISTANCE_COST,
                0,
                DISTANCE_COST,
            ]

            for idx, pos in enumerate(positions):
                if self.is_valid_position(*pos):
                    cells.append(
                        CellState(*pos, Direction.EAST,
                                  self.obstacle_id, costs[idx])
                    )
        return cells

    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Checks if given position of robot is within bounds

        Args:
            x (int): x-coordinate of robot (wrt center)
            y (int): y-coordinate of robot (wrt center)
        """
        return 0 < x < ARENA_WIDTH - 1 and 0 < y < ARENA_HEIGHT - 1


class Grid:
    """
    Grid object that contains the size of the grid and a list of obstacles
    """

    def __init__(self, size_x: int, size_y: int) -> None:
        """
        Args:
            size_x (int): Size of the grid in the x direction
            size_y (int): Size of the grid in the y direction
        """
        self.size_x = size_x
        self.size_y = size_y
        self.obstacles: list[Obstacle] = []

    def add_obstacle(self, obstacle: Obstacle) -> None:
        """
        Add a new obstacle to the Grid object, ignores if duplicate obstacle. 
        Ensures that list of Obstacles is always sorted so that the same optimal path is returned for the same obstacles in different orders.

        NOTE: Sorting is just a band-aid fix to to ensure consistency. 
        There may be issues in the pathfinding algorithm or the A* heuristic may not be admissible which is causing different paths to be returned for same obstacles in different orders

        Args:
            obstacle (Obstacle): Obstacle to be added
        """
        if obstacle not in self.obstacles:
            self.obstacles.append(obstacle)
            self.obstacles.sort(key=lambda ob: (ob.x, ob.y))

    def reachable(self, x: int, y: int) -> bool:
        """Checks whether the given x,y coordinate is reachable/safe for the robot from a straight movement.
        Args:
            x (int): x coordinate
            y (int): y coordinate
        """
        if not self.is_valid_coord(x, y):
            return False

        for ob in self.obstacles:
            # ensure Manhattan distance from robot to obstacle is not within padding
            if abs(ob.x - x) + abs(ob.y - y) <= PADDING:
                return False
            # ensure Chebyshev distance from robot to obstacle is not within padding
            if max(abs(ob.x - x), abs(ob.y - y)) < PADDING:
                return False

        return True

    def turn_reachable(
        self, x: int, y: int, new_x: int, new_y: int, direction: Direction
    ) -> bool:
        """
        Checks if the robot can turn from x, y to new_x, new_y
        Logic:
            Checks 3 things for a turn: pre-turn, turn, post-turn
            1. pre-turn: if the obstacle is within the padding distance from the starting point
            2. post-turn: if the obstacle is within the padding distance from the end point
            3. turn:
                Finds 3 points near the curve followed by the robot during the turn
                For each point, checks if the obstacle is within the padding distance
        """

        points = self._get_turn_checking_points(x, y, new_x, new_y, direction)

        if not self.is_valid_coord(x, y) or not self.is_valid_coord(new_x, new_y):
            return False
        for obstacle in self.obstacles:
            # pre turn
            preturn_horizontal_distance = obstacle.x - x
            preturn_vertical_distance = obstacle.y - y
            preturn_dist = sqrt(
                preturn_horizontal_distance**2 + preturn_vertical_distance**2
            )
            if preturn_dist < TURN_PADDING:
                return False

            # post-turn
            turn_horizontal_distance = obstacle.x - new_x
            turn_vertical_distance = obstacle.y - new_y
            turn_dist = sqrt(
                turn_horizontal_distance**2 + turn_vertical_distance**2
            )
            if turn_dist < TURN_PADDING:
                return False

            # turn
            for point in points:
                horizontal_distance = obstacle.x - point[0]
                vertical_distance = obstacle.y - point[1]
                if sqrt(horizontal_distance**2 + vertical_distance**2) < MID_TURN_PADDING:
                    return False

        return True

    def is_valid_coord(self, x: int, y: int) -> bool:
        """
        Checks if given position is within bounds
        """
        return 0 < x < self.size_x - 1 and 0 < y < self.size_y - 1

    def get_view_obstacle_positions(self) -> list[list[CellState]]:
        """
        This function return a list of desired states for the robot to achieve based on the obstacle position and direction.
        The state is the position that the robot can see the image of the obstacle and is safe to reach without collision
        """

        optimal_positions = []
        for obstacle in self.obstacles:
            # skip obstacles with no direction
            if obstacle.direction == Direction.SKIP:
                continue
            else:
                view_states = [view_state for view_state in obstacle.get_view_state() if
                               self.reachable(view_state.x, view_state.y)]
            optimal_positions.append(view_states)
        return optimal_positions

    def find_obstacle_by_id(self, obstacle_id: int) -> Union[Obstacle, None]:
        """
        Return obstacle object by its id
        """
        for obstacle in self.obstacles:
            if obstacle.obstacle_id == obstacle_id:
                return obstacle
        return None

    @staticmethod
    def _get_turn_checking_points(
        x: int, y: int, new_x: int, new_y: int, direction: Direction
    ) -> list[tuple[int, int]]:
        """
        Finds 3 points near the curve followed by the robot during the turn. Near the curve since it is difficult to
        approximate points on the curve since it is not a part of a circle, but rather an irregular ellipse.

        Some intermediate points are used in the calculation. These are:
            1. mid_x, mid_y: the mid-point between the starting point and end point of the turn
            2. tr_x, tr_y: The point that completes the right-angled triangle with the starting point and end point of the turn.

        The 3 points are calculated as follows:
            1. p1x, p1y: A point between the starting point and (mid_x, mid_y)
            2. p2x, p2y: the mid-point between (tr_x, tr_y) and (mid_x, mid_y)
            3. p3x, p3y: A point between the ending point and (mid_x, mid_y)
        """
        mid_x, mid_y = (x + new_x) / 2, (y + new_y) / 2
        if direction == Direction.NORTH or direction == Direction.SOUTH:
            tr_x, tr_y = x, new_y
            p1x, p1y = (x + mid_x) / 2, mid_y
            p2x, p2y = (tr_x + mid_x) / 2, (tr_y + mid_y) / 2
            p3x, p3y = mid_x, (new_y + mid_y) / 2
            return [(p1x, p1y), (p2x, p2y), (p3x, p3y)]
        elif direction == Direction.EAST or direction == Direction.WEST:
            tr_x, tr_y = new_x, y
            p1x, p1y = mid_x, (y + mid_y) / 2
            p2x, p2y = (tr_x + mid_x) / 2, (tr_y + mid_y) / 2
            p3x, p3y = (new_x + mid_x) / 2, mid_y
            return [(p1x, p1y), (p2x, p2y), (p3x, p3y)]
        raise ValueError("Invalid direction")
