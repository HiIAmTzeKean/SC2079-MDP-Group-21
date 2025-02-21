import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const obstacles8tightspaces: AlgoTestDataInterface = {
  obstacles: [
		{ id: 1, x: 13, y: 6, d: Direction.SOUTH },
		{ id: 2, x: 5, y: 4, d: Direction.NORTH },
		{ id: 3, x: 10, y: 9, d: Direction.SOUTH },
		{ id: 4, x: 6, y: 10, d: Direction.NORTH },
		{ id: 5, x: 10, y: 13, d: Direction.NORTH },
		{ id: 6, x: 13, y: 11, d: Direction.EAST },
		{ id: 7, x: 8, y: 2, d: Direction.NORTH },
		{ id: 8, x: 16, y: 13, d: Direction.WEST },
	],
};
