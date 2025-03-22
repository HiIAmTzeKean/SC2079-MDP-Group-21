import { AlgoTestDataInterface } from ".";
import { Direction } from "../schemas/entity";

export const Obstacles6_PastSem1: AlgoTestDataInterface = {
	obstacles: [
		{ id: 1, x: 1, y: 18, d: Direction.EAST },
		{ id: 2, x: 5, y: 14, d: Direction.NORTH },
		{ id: 3, x: 15, y: 17, d: Direction.WEST },
		{ id: 4, x: 19, y: 10, d: Direction.WEST },
		{ id: 5, x: 10, y: 9, d: Direction.EAST },
		{ id: 6, x: 13, y: 2, d: Direction.NORTH },
	],
};

export const Obstacles6_A: AlgoTestDataInterface = {
	obstacles: [
		{ id: 1, x: 1, y: 18, d: Direction.SOUTH },
		{ id: 2, x: 6, y: 12, d: Direction.NORTH },
		{ id: 3, x: 10, y: 7, d: Direction.EAST },
		{ id: 4, x: 13, y: 2, d: Direction.EAST },
		{ id: 5, x: 15, y: 16, d: Direction.WEST },
		{ id: 6, x: 19, y: 9, d: Direction.WEST },
	],
};