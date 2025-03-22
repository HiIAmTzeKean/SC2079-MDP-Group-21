import { AlgoTestDataInterface } from ".";
import { Direction } from "../schemas/entity";

export const Basic_Mock: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 15, y: 10, d: Direction.WEST },
    { id: 2, x: 1, y: 18, d: Direction.SOUTH },
  ]
};

export const Basic_UTurn: AlgoTestDataInterface = {
  obstacles: [{ id: 1, x: 11, y: 2, d: Direction.NORTH }],
};

export const Basic_Corners: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 1, y: 18, d: Direction.EAST },
    { id: 2, x: 18, y: 18, d: Direction.SOUTH },
    { id: 3, x: 18, y: 1, d: Direction.WEST },
  ],
};
export const Basic_ShapeV: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 2, y: 18, d: Direction.SOUTH },
    { id: 2, x: 10, y: 2, d: Direction.NORTH },
    { id: 3, x: 18, y: 18, d: Direction.SOUTH },
  ],
};

export const Basic_CollisionCheckA: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 1, y: 13, d: Direction.SOUTH },
    { id: 2, x: 7, y: 13, d: Direction.WEST },
  ],
};

export const Basic_CollisionCheckB: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 10, y: 15, d: Direction.SOUTH },
    { id: 2, x: 10, y: 7, d: Direction.NORTH },
  ],
};

export const Basic_CollisionCheckC: AlgoTestDataInterface = {
  obstacles: [
    { id: 1, x: 9, y: 5, d: Direction.WEST },
    { id: 2, x: 9, y: 9, d: Direction.EAST },
    { id: 3, x: 17, y: 7, d: Direction.WEST },
  ],
};

