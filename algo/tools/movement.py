
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


# move direction is a list of the possible moves the robot can make
MOVE_DIRECTION = [
    (1, 0, Direction.EAST),
    (-1, 0, Direction.WEST),
    (0, 1, Direction.NORTH),
    (0, -1, Direction.SOUTH),
]


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
            raise ValueError(f"Invalid motion {
                             self}. This should never happen.")

        return Motion(opp_val)

    def is_combinable(self):
        if self == Motion.CAPTURE:
            return False
        return self not in [Motion.FORWARD_OFFSET_LEFT, Motion.FORWARD_OFFSET_RIGHT, Motion.REVERSE_OFFSET_RIGHT, Motion.REVERSE_OFFSET_LEFT]

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
