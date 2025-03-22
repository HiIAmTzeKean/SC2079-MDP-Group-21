import { AlgoTestDataInterface } from ".";
import { Direction } from "../schemas/entity";

export const Misc_Custom: AlgoTestDataInterface = {
	obstacles: [],
};


export const Misc_TaskA5: AlgoTestDataInterface = {
	obstacles: [
		{ id: 1, x: 9, y: 9, d: Direction.SOUTH },
		{ id: 2, x: 9, y: 9, d: Direction.NORTH },
		{ id: 3, x: 9, y: 9, d: Direction.WEST },
		{ id: 4, x: 9, y: 9, d: Direction.EAST },
	],
};

export const Misc_FailTest: AlgoTestDataInterface = {
	obstacles: [
		{ id: 1, x: 19, y: 19, d: Direction.SOUTH },
		{ id: 2, x: 0, y: 19, d: Direction.NORTH },
		{ id: 3, x: 19, y: 1, d: Direction.SOUTH },
	],
};

