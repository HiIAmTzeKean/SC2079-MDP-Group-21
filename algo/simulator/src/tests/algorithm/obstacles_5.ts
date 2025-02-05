import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const AlgoTestObstacles_5_Basic: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 7, y: 19, d: Direction.SOUTH },
    { id: 2, x: 6, y: 2, d: Direction.NORTH },
    { id: 3, x: 1, y: 15, d: Direction.SOUTH },
    { id: 4, x: 18, y: 12, d: Direction.WEST },
    { id: 5, x: 18, y: 6, d: Direction.WEST },
  ],
};
