/* eslint-disable @typescript-eslint/no-unused-vars */

import { Direction, RobotPosition } from "../schemas/robot";

// Robot's Environment - Grid Format
const WIDTH_CM = 200;
const HEIGHT_CM = 200;
export const GRID_BLOCK_SIZE_CM = 10; // *Size of each block in cm

export const GRID_TOTAL_WIDTH = WIDTH_CM / GRID_BLOCK_SIZE_CM; // 20
export const GRID_TOTAL_HEIGHT = HEIGHT_CM / GRID_BLOCK_SIZE_CM; // 20

// Obstacles
const OBSTACLE_WIDTH_CM = 10;
const OBSTACLE_HEIGHT_CM = 10;

export const OBSTACLE_GRID_WIDTH = OBSTACLE_WIDTH_CM / GRID_BLOCK_SIZE_CM; // 1
export const OBSTACLE_GRID_HEIGHT = OBSTACLE_HEIGHT_CM / GRID_BLOCK_SIZE_CM; // 1

// Robot's Footprint (Can be reduced according to measurements)
const ROBOT_WIDTH_CM = 30;
const ROBOT_HEIGHT_CM = 30;

export const ROBOT_GRID_WIDTH = ROBOT_WIDTH_CM / GRID_BLOCK_SIZE_CM; // 3
export const ROBOT_GRID_HEIGHT = ROBOT_HEIGHT_CM / GRID_BLOCK_SIZE_CM; // 3

export const ROBOT_INITIAL_POSITION: RobotPosition = {
  x: 1,
  y: 1,
  d: Direction.NORTH,
  s: null
};

// Grid Animation
export const GRID_ANIMATION_SPEED = 100; // in milli-seconds
