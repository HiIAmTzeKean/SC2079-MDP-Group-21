# for both agent and obstacles.
# a higher value will allow robot to have more space to move around obstacles at the cost of it being harder to find a shortest path
EXPANDED_CELL = 1

# dimensions of arena (in 10 cm units)
ARENA_WIDTH = 20
ARENA_HEIGHT = 20

# no. of iterations to run algorithm for to find the most accurate shortest path
ITERATIONS = 2000

# Cost for the chance that the robot touches an obstacle.
# The higher the value, the less likely the robot moves too close to an obstacle.
SAFE_COST = 1000

# Cost of taking an image off center.
# The higher the value, the less likely the robot takes pictures from a position that is not directly in front of image.
SCREENSHOT_COST = 100
DISTANCE_COST = 50  # the cost for when the robot is too close or too far from the obstacle

# Cost of turning the robot.
# The higher the value, the less likely the robot is to turn.
TURN_FACTOR = 5

# Cost of half-turning the robot.
# The higher the value, the less likely the robot is to make half-turns.
# weighted by 2 since it makes 2 half-turns in an offset motion
HALF_TURN_FACTOR = 4 * 2

# Cost of reversing the robot.
# The higher the value, the less likely the robot is to reverse.
REVERSE_FACTOR = 5

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
TURN_DISPLACEMENT = [4, 4]

# offset due to position of robot's center / how many cells more the robot occupies from its center cell
OFFSET = 1
# for collision checking. minimum padding from robot to obstacle position
TURN_PADDING = (OFFSET + 1) * EXPANDED_CELL
MID_TURN_PADDING = (OFFSET + 1) * EXPANDED_CELL
PADDING = (OFFSET + 1) * EXPANDED_CELL

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
HALF_TURNS_DISPLACEMENT = [6, 2]
