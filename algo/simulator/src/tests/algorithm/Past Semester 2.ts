import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const Past_Semester_2: AlgoTestDataInterface = {
  obstacles: [
		{ id: 1, x: 1, y: 18, d: Direction.SOUTH },
		{ id: 2, x: 15, y: 16, d: Direction.SOUTH },
		{ id: 3, x: 6, y: 12, d: Direction.NORTH },
		{ id: 4, x: 19, y: 9, d: Direction.WEST },
		{ id: 5, x: 9, y: 7, d: Direction.EAST },
		{ id: 6, x: 13, y: 2, d: Direction.WEST },
	],
};
