import { AlgoTestDataInterface } from ".";
import { Obstacle, Direction } from "../../schemas/entity";

const obstacles: Obstacle[] = [
  { id: 1, x: 1, y: 18, d: Direction.EAST },
  { id: 2, x: 18, y: 18, d: Direction.SOUTH },
  { id: 3, x: 18, y: 1, d: Direction.WEST },
];

export const AlgoTestCorners: AlgoTestDataInterface = {
  obstacles: obstacles,
};
