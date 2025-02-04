/** The direction an Obstacle's image is facing */
export enum ObstacleDirection {
  NORTH = 0,
  EAST = 2,
  SOUTH = 4,
  WEST = 6,
  SKIP = 8,

}

/** Obstacle with it's (x, y) co-ordinates, image face direction, and id */
export interface Obstacle {
  id: number; // obstacle_id
  x: number; // grid format
  y: number; // grid format
  d: ObstacleDirection; // obstacle face direction
}

export const ObstacleDirectionStringMapping = {
  [ObstacleDirection.NORTH]: "North",
  [ObstacleDirection.SOUTH]: "South",
  [ObstacleDirection.EAST]: "East",
  [ObstacleDirection.WEST]: "West",
  [ObstacleDirection.SKIP]: "Skip",
};
