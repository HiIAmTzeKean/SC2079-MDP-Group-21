import { AlgoTestDataInterface } from ".";
import { Obstacle, Direction } from "../../schemas/entity";

const obstacles: Obstacle[] = [
  { id: 1, x: 15, y: 10, d: Direction.WEST },
  { id: 2, x: 1, y: 18, d: Direction.SOUTH },
];

export const AlgoTestBasicMock: AlgoTestDataInterface = {
  obstacles: obstacles,
};
