import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const A5Task: AlgoTestDataInterface = {
  obstacles: [
		{ id: 1, x: 9, y: 9, d: Direction.SOUTH },
		{ id: 2, x: 9, y: 9, d: Direction.NORTH },
		{ id: 3, x: 9, y: 9, d: Direction.WEST },
		{ id: 4, x: 9, y: 9, d: Direction.EAST },
	],
};
