import { AlgoTestDataInterface } from ".";
import { Direction } from "../schemas/entity";

export const Obstacles8_Long: AlgoTestDataInterface = {
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

export const Obstacles8_TightSpaces: AlgoTestDataInterface = {
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

export const Obstacles8_A: AlgoTestDataInterface = {
    obstacles: [
        { id: 1, x: 0, y: 6, d: Direction.SOUTH },
        { id: 2, x: 5, y: 14, d: Direction.SOUTH },
        { id: 3, x: 6, y: 1, d: Direction.WEST },
        { id: 4, x: 7, y: 17, d: Direction.EAST },
        { id: 5, x: 9, y: 19, d: Direction.SOUTH },
        { id: 6, x: 16, y: 13, d: Direction.SOUTH },
        { id: 7, x: 18, y: 11, d: Direction.WEST },
        { id: 8, x: 18, y: 1, d: Direction.WEST },
    ],
};

export const Obstacles8_B: AlgoTestDataInterface = {
    obstacles: [
        { id: 1, x: 1, y: 13, d: Direction.SOUTH },
        { id: 2, x: 7, y: 6, d: Direction.WEST },
        { id: 3, x: 8, y: 2, d: Direction.EAST },
        { id: 4, x: 8, y: 19, d: Direction.SOUTH },
        { id: 5, x: 13, y: 7, d: Direction.SOUTH },
        { id: 6, x: 14, y: 14, d: Direction.EAST },
        { id: 7, x: 19, y: 18, d: Direction.WEST },
        { id: 8, x: 19, y: 2, d: Direction.WEST },
    ],
};