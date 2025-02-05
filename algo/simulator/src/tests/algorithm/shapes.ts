import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const AlgoTestShapes_V: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 2, y: 18, d: Direction.SOUTH },
    { id: 2, x: 10, y: 2, d: Direction.NORTH },
    { id: 3, x: 18, y: 18, d: Direction.SOUTH },
  ],
};
