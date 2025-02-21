import { AlgoTestDataInterface } from ".";
import { Direction } from "../../schemas/entity";

export const obstacles_5_BriefingSlides: AlgoTestDataInterface = {
  obstacles: [
		{ id: 1, x: 5, y: 7, d: Direction.NORTH },
		{ id: 2, x: 5, y: 13, d: Direction.EAST },
		{ id: 3, x: 12, y: 9, d: Direction.WEST },
		{ id: 4, x: 15, y: 15, d: Direction.NORTH },
		{ id: 5, x: 15, y: 4, d: Direction.SOUTH },
	],
};
