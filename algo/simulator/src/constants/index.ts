import { Direction, Position } from "../schemas/entity";

export const API_IP = "localhost"; // TODO: replace with your PC's local IPv4 address
export const PORT = "5000";

// Robot's Environment in grid cell units
const WIDTH_CM = 200;
const HEIGHT_CM = 200;
export const GRID_BLOCK_SIZE_CM = 10; // Size of each block in cm

export const GRID_TOTAL_WIDTH = WIDTH_CM / GRID_BLOCK_SIZE_CM; // 20
export const GRID_TOTAL_HEIGHT = HEIGHT_CM / GRID_BLOCK_SIZE_CM; // 20

// Obstacles
const OBSTACLE_WIDTH_CM = 10;
const OBSTACLE_HEIGHT_CM = 10;
export const OBSTACLE_GRID_PADDING = 2; // safe padding around each obstacle when generating random obstacles

export const OBSTACLE_GRID_WIDTH = OBSTACLE_WIDTH_CM / GRID_BLOCK_SIZE_CM; // 1
export const OBSTACLE_GRID_HEIGHT = OBSTACLE_HEIGHT_CM / GRID_BLOCK_SIZE_CM; // 1

// Robot's Footprint (Can be reduced according to measurements)
const ROBOT_WIDTH_CM = 30;
const ROBOT_HEIGHT_CM = 30;

export const ROBOT_GRID_WIDTH = ROBOT_WIDTH_CM / GRID_BLOCK_SIZE_CM; // 3
export const ROBOT_GRID_HEIGHT = ROBOT_HEIGHT_CM / GRID_BLOCK_SIZE_CM; // 3

export const ROBOT_ACTUAL_GRID_WIDTH = 20 / GRID_BLOCK_SIZE_CM; // 2
export const ROBOT_ACTUAL_GRID_HEIGHT = 21 / GRID_BLOCK_SIZE_CM; // 2.1

export const ROBOT_INITIAL_POSITION: Position = {
  x: 1,
  y: 1,
  d: Direction.NORTH,
  s: null
};

// Grid Animation
export const GRID_ANIMATION_SPEED = 100; // in milli-seconds

if (!API_IP) {
  throw Error("Update `API_IP` in `algo/simulator/src/constants/index.ts`");
}
