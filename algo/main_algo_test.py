from algorithms.algo import MazeSolver
from entities.entity import Obstacle
from tools.helper import *
from tools.consts import *
from algorithms.simulation import MazeSolverSimulation

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
sim.add_obstacles([(12, 2, Direction.WEST, 1), (1, 10, Direction.EAST, 2), (11, 18, Direction.SOUTH, 3)])
# sim.add_obstacles([(11, 18, Direction.SOUTH, 3)])


sim.plot_optimal_path_animation(testing=True)
