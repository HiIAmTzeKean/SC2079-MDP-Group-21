import { AlgoTestDataInterface } from ".";
import { Obstacle, ObstacleDirection } from "../../schemas/obstacle";

const obstacles: Obstacle[] = [{ id: 1, x: 11, y: 2, d: ObstacleDirection.NORTH }];

export const AlgoTestBasicUTurn: AlgoTestDataInterface = {
  obstacles: obstacles,
};
