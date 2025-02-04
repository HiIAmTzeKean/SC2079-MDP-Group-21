import { AlgoTestDataInterface } from ".";
import { ObstacleDirection } from "../../schemas/obstacle";

export const AlgoTestCollisionCheck_A: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 1, y: 13, d: ObstacleDirection.SOUTH },
    { id: 2, x: 7, y: 13, d: ObstacleDirection.WEST },
  ],
};

export const AlgoTestCollisionCheck_B: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 10, y: 15, d: ObstacleDirection.SOUTH },
    { id: 2, x: 10, y: 7, d: ObstacleDirection.NORTH },
  ],
};

export const AlgoTestCollisionCheck_C: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 9, y: 5, d: ObstacleDirection.WEST },
    { id: 2, x: 9, y: 9, d: ObstacleDirection.EAST },
    { id: 2, x: 17, y: 7, d: ObstacleDirection.WEST },
  ],
};
