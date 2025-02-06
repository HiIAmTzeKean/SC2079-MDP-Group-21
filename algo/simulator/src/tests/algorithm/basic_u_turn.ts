import { AlgoTestDataInterface } from ".";
import { Obstacle, Direction } from "../../schemas/entity";

const obstacles: Obstacle[] = [{ id: 1, x: 11, y: 2, d: Direction.NORTH }];

export const AlgoTestBasicUTurn: AlgoTestDataInterface = {
  obstacles: obstacles,
};
