import { AlgoTestDataInterface } from ".";
import { Direction } from "../schemas/entity";

export const Obstacles7_A: AlgoTestDataInterface = {
	obstacles: [
		{ id: 1, x: 1, y: 10, d: Direction.NORTH },
		{ id: 2, x: 9, y: 8, d: Direction.WEST },
		{ id: 3, x: 6, y: 1, d: Direction.EAST },
		{ id: 4, x: 1, y: 18, d: Direction.EAST },
		{ id: 5, x: 18, y: 18, d: Direction.SOUTH },
		{ id: 6, x: 18, y: 0, d: Direction.NORTH },
		{ id: 7, x: 12, y: 17, d: Direction.SOUTH },
	],
};

export const Obstacles7_B: AlgoTestDataInterface = {
	obstacles: [
		{ id: 1, x: 0, y: 17, d: Direction.EAST },
		{ id: 2, x: 5, y: 12, d: Direction.SOUTH },
		{ id: 3, x: 7, y: 5, d: Direction.NORTH },
		{ id: 4, x: 15, y: 2, d: Direction.WEST },
		{ id: 5, x: 11, y: 14, d: Direction.EAST },
		{ id: 6, x: 16, y: 19, d: Direction.SOUTH },
		{ id: 7, x: 19, y: 9, d: Direction.WEST },
	],
};

export const Obstacles7_PastSem1: AlgoTestDataInterface = {
	obstacles: [
		{ id: 1, x: 1, y: 18, d: Direction.SOUTH },
		{ id: 2, x: 15, y: 16, d: Direction.SOUTH },
		{ id: 3, x: 6, y: 12, d: Direction.NORTH },
		{ id: 4, x: 19, y: 9, d: Direction.WEST },
		{ id: 5, x: 9, y: 7, d: Direction.EAST },
		{ id: 6, x: 13, y: 2, d: Direction.WEST },
	],
};

export const Obstacles7_PastSem2: AlgoTestDataInterface = {
	obstacles: [
		{ id: 1, x: 1, y: 17, d: Direction.EAST },
		{ id: 2, x: 16, y: 19, d: Direction.SOUTH },
		{ id: 3, x: 5, y: 11, d: Direction.SOUTH },
		{ id: 4, x: 7, y: 4, d: Direction.NORTH },
		{ id: 5, x: 14, y: 3, d: Direction.WEST },
		{ id: 6, x: 11, y: 14, d: Direction.SOUTH },
		{ id: 7, x: 19, y: 9, d: Direction.WEST },
	],
};

