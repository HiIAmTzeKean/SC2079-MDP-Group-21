import { AlgoTestDataInterface } from ".";
import { ObstacleDirection } from "../../schemas/obstacle";

export const AlgoTestOfficialMockLayout: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 5, y: 9, d: ObstacleDirection.SOUTH },
    { id: 2, x: 7, y: 14, d: ObstacleDirection.WEST },
    { id: 3, x: 12, y: 9, d: ObstacleDirection.EAST },
    { id: 4, x: 15, y: 4, d: ObstacleDirection.WEST },
    { id: 5, x: 15, y: 15, d: ObstacleDirection.SOUTH },
  ],
};
