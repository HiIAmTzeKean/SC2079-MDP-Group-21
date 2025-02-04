import { AlgoTestDataInterface } from ".";
import { Obstacle, ObstacleDirection } from "../../schemas/obstacle";

const obstacles: Obstacle[] = [
  { id: 1, x: 1, y: 18, d: ObstacleDirection.EAST },
  { id: 2, x: 18, y: 18, d: ObstacleDirection.SOUTH },
  { id: 3, x: 18, y: 1, d: ObstacleDirection.WEST },
];

export const AlgoTestCorners: AlgoTestDataInterface = {
  obstacles: obstacles,
};
