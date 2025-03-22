import { AlgoTestDataInterface } from ".";
import { Direction } from "../schemas/entity";

export const Obstacles5_Basic: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 7, y: 19, d: Direction.SOUTH },
    { id: 2, x: 6, y: 2, d: Direction.NORTH },
    { id: 3, x: 1, y: 15, d: Direction.SOUTH },
    { id: 4, x: 18, y: 12, d: Direction.WEST },
    { id: 5, x: 18, y: 6, d: Direction.WEST },
  ],
};

export const Obstacles5_OfficialMockLayout: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 5, y: 9, d: Direction.SOUTH },
    { id: 2, x: 7, y: 14, d: Direction.WEST },
    { id: 3, x: 12, y: 9, d: Direction.EAST },
    { id: 4, x: 15, y: 4, d: Direction.WEST },
    { id: 5, x: 15, y: 15, d: Direction.SOUTH },
  ],
};

export const Obstacles5_BriefingSlides: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 5, y: 7, d: Direction.NORTH },
    { id: 2, x: 5, y: 13, d: Direction.EAST },
    { id: 3, x: 12, y: 9, d: Direction.WEST },
    { id: 4, x: 15, y: 15, d: Direction.NORTH },
    { id: 5, x: 15, y: 4, d: Direction.SOUTH },
  ],
};

export const Obstacles5_A: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 1, y: 7, d: Direction.SOUTH },
    { id: 2, x: 3, y: 18, d: Direction.SOUTH },
    { id: 3, x: 10, y: 8, d: Direction.WEST },
    { id: 4, x: 15, y: 15, d: Direction.SOUTH },
    { id: 5, x: 19, y: 3, d: Direction.WEST },
  ],
};

