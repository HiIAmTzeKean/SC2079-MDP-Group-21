from typing import Union
import heapq
import math
import numpy as np
from python_tsp.heuristics import solve_tsp_lin_kernighan
from algo.entities.entity import CellState, Obstacle, Grid
from algo.entities.robot import Robot
from algo.tools.consts import (
    TURN_FACTOR,
    ITERATIONS,
    SAFE_COST,
    TURN_DISPLACEMENT,
    REVERSE_FACTOR,
    PADDING,
    ARENA_WIDTH,
    ARENA_HEIGHT,
)
from algo.tools.movement import (
    Direction,
    MOVE_DIRECTION,
    Motion
)


class MazeSolver:
    """
    A class that is used to find the shortest path given a grid, robot and obstacles
    """

    def __init__(
            self,
            size_x: int = ARENA_WIDTH,
            size_y: int = ARENA_HEIGHT,
            robot: Union[Robot, None] = None,
            robot_x: int = 1,
            robot_y: int = 1,
            robot_direction: Direction = Direction.NORTH,
    ) -> None:
        self.neighbor_cache = {}  # Store precomputed neighbors
        """
        Args:
            size_x: size of the grid in x direction. Default is 20
            size_y: size of the grid in y direction. Default is 20
            robot: A robot object that contains the robot's path
            robot_x: x coordinate of the robot. Default is 1
            robot_y: y coordinate of the robot. Default is 1
            robot_direction: direction the robot is facing. Default is NORTH
        """
        self.grid = Grid(size_x, size_y)

        self.robot = robot if robot else Robot(
            robot_x, robot_y, robot_direction)

        self.path_table = dict()
        self.cost_table = dict()
        self.motion_table = dict()

    def add_obstacle(
            self, x: int, y: int, direction: Direction, obstacle_id: int
    ) -> None:
        """
        Add an obstacle to the grid

        Args:
        x: x coordinate of the obstacle
        y: y coordinate of the obstacle
        direction: direction that the image on the obstacle is facing
        obstacle_id: id of the obstacle
        """
        self.grid.add_obstacle(Obstacle(x, y, direction, obstacle_id))

    def clear_obstacles(self) -> None:
        """
        Removes all obstacles from the grid
        """
        self.grid.reset_obstacles()

    def get_optimal_path(self) -> tuple[list[CellState], float]:
        """
        Get the optimal path between all possible view states for all obstacles using A* search and solving TSP problem

        Returns: 
            tuple[list[CellState], float]: an optimal path which is a list of all the CellStates involved, and cost of the path
        """
        min_dist = 1e9
        optimal_path = []

        # get all grid positions that can view the obstacle images
        views = self.grid.get_view_obstacle_positions()
        num_views = len(views)

        for bin_pos in self._get_visit_options(num_views):
            visit_states = [self.robot.get_start_state()]
            cur_view_positions = []

            for i in range(num_views):
                # if the i-th bit is 1, then the robot will visit the view position at obstacle i
                if bin_pos[i] == "1":
                    # add the view position to the current view positions
                    cur_view_positions.append(views[i])
                    # add the view position to flattened list of all view states
                    visit_states.extend(views[i])

            # for each visit state, generate path to all other visit states and cost of the paths using A* search
            self._generate_paths(visit_states)

            # generate all possible combinations of the view positions
            combinations = MazeSolver._generate_combinations(
                cur_view_positions, 0, [], [], ITERATIONS
            )

            # iterate over all the combinations and find the optimal path
            for combination in combinations:
                visited = [0]

                current_idx = 1  # idx 0 of visit_states: robot start state
                cost = 0

                # iterate over the views for each obstacle and calculate the cost of the path
                for idx, view_pos in enumerate(cur_view_positions):
                    # global index of selected view state in visit_states (flattened list of all view states)
                    visited.append(current_idx + combination[idx])
                    cost += view_pos[combination[idx]].penalty
                    # move starting idx to next obstacle
                    current_idx += len(view_pos)

                # initialize the cost matrix to travel between each obstacle
                cost_matrix = np.zeros((len(visited), len(visited)))

                for start_idx in range(len(visited) - 1):
                    for end_idx in range(start_idx + 1, len(visited)):
                        start_state = visit_states[visited[start_idx]]
                        end_state = visit_states[visited[end_idx]]

                        # check if the cost has already been calculated
                        if (start_state, end_state) in self.cost_table:
                            cost_matrix[start_idx, end_idx] = self.cost_table[
                                (start_state, end_state)
                            ]
                        else:
                            # initialize the cost matrix with a large value since the cost has not been calculated
                            cost_matrix[start_idx, end_idx] = 1e9

                    # add the cost for the reverse path
                        cost_matrix[end_idx, start_idx] = cost_matrix[
                            start_idx, end_idx
                        ]

                # set the cost of travelling from each state to itself to 0
                cost_matrix[:, 0] = 0

                # find Hamiltonian path with least cost for the selected combination of view states
                # solve_tsp_lin_kernighan is used instead of solve_tsp_dynamic_programming since it was the empirically fastest solver
                permutation, distance = solve_tsp_lin_kernighan(cost_matrix)

                # if the distance is more than the minimum distance, the path is irrelevant
                if distance + cost >= min_dist:
                    continue

                # update the minimum distance
                min_dist = distance + cost

                # update the optimal path
                optimal_path = [visit_states[0]]
                for idx in range(len(permutation) - 1):
                    from_state = visit_states[visited[permutation[idx]]]
                    to_state = visit_states[visited[permutation[idx + 1]]]

                    current_path = self.path_table[(from_state, to_state)]

                    # add each state from the current path to the optimal path
                    for idx2 in range(1, len(current_path)):
                        optimal_path.append(
                            CellState(
                                current_path[idx2][0],
                                current_path[idx2][1],
                                current_path[idx2][2],
                            )
                        )

                    # check position of to_state wrt to obstacle to snap screenshot from center/left/right.
                    obs = self.grid.find_obstacle_by_id(to_state.screenshot_id)
                    if obs:
                        pos = MazeSolver._get_capture_relative_position(
                            optimal_path[-1], obs
                        )
                        formatted = f"{to_state.screenshot_id}_{pos}"

                        optimal_path[-1].set_screenshot(formatted)
                    else:
                        raise ValueError(
                            f"Obstacle with id {to_state.screenshot_id} not found"
                        )

            # if the optimal path has been found, break the view positions loop
            if optimal_path:
                break

        return optimal_path, min_dist

    def _generate_paths(self, states: list[CellState]) -> None:
        """
        Generate and store the path between all combinations of all view states
        """
        for i in range(len(states) - 1):
            for j in range(i + 1, len(states)):
                self._astar_search(states[i], states[j])

    def _astar_search(self, start: CellState, end: CellState) -> None:
        """
        A* search algorithm to find the shortest path between two states
        Each state is defined by x, y, and direction.

        Heuristic: distance f = g + h
        g: Actual distance from the start state to the current state
        h: Estimated distance from the current state to the end state
        """
        # check if the path has already been calculated
        if (start, end) in self.path_table:
            return

        # initialize the actual distance dict with the start state
        g_dist = {(start.x, start.y, start.direction): 0}

        visited = set()
        parent_dict = {}

        # initialize min heap with the start state
        # the heap is a list of tuples (h, x, y, direction) where h is the estimated distance from the current state to the end state
        heap = [(self._estimate_distance(start, end),
                 start.x, start.y, start.direction)]

        while heap:
            # get the node with the minimum estimated distance
            _, x, y, direction = heapq.heappop(heap)

            # check if the node has already been visited
            if (x, y, direction) in visited:
                continue

            # if the terminal state is reached record the path and return
            if end.is_eq(x, y, direction):
                self._record_path(start, end, parent_dict,
                                  g_dist[(x, y, direction)])
                return

            # mark the node as visited
            visited.add((x, y, direction))
            dist = g_dist[(x, y, direction)]

            # traverse the neighboring states
            for (
                    new_x,
                    new_y,
                    new_direction,
                    safe_cost,
                    motion,
            ) in self._get_neighboring_states(x, y, direction):

                # check if the new state has already been visited
                if (new_x, new_y, new_direction) in visited:
                    continue

                if (
                        x,
                        y,
                        direction,
                        new_x,
                        new_y,
                        new_direction,
                ) not in self.motion_table and (
                        new_x,
                        new_y,
                        new_direction,
                        x,
                        y,
                        direction,
                ) not in self.motion_table:
                    # only need to store one of the two directions as the other will be the opposite
                    self.motion_table[
                        (x, y, direction, new_x, new_y, new_direction)
                    ] = motion

                # calculate the cost of robot turning
                turn_cost = TURN_FACTOR * Direction.turn_cost(
                    direction, new_direction
                )
                # calculate the cost of robot reversing
                reverse_cost = REVERSE_FACTOR * motion.reverse_cost()

                motion_cost = turn_cost + reverse_cost + safe_cost

                # check if there is a screenshot penalty
                if end.is_eq(new_x, new_y, new_direction):
                    screenshot_cost = end.penalty
                else:
                    screenshot_cost = 0

                # total cost f = g + h = safe_cost + rot_cost + screenshot_cost + dist + h (estimated distance)
                total_cost = (
                    dist
                    + motion_cost
                    + screenshot_cost
                    + self._estimate_distance(
                        CellState(new_x, new_y, new_direction), end
                    )
                )

                # update the g distance if the new state has not been visited or the new cost is less than the previous cost
                if (new_x, new_y, new_direction) not in g_dist or g_dist[
                    (new_x, new_y, new_direction)
                ] > dist + motion_cost + screenshot_cost:
                    g_dist[(new_x, new_y, new_direction)] = dist + \
                        motion_cost + screenshot_cost

                    # add the new state to the heap
                    heapq.heappush(
                        heap, (total_cost, new_x, new_y, new_direction))

                    # update the parent dict
                    parent_dict[(new_x, new_y, new_direction)] = (
                        x, y, direction)

    def _get_neighboring_states(
            self, x: int, y: int, direction: Direction
    ) -> list[tuple[int, int, Direction, int, Motion]]:
        """
        Returns list of possible valid cell states the robot can reach from its current position
        Neighbors have the following format: (newX, newY, movement direction, safe cost, motion)
        """
        # cell state already visited. caching significantly reduces algo runtime
        if (x, y, direction) in self.neighbor_cache:
            return self.neighbor_cache[(x, y, direction)]
        neighbors = []

        for dx, dy, md in MOVE_DIRECTION:
            if md == direction:  # if the new direction == md means straight-line motion
                # FORWARD
                if self.grid.reachable(x + dx, y + dy):  # go forward;
                    # Get safe cost of destination
                    safe_cost = self._calculate_safe_cost(x + dx, y + dy)
                    motion = Motion.FORWARD
                    neighbors.append((x + dx, y + dy, md, safe_cost, motion))

                # REVERSE
                if self.grid.reachable(x - dx, y - dy):  # go back;
                    # Get safe cost of destination
                    safe_cost = self._calculate_safe_cost(x - dx, y - dy)
                    motion = Motion.REVERSE
                    neighbors.append((x - dx, y - dy, md, safe_cost, motion))

            else:  # Turns
                delta_big = TURN_DISPLACEMENT[0]
                delta_small = TURN_DISPLACEMENT[1]

                # north -> east
                if direction == Direction.NORTH and md == Direction.EAST:
                    # FORWARD_RIGHT_TURN
                    if self.grid.turn_reachable(
                        x, y, x + delta_big, y + delta_small, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x + delta_big, y + delta_small
                        )
                        motion = Motion.FORWARD_RIGHT_TURN
                        neighbors.append(
                            (x + delta_big, y + delta_small,
                             md, safe_cost, motion)
                        )

                    # REVERSE_LEFT_TURN
                    if self.grid.turn_reachable(
                        x, y, x - delta_small, y - delta_big, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x - delta_small, y - delta_big
                        )
                        motion = Motion.REVERSE_LEFT_TURN
                        neighbors.append(
                            (x - delta_small, y - delta_big,
                             md, safe_cost, motion)
                        )

                # east -> north
                if direction == Direction.EAST and md == Direction.NORTH:
                    # FORWARD_LEFT_TURN
                    if self.grid.turn_reachable(
                        x, y, x + delta_small, y + delta_big, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x + delta_small, y + delta_big
                        )
                        motion = Motion.FORWARD_LEFT_TURN
                        neighbors.append(
                            (x + delta_small, y + delta_big,
                             md, safe_cost, motion)
                        )

                    # REVERSE_RIGHT_TURN
                    if self.grid.turn_reachable(
                        x, y, x - delta_big, y - delta_small, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x - delta_big, y - delta_small
                        )
                        motion = Motion.REVERSE_RIGHT_TURN
                        neighbors.append(
                            (x - delta_big, y - delta_small,
                             md, safe_cost, motion)
                        )

                # east -> south
                if direction == Direction.EAST and md == Direction.SOUTH:
                    # FORWARD_RIGHT_TURN
                    if self.grid.turn_reachable(
                        x, y, x + delta_small, y - delta_big, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x + delta_small, y - delta_big
                        )
                        motion = Motion.FORWARD_RIGHT_TURN
                        neighbors.append(
                            (x + delta_small, y - delta_big,
                             md, safe_cost, motion)
                        )

                    # REVERSE_LEFT_TURN
                    if self.grid.turn_reachable(
                        x, y, x - delta_big, y + delta_small, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x - delta_big, y + delta_small
                        )
                        motion = Motion.REVERSE_LEFT_TURN
                        neighbors.append(
                            (x - delta_big, y + delta_small,
                             md, safe_cost, motion)
                        )

                # south -> east
                if direction == Direction.SOUTH and md == Direction.EAST:
                    # FORWARD_LEFT_TURN
                    if self.grid.turn_reachable(
                        x, y, x + delta_big, y - delta_small, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x + delta_big, y - delta_small
                        )
                        motion = Motion.FORWARD_LEFT_TURN
                        neighbors.append(
                            (x + delta_big, y - delta_small,
                             md, safe_cost, motion)
                        )

                    # REVERSE_RIGHT_TURN
                    if self.grid.turn_reachable(
                        x, y, x - delta_small, y + delta_big, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x - delta_small, y + delta_big
                        )
                        motion = Motion.REVERSE_RIGHT_TURN
                        neighbors.append(
                            (x - delta_small, y + delta_big,
                             md, safe_cost, motion)
                        )

                # south -> west
                if direction == Direction.SOUTH and md == Direction.WEST:
                    # FORWARD_RIGHT_TURN
                    if self.grid.turn_reachable(
                        x, y, x - delta_big, y - delta_small, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x - delta_big, y - delta_small
                        )
                        motion = Motion.FORWARD_RIGHT_TURN
                        neighbors.append(
                            (x - delta_big, y - delta_small,
                             md, safe_cost, motion)
                        )

                    # REVERSE_LEFT_TURN
                    if self.grid.turn_reachable(
                        x, y, x + delta_small, y + delta_big, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x + delta_small, y + delta_big
                        )
                        motion = Motion.REVERSE_LEFT_TURN
                        neighbors.append(
                            (x + delta_small, y + delta_big,
                             md, safe_cost, motion)
                        )

                # west -> south
                if direction == Direction.WEST and md == Direction.SOUTH:
                    # FORWARD_LEFT_TURN
                    if self.grid.turn_reachable(
                        x, y, x - delta_small, y - delta_big, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x - delta_small, y - delta_big
                        )
                        motion = Motion.FORWARD_LEFT_TURN
                        neighbors.append(
                            (x - delta_small, y - delta_big,
                             md, safe_cost, motion)
                        )

                    # REVERSE_RIGHT_TURN
                    if self.grid.turn_reachable(
                        x, y, x + delta_big, y + delta_small, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x + delta_big, y + delta_small
                        )
                        motion = Motion.REVERSE_RIGHT_TURN
                        neighbors.append(
                            (x + delta_big, y + delta_small,
                             md, safe_cost, motion)
                        )

                # west -> north
                if direction == Direction.WEST and md == Direction.NORTH:
                    # FORWARD_RIGHT_TURN
                    if self.grid.turn_reachable(
                        x, y, x - delta_small, y + delta_big, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x - delta_small, y + delta_big
                        )
                        motion = Motion.FORWARD_RIGHT_TURN
                        neighbors.append(
                            (x - delta_small, y + delta_big,
                             md, safe_cost, motion)
                        )

                    # REVERSE_LEFT_TURN
                    if self.grid.turn_reachable(
                        x, y, x + delta_big, y - delta_small, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x + delta_big, y - delta_small
                        )
                        motion = Motion.REVERSE_LEFT_TURN
                        neighbors.append(
                            (x + delta_big, y - delta_small,
                             md, safe_cost, motion)
                        )

                # north <-> west
                if direction == Direction.NORTH and md == Direction.WEST:
                    # FORWARD_LEFT_TURN
                    if self.grid.turn_reachable(
                        x, y, x - delta_big, y + delta_small, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x - delta_big, y + delta_small
                        )
                        motion = Motion.FORWARD_LEFT_TURN
                        neighbors.append(
                            (x - delta_big, y + delta_small,
                             md, safe_cost, motion)
                        )

                    # REVERSE_RIGHT_TURN
                    if self.grid.turn_reachable(
                        x, y, x + delta_small, y - delta_big, direction
                    ):
                        safe_cost = self._calculate_safe_cost(
                            x + delta_small, y - delta_big
                        )
                        motion = Motion.REVERSE_RIGHT_TURN
                        neighbors.append(
                            (x + delta_small, y - delta_big,
                             md, safe_cost, motion)
                        )

        self.neighbor_cache[(x, y, direction)] = neighbors
        return neighbors

    def _calculate_safe_cost(self, new_x: int, new_y: int) -> int:
        """
        calculates the safe cost of moving to a new position, considering obstacles that the robot might touch.
        Currently, the function checks PADDING units in each direction.
        """
        for obj in self.grid.obstacles:
            if abs(obj.x - new_x) <= PADDING and abs(obj.y - new_y) <= PADDING:
                return SAFE_COST
            if abs(obj.y - new_y) <= PADDING and abs(obj.x - new_x) <= PADDING:
                return SAFE_COST
        return 0

    def _record_path(self, start: CellState, end: CellState, parent: dict[tuple[int, int, Direction], tuple[int, int, Direction]], cost: int) -> None:
        """
        Record the path between two states. Should be called only during the A* search.
        """
        # update the cost table for edges (start, end) and (end, start)
        self.cost_table[(start, end)] = cost
        self.cost_table[(end, start)] = cost

        # record the path
        path = []
        parent_pointer = (end.x, end.y, end.direction)
        while parent_pointer in parent:
            path.append(parent_pointer)
            parent_pointer = parent[parent_pointer]
        path.append(parent_pointer)

        # reverse the path and store it in the path table
        self.path_table[(start, end)] = path[::-1]
        self.path_table[(end, start)] = path

    @staticmethod
    def _estimate_distance(
            start: CellState, end: CellState, level: int = 0,
    ) -> int:
        """
        Estimate the distance between two states.
        level 0: Manhattan distance
        level 1: Euclidean distance
        """
        horizontal_distance = start.x - end.x
        vertical_distance = start.y - end.y

        # Euclidean distance
        if level == 1:
            return math.sqrt(horizontal_distance ** 2 + vertical_distance ** 2)

        # Manhattan distance
        return abs(horizontal_distance) + abs(vertical_distance)

    @staticmethod
    def _get_visit_options(n: int) -> list[str]:
        """
        Generate all possible visit options for n-digit binary numbers
        """
        max_len = bin(2 ** n - 1).count("1")
        strings = [bin(i)[2:].zfill(max_len) for i in range(2 ** n)]
        strings.sort(key=lambda x: x.count("1"), reverse=True)
        return strings

    @staticmethod
    def _generate_combinations(
            view_positions: list[list[CellState]],
            index: int,
            current: list[int],
            result: list[list[int]],
            num_iters: int,
    ) -> list[list[int]]:
        """
        Generate all possible combinations of the view positions, where one view state is selected for each obstacle

        :return: A list of lists, where each inner list is a unique combination of selected view states for all obstacles
        """
        # if all the view positions have been visited, add the current iteration's combination to the result
        if index == len(view_positions):
            result.append(current.copy())
            return result

        # if the number of iterations is 0, return the result
        if num_iters == 0:
            return result

        # update the number of iterations
        num_iters -= 1

        # iterate over the view positions and generate the combinations for the next view position
        for i in range(len(view_positions[index])):
            current.append(i)
            result = MazeSolver._generate_combinations(
                view_positions, index + 1, current, result, num_iters
            )
            current.pop()

        return result

    @staticmethod
    def _get_capture_relative_position(
        cell_state: CellState, obstacle: Obstacle
    ) -> str:
        """
        Determines the relative position of the obstacle (L, R, or C) with respect to the robot's orientation.
        This is used in image recognition heuristic when it detects multiple bounding boxes that are relatively the same size
        """
        x, y, direction = cell_state.x, cell_state.y, cell_state.direction
        x_obs, y_obs = obstacle.x, obstacle.y

        # check relative position based on the robot's direction
        if direction == Direction.NORTH:
            if x_obs == x and y_obs > y:
                return "C"
            elif x_obs < x:
                return "L"
            else:
                return "R"
        elif direction == Direction.SOUTH:
            if x_obs == x and y_obs < y:
                return "C"
            elif x_obs < x:
                return "R"
            else:
                return "L"
        elif direction == Direction.EAST:
            if y_obs == y and x_obs > x:
                return "C"
            elif y_obs < y:
                return "R"
            else:
                return "L"
        elif direction == Direction.WEST:
            if y_obs == y and x_obs < x:
                return "C"
            elif y_obs < y:
                return "L"
            else:
                return "R"
        else:
            raise ValueError(
                f"Invalid direction {direction}. This should never happen."
            )

    def optimal_path_to_motion_path(
            self, optimal_path: list[CellState]
    ) -> tuple[list[Motion], list[str], list[Obstacle]]:
        """
        Convert the optimal path to a list of motions that the robot needs to take
        """
        # requires the path table to be filled and the optimal path to be calculated
        motion_path = []
        obstacle_id_with_signals = []
        scanned_obstacles = []
        for i in range(len(optimal_path) - 1):
            from_state = optimal_path[i]
            to_state = optimal_path[i + 1]
            x, y, d = from_state.x, from_state.y, from_state.direction
            x_new, y_new, d_new = to_state.x, to_state.y, to_state.direction

            if (x_new, y_new, d_new, x, y, d) in self.motion_table:
                # if the motion is not found, check the reverse motion and get its opposite
                motion = self.motion_table[
                    (x_new, y_new, d_new, x, y, d)
                ].opposite_motion()
            elif (x, y, d, x_new, y_new, d_new) in self.motion_table:
                motion = self.motion_table[(x, y, d, x_new, y_new, d_new)]
            else:
                # if the motion is still not found, then the path is invalid
                raise ValueError(
                    f"Invalid path from {from_state} to {to_state}. This should never happen."
                )

            motion_path.append(motion)

            # check if the robot is taking a screenshot
            if to_state.screenshot_id != None:
                motion_path.append(Motion.CAPTURE)
                obstacle_id_with_signals.append(to_state.screenshot_id)
                obstacle_id = int(to_state.screenshot_id.split("_")[0])
                scanned_obstacles.append(
                    self.grid.find_obstacle_by_id(obstacle_id)
                )

        return motion_path, obstacle_id_with_signals, scanned_obstacles
