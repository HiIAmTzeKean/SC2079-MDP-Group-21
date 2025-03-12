# for both agent and obstacles.
# a higher value will allow robot to have more space to move around obstacles at the cost of it being harder to find a shortest path
EXPANDED_CELL: int = 1

# dimensions of arena (in 10 cm units)
ARENA_WIDTH: int = 20
ARENA_HEIGHT: int = 20
# no. of cells taken up by obstacle (in 10 cm units)
OBSTACLE_SIZE: int = 1

# no. of iterations to run algorithm for to find the most accurate shortest path
ITERATIONS: int = 2000

# Cost for the chance that the robot touches an obstacle.
# The higher the value, the less likely the robot moves too close to an obstacle.
SAFE_COST: int = 1000

# Cost of taking an image off center.
# The higher the value, the less likely the robot takes pictures from a position that is not directly in front of image.
SCREENSHOT_COST: int = 100
# the cost for when the robot is too close or too far from the obstacle
DISTANCE_COST: int = 1000

# Cost of turning the robot.
# The higher the value, the less likely the robot is to turn.
TURN_FACTOR: int = 5

# Cost of half-turning the robot.
# The higher the value, the less likely the robot is to make half-turns.
# weighted by 2 since it makes 2 half-turns in an offset motion
HALF_TURN_FACTOR: int = 4 * 200

# Cost of reversing the robot.
# The higher the value, the less likely the robot is to reverse.
REVERSE_FACTOR: int = 0

"""
No. of units the robot turns. This must be tuned based on real robot movement.
eg. Motion.FORWARD_LEFT_TURN
.  .   .  .  .
.  .   .  .  .   
X ←----┐  .  .  
.  .   |  .  .   
.  .   X  .  .

0: long axis, 1: short axis
"""
# TODO: tune to 10cm interval
TURN_DISPLACEMENT: tuple[int, int] = [2, 1]

# offset due to position of robot's center / how many cells more the robot occupies from its center cell
OFFSET: int = 1
# for collision checking. minimum padding from robot to obstacle position
TURN_PADDING: int = (OFFSET + 1) * EXPANDED_CELL
MID_TURN_PADDING: int = (OFFSET + 1) * EXPANDED_CELL
PADDING: int = (OFFSET + 1) * EXPANDED_CELL

# minimum number of cells away front of robot should be from obstacle in view state generation
MIN_CLEARANCE: int = 1  # front of robot at least 10cm away

"""
The number of grid squares the robot moves for TWO half turns on each axis. This must be tuned based on real robot movement.
eg. Motion.FORWARD_OFFSET_LEFT: TWO half turns to end up diagonally in the specified direction
.  . X .  .  .
.  . ↑ .  .  .   
.  . └o┐  .  .  
.  .   |  .  .   
.  .   X  .  .

0: long axis, 1: short axis
"""
# TODO: tune to 10cm interval
HALF_TURNS_DISPLACEMENT: tuple[int, int] = [3, 1]

# TODO: remove when done testing
W_COMMAND_FLAG = 0  # 0: disable w/W commands, 1: enable w/W cmoomands
