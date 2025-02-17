import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const AlgoTestOfficialMockLayout: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 5, y: 9, d: Direction.SOUTH },
    { id: 2, x: 7, y: 14, d: Direction.WEST },
    { id: 3, x: 12, y: 9, d: Direction.EAST },
    { id: 4, x: 15, y: 4, d: Direction.WEST },
    { id: 5, x: 15, y: 15, d: Direction.SOUTH },
  ],
};
