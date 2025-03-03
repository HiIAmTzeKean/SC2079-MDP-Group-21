import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const FailTest: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 19, y: 19, d: Direction.SOUTH },
    { id: 2, x: 0, y: 19, d: Direction.NORTH },
    { id: 3, x: 19, y: 1, d: Direction.SOUTH },
  ],
};
