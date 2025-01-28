from algorithms.algo import MazeSolver
from entities.entity import Obstacle
from tools.helper import *
from tools.consts import *
from algorithms.simulation import MazeSolverSimulation
import time

obstacles = [
    {"x": 0, "y": 17, "d": Direction.EAST, "id": 1},
    {"x": 5, "y": 12, "d": Direction.SOUTH, "id": 2},
    {"x": 7, "y": 5, "d": Direction.NORTH, "id": 3},
    {"x": 15, "y": 2, "d": Direction.WEST, "id": 4},
    {"x": 11, "y": 14, "d": Direction.EAST, "id": 5},
    {"x": 16, "y": 19, "d": Direction.SOUTH, "id": 6},
    {"x": 19, "y": 9, "d": Direction.WEST, "id": 7}
]


# -------------------- TESTING SIMULATOR --------------------
sim = MazeSolverSimulation(
    grid_size_x=20,
    grid_size_y=20,
    robot_x=1,
    robot_y=1,
    robot_direction=Direction.NORTH,
    big_turn=1
)

sim.enable_debug(0)

# sim.load_obstacles(0)  # load obstacles from file option 0 for last
# sim.generate_random_obstacles(2)
for ob in obstacles:
    sim.maze_solver.add_obstacle(ob["x"], ob["y"], ob["d"], ob["id"])

sim.plot_optimal_path_animation(testing=True)


# -------------------- TESTING ACTUAL ALGO --------------------
maze_solver = MazeSolver(size_x=20, size_y=20, robot_x=1,
                         robot_y=1, robot_direction=Direction.NORTH, big_turn=1)

for ob in obstacles:
    maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])

start = time.time()
optimal_path, cost = maze_solver.get_optimal_path(retrying=False)
print(
    f"Time taken to find shortest path using A* search: {time.time() - start}s")
print(f"cost to travel: {cost} units")

motions = maze_solver.optimal_path_to_motion_path(optimal_path)
command_generator = CommandGenerator()
commands = command_generator.generate_commands(motions)
print(commands)

path_results = [optimal_path[0].get_dict()]
for pos in optimal_path:
    path_results.append(pos.get_dict())
