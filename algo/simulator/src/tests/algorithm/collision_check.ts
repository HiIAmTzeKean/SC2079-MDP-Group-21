import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const AlgoTestCollisionCheck_A: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 1, y: 13, d: Direction.SOUTH },
    { id: 2, x: 7, y: 13, d: Direction.WEST },
  ],
};

export const AlgoTestCollisionCheck_B: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 10, y: 15, d: Direction.SOUTH },
    { id: 2, x: 10, y: 7, d: Direction.NORTH },
  ],
};

export const AlgoTestCollisionCheck_C: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 9, y: 5, d: Direction.WEST },
    { id: 2, x: 9, y: 9, d: Direction.EAST },
    { id: 2, x: 17, y: 7, d: Direction.WEST },
  ],
};
