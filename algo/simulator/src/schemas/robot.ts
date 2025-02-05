export interface RobotPosition {
  s: number | null; // screenshot_id
  x: number;
  y: number;
  d: Direction;
}

export enum Direction {
  NORTH = 0,
  EAST = 2,
  SOUTH = 4,
  WEST = 6,
  SKIP = 8,
}
