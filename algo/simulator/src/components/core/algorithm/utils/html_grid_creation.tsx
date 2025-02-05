import {
  GRID_TOTAL_HEIGHT,
  GRID_TOTAL_WIDTH,
  ROBOT_GRID_HEIGHT,
  ROBOT_GRID_WIDTH,
} from "../../../../constants";
import { Obstacle, Direction, Position } from "../../../../schemas/entity";

/**
 * Creates a HTML Grid.
 * @abstract This function will look at the state of the cell and style it accordingly. E.g.: Empty cell vs Cell with Robot.
 * @returns React.ReactNode[][] - `<td />[][]`
 * */
export const createHTMLGrid = (
  robotPosition: Position,
  obstacles: Obstacle[],
  canAddObstacle: boolean,
  handleAddObstacle: (x: number, y: number, d: number) => void,
  handleChangeDirection: (x: number, y: number, new_d: number) => void
) => {
  const grid: React.ReactNode[][] = [];

  for (let y = GRID_TOTAL_HEIGHT - 1; y >= 0; y--) {
    const currentRow: React.ReactNode[] = [];

    for (let x = 0; x < GRID_TOTAL_WIDTH; x++) {
      // Cell Contains Robot.
      if (isRobotCell(robotPosition, x, y))
        currentRow.push(
          createHTMLGridCellRobot(
            x,
            y,
            x ===
              robotPosition.x +
              convertRobotThetaToCameraOffsetBlock(robotPosition.d)[0] &&
              y ===
              robotPosition.y +
              convertRobotThetaToCameraOffsetBlock(robotPosition.d)[1]
              ? "camera"
              : "body"
          )
        );
      // Cell Contains an Obstacle
      else if (
        obstacles.filter((obstacle) => obstacle.x === x && obstacle.y === y)
          .length > 0
      ) {
        currentRow.push(
          createHTMLGridCellObstacle(
            x,
            y,
            obstacles.filter(
              (obstacle) => obstacle.x === x && obstacle.y === y
            )[0].d,
            canAddObstacle,
            handleChangeDirection
          )
        );
      }
      // Empty Cell
      else
        currentRow.push(
          createHTMLGridCellEmpty(x, y, canAddObstacle, handleAddObstacle)
        );
    }
    grid.push(currentRow);
  }
  return grid;
};

// ---------- Helper Functions - HTML ---------- //
/**
 * Creates a `<td />` for an empty cell
 * @used_by createHTMLGrid()
 */
const createHTMLGridCellEmpty = (
  x: number,
  y: number,
  canAddObstacle: boolean,
  handleAddObstacle: (x: number, y: number, d: number) => void
) => {
  if (!canAddObstacle) {
    return (
      <td id={`cell-${x}-${y}`} className="border border-orange-900 w-8 h-8" />
    );
  }

  return (
    <td
      id={`cell-${x}-${y}`}
      className="border border-orange-900 w-8 h-8 cursor-pointer hover:bg-amber-400 hover:border-t-4 hover:border-t-red-700"
      onClick={() => handleAddObstacle(x, y, 1)} // Default North Facing
      title="Add obstacle"
    />
  );
};

/**
 * Creates a `<td />` for a cell that contains the Robot's body
 * @used_by createHTMLGrid()
 */
const createHTMLGridCellRobot = (
  x: number,
  y: number,
  type: "camera" | "body"
) => {
  return (
    <td
      id={`cell-${x}-${y}`}
      className={`border-2 border-orange-900 w-8 h-8 align-middle text-center ${type === "body" ? "bg-green-300" : "bg-blue-400"
        }`}
    />
  );
};

/**
 * Creates a `<td />` for a cell that contains an Obstacle
 * @used_by createHTMLGrid()
 */
const createHTMLGridCellObstacle = (
  x: number,
  y: number,
  direction: Direction,
  canChangeDirection: boolean,
  handleChangeDirection: (x: number, y: number, new_d: number) => void
) => {
  let imageFaceBorderClassName = "";
  switch (direction) {
    case Direction.NORTH:
      imageFaceBorderClassName = "border-t-4 border-t-red-700";
      break;
    case Direction.SOUTH:
      imageFaceBorderClassName = "border-b-4 border-b-red-700";
      break;
    case Direction.EAST:
      imageFaceBorderClassName = "border-r-4 border-r-red-700";
      break;
    case Direction.WEST:
      imageFaceBorderClassName = "border-l-4 border-l-red-700";
      break;
  }

  if (!canChangeDirection) {
    return (
      <td
        id={`cell-${x}-${y}`}
        className={`border border-orange-900 w-8 h-8 align-middle text-center bg-amber-400 ${imageFaceBorderClassName}`}
      />
    );
  }

  return (
    <td
      id={`cell-${x}-${y}`}
      className={`border border-orange-900 w-8 h-8 align-middle text-center bg-amber-400 ${imageFaceBorderClassName} cursor-pointer hover:bg-amber-500`}
      title="Change obstacle direction"
      onClick={() =>
        handleChangeDirection(x, y, (direction.valueOf() % 4) + 1)
      }
    />
  );
};

/** Adds x-axis and y-axis labels to the Grid */
export const addHTMLGridLables = (grid: React.ReactNode[][]) => {
  grid.forEach((row, index) =>
    row.unshift(
      <td className="font-bold pr-2">{GRID_TOTAL_HEIGHT - index - 1}</td>
    )
  );

  const gridColumnLabels: React.ReactNode[] = [];
  for (let c = -1; c < GRID_TOTAL_WIDTH; c++) {
    if (c === -1) gridColumnLabels.push(<td />);
    else
      gridColumnLabels.push(
        <td className="font-bold pt-2 text-center">{c}</td>
      );
  }
  grid.push(gridColumnLabels);
  return grid;
};

// ---------- Helper Functions - Calculations ---------- //

/**
 * Used Center of Robot's Body as Robot's current (x, y) position.
 * @returns (x, y) offset of the robot's camera from the center of the robot
 */
export const convertRobotThetaToCameraOffsetBlock = (direction: Direction) => {
  // East
  if (direction === Direction.EAST) {
    return [1, 0];
  }
  // North
  else if (direction === Direction.NORTH) {
    return [0, 1];
  }
  // West
  else if (direction === Direction.WEST) {
    return [-1, 0];
  }
  // South
  else if (direction === Direction.SOUTH) {
    return [0, -1];
  }
  return [0, 0];
};

/**
 * Checks if current cell is occupied by a Robot based on it's (x, y) position and facing.
 * @location
 */
export const isRobotCell = (
  robotPosition: Position,
  cell_x: number,
  cell_y: number
) => {
  return (
    robotPosition.x - (ROBOT_GRID_WIDTH - 1) / 2 <= cell_x &&
    cell_x <= robotPosition.x + (ROBOT_GRID_WIDTH - 1) / 2 &&
    robotPosition.y - (ROBOT_GRID_HEIGHT - 1) / 2 <= cell_y &&
    cell_y <= robotPosition.y + (ROBOT_GRID_HEIGHT - 1) / 2
  )
};
