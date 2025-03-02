import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const Obstacles_8_long: AlgoTestDataInterface = {
  obstacles: [
		{ id: 1, x: 4, y: 3, d: Direction.EAST },
		{ id: 2, x: 9, y: 12, d: Direction.SOUTH },
		{ id: 3, x: 12, y: 4, d: Direction.NORTH },
		{ id: 4, x: 14, y: 14, d: Direction.WEST },
		{ id: 5, x: 17, y: 6, d: Direction.SOUTH },
		{ id: 6, x: 3, y: 19, d: Direction.SOUTH },
		{ id: 7, x: 19, y: 18, d: Direction.WEST },
		{ id: 8, x: 6, y: 9, d: Direction.WEST },
	],
};
