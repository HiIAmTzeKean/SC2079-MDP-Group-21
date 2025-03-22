
import time

import os
import sys
# Allows Python to find packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from algo.algorithms.algo import MazeSolver  # nopep8
from algo.tools.commands import CommandGenerator  # nopep8
from algo.tools.movement import Direction  # nopep8

obstacles = [
    {"x": 0, "y": 17, "d": Direction.EAST, "id": 1},
    {"x": 5, "y": 12, "d": Direction.SOUTH, "id": 2},
    {"x": 7, "y": 5, "d": Direction.NORTH, "id": 3},
    {"x": 15, "y": 2, "d": Direction.WEST, "id": 4},
    {"x": 11, "y": 14, "d": Direction.EAST, "id": 5},
    {"x": 16, "y": 19, "d": Direction.SOUTH, "id": 6},
    {"x": 19, "y": 9, "d": Direction.WEST, "id": 7}
]

maze_solver = MazeSolver(size_x=20, size_y=20, robot_x=1,
                         robot_y=1, robot_direction=Direction.NORTH)

for ob in obstacles:
    maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])

start = time.time()
optimal_path, cost = maze_solver.get_optimal_path()
print(
    f"Time taken to find shortest path using A* search: {time.time() - start}s")
print(f"cost to travel: {cost} units")

motions, obstacle_ids = maze_solver.optimal_path_to_motion_path(optimal_path)
command_generator = CommandGenerator()
commands = command_generator.generate_commands(motions, obstacle_ids)
print(commands)
