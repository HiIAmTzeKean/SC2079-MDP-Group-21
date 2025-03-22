from algo.entities.entity import CellState
from algo.tools.movement import Direction


class Robot:
    def __init__(self, center_x: int, center_y: int, start_direction: Direction) -> None:
        """Robot object class

        Args:
            center_x (int): x coordinate of center of robot
            center_y (int): y coordinate of center of robot
            start_direction (Direction): Direction robot is facing at the start
        """
        self.states: list[CellState] = [
            CellState(center_x, center_y, start_direction)]

    def get_start_state(self) -> CellState:
        """Returns the starting cell state of the robot

        Returns:
            CellState: starting cell state of robot (x,y,direction)
        """
        return self.states[0]
