/** The direction an Obstacle's image or the Robot is facing */
export enum Direction {
  NORTH = 0,
  EAST = 2,
  SOUTH = 4,
  WEST = 6,
  SKIP = 8,
}

export interface Position {
  s: string | null; // screenshot: "obstacleid_L/C/R"
  x: number;
  y: number;
  d: Direction;
}

/** Obstacle with its id, (x, y) coordinates, obstacle image direction */
export interface Obstacle {
  id: number;
  x: number;
  y: number;
  d: Direction;
}

export const DirectionStringMapping = {
  [Direction.NORTH]: "North",
  [Direction.SOUTH]: "South",
  [Direction.EAST]: "East",
  [Direction.WEST]: "West",
  [Direction.SKIP]: "Skip",
};
