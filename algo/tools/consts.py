# for both agent and obstacles.
# a higher value will allow robot to have more space to move around obstacles at the cost of it being harder to find a shortest path
EXPANDED_CELL = 1

# dimensions of arena (in 10cm units)
WIDTH = 20
HEIGHT = 20

# no. of iterations to run algorithm for to find the most accurate shortest path
ITERATIONS = 2000

# Cost for the chance that the robot touches an obstacle.
# The higher the value, the less likely the robot moves too close to an obstacle.
SAFE_COST = 1000

# Cost of taking an image off center.
# The higher the value, the less likely the robot takes pictures from a position that is not directly in front of image.
SCREENSHOT_COST = 50

# Cost of turning the robot.
# The higher the value, the less likely the robot is to turn.
TURN_FACTOR = 5

# Cost of reversing the robot.
# The higher the value, the less likely the robot is to reverse.
REVERSE_FACTOR = 5

# no. of units the robot turns
TURN_RADIUS = 1

TURN_WRT_BIG_TURNS = [[3 * TURN_RADIUS, TURN_RADIUS],
                      [6 * TURN_RADIUS, 3 * TURN_RADIUS]]
# The number of grid squares the robot moves for a half turn on each axis. This must be tuned based on real robot movement.
HALF_TURNS = [6 * TURN_RADIUS, 2 * TURN_RADIUS]
