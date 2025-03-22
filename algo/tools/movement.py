
from enum import Enum


class Direction(int, Enum):
    NORTH: int = 0
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 6
    SKIP: int = 8

    def __int__(self) -> int:
        return self.value

    @staticmethod
    def turn_cost(d1: "Direction", d2: "Direction") -> int:
        """
        Calculate the cost of turning from direction d1 to direction d2
        If the robot does not turn, the cost is 0.
        """
        if d1 == Direction.NORTH:
            if d2 in [Direction.EAST, Direction.WEST]:
                return 1
            elif d2 == Direction.NORTH:
                return 0
            else:
                raise ValueError("Robot cannot turn from north to south")

        elif d1 == Direction.SOUTH:
            if d2 in [Direction.EAST, Direction.WEST]:
                return 1
            elif d2 == Direction.SOUTH:
                return 0
            else:
                raise ValueError("Robot cannot turn from south to north")

        elif d1 == Direction.EAST:
            if d2 in [Direction.NORTH, Direction.SOUTH]:
                return 1
            elif d2 == Direction.EAST:
                return 0
            else:
                raise ValueError("Robot cannot turn from east to west")

        elif d1 == Direction.WEST:
            if d2 in [Direction.NORTH, Direction.SOUTH]:
                return 1
            elif d2 == Direction.WEST:
                return 0
            else:
                raise ValueError("Robot cannot turn from west to east")

        else:
            raise ValueError(f"direction {d1} is not a valid direction.")

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


# move direction is a list of the possible moves the robot can make (x, y, direction)
MOVE_DIRECTION: list[tuple[int, int, Direction]] = [
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
    FORWARD_LEFT_TURN: int = 0
    FORWARD: int = 2
    FORWARD_RIGHT_TURN: int = 4

    REVERSE_LEFT_TURN: int = 10
    REVERSE: int = 8
    REVERSE_RIGHT_TURN: int = 6

    CAPTURE: int = 1000

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Motion):
            return NotImplemented
        return self.value == other.value

    def opposite_motion(self) -> "Motion":
        if self == Motion.CAPTURE:
            return Motion.CAPTURE

        opp_val: int = 10 - self.value
        if opp_val == 5 or opp_val < 0 or opp_val > 10:
            raise ValueError(
                f"Invalid motion {self}. This should never happen.")

        return Motion(opp_val)

    def is_combinable(self) -> bool:
        if self == Motion.CAPTURE:
            return False
        return self in [Motion.REVERSE, Motion.FORWARD]

    def reverse_cost(self) -> int:
        if self == Motion.CAPTURE:
            raise ValueError("Capture motion does not have a reverse cost")
        elif self in [
            Motion.REVERSE_LEFT_TURN,
            Motion.REVERSE_RIGHT_TURN,
            Motion.REVERSE
        ]:
            return 1
        else:
            return 0
