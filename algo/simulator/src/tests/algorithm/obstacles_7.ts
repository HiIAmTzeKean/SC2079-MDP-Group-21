import { AlgoTestDataInterface } from ".";
import { Obstacle, Direction } from "../../schemas/entity";

const obstacles: Obstacle[] = [
  { id: 1, x: 1, y: 10, d: Direction.NORTH },
  { id: 2, x: 9, y: 8, d: Direction.WEST },
  { id: 3, x: 6, y: 1, d: Direction.EAST },
  { id: 4, x: 1, y: 18, d: Direction.EAST },
  { id: 5, x: 18, y: 18, d: Direction.SOUTH },
  { id: 6, x: 18, y: 0, d: Direction.NORTH },
  { id: 7, x: 12, y: 17, d: Direction.SOUTH },
];

export const AlgoTestObstacles_7: AlgoTestDataInterface = {
  obstacles: obstacles,
};
