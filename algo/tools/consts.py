# for both agent and obstacles.
# a higher value will allow robot to have more space to move around obstacles at the cost of it being harder to find a shortest path
EXPANDED_CELL: int = 1

# dimensions of arena (in 10 cm units)
ARENA_WIDTH: int = 20
ARENA_HEIGHT: int = 20
# no. of cells taken up by obstacle (in 10 cm units)
OBSTACLE_SIZE: int = 1

# no. of iterations to run algorithm for to find the most accurate shortest path
ITERATIONS: int = 5000

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
# TODO STM should tune turns to 10cm intervals, then this variable should be set to the robot's actual turn displacement.
# If tuning on STM side is not possible, tune by adjusting the actual commands in `commands.py`
# A smaller turn displacement is more ideal as it is more likely to generate a path to all obstacles.
# 20cm x 10cm turn displacement measured from center of robot
TURN_DISPLACEMENT: tuple[int, int] = [2, 1]

# offset due to position of robot's center / how many cells more the robot occupies from its center cell
OFFSET: int = 1
# for collision checking. minimum padding from robot to obstacle position
TURN_PADDING: int = (OFFSET + 1) * EXPANDED_CELL
MID_TURN_PADDING: int = (OFFSET + 1) * EXPANDED_CELL
PADDING: int = (OFFSET + 1) * EXPANDED_CELL

# minimum number of cells away front of robot should be from obstacle in view state generation
MIN_CLEARANCE: int = 1  # front of robot at least 10cm away

# Use ultrasonic sensor for straight-line motions, to reset movement error build-up
W_COMMAND_FLAG = 0  # 0: disable w/W commands, 1: enable w/W commands
