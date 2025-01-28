from enum import Enum


class Direction(int, Enum):
    NORTH = 0
    EAST = 2
    SOUTH = 4
    WEST = 6
    SKIP = 8

    def __int__(self):
        return self.value

    @staticmethod
    def rotation_cost(d1, d2):
        diff = abs(d1 - d2)
        return min(diff, 8 - diff)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Motion(int, Enum):
    """
    Enum class for the motion of the robot between two cells
    """
    # the robot can move in 10 different ways from one cell to another
    # designed so that 10 - motion = opposite motion
    FORWARD_LEFT_TURN = 0
    FORWARD_OFFSET_LEFT = 1
    FORWARD = 2
    FORWARD_OFFSET_RIGHT = 3
    FORWARD_RIGHT_TURN = 4

    REVERSE_LEFT_TURN = 10
    REVERSE_OFFSET_RIGHT = 9
    REVERSE = 8
    REVERSE_OFFSET_LEFT = 7
    REVERSE_RIGHT_TURN = 6

    CAPTURE = 1000

    def __int__(self):
        return self.value

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other: 'Motion'):
        return self.value == other.value

    def opposite_motion(self):
        if self == Motion.CAPTURE:
            return Motion.CAPTURE

        opp_val = 10 - self.value
        if opp_val == 5 or opp_val < 0 or opp_val > 10:
            raise ValueError(f"Invalid motion {self}. This should never happen.")

        return Motion(opp_val)

    def is_combinable(self):
        if self == Motion.CAPTURE:
            return False
        return self.value not in [1, 3, 9, 7]

    def reverse_cost(self):
        if self == Motion.CAPTURE:
            raise ValueError("Capture motion does not have a reverse cost")
        if self in [Motion.REVERSE_OFFSET_RIGHT, Motion.REVERSE_OFFSET_LEFT, Motion.REVERSE_LEFT_TURN,
                    Motion.REVERSE_RIGHT_TURN]:
            return 5
        elif self == Motion.REVERSE:
            return 1
        else:
            return 0


# move direction is a list of the possible moves the robot can make
MOVE_DIRECTION = [
    (1, 0, Direction.EAST),
    (-1, 0, Direction.WEST),
    (0, 1, Direction.NORTH),
    (0, -1, Direction.SOUTH),
]

TURN_FACTOR = 5

REVERSE_FACTOR = 5

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
