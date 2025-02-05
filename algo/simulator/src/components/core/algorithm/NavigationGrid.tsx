import { Position, Obstacle, Direction } from "../../../schemas/entity";
import { GRID_TOTAL_HEIGHT, GRID_TOTAL_WIDTH, ROBOT_ACTUAL_GRID_HEIGHT, ROBOT_ACTUAL_GRID_WIDTH, ROBOT_GRID_HEIGHT, ROBOT_GRID_WIDTH } from "../../../constants";
import { AlgoTestDataInterface } from "../../../tests/algorithm";

interface NavigationGridProps {
  robotPosition: Position;
  obstacles: Obstacle[];
  canAddObstacle: boolean;
  setSelectedTest: React.Dispatch<React.SetStateAction<AlgoTestDataInterface>>;
}

export const NavigationGrid = (props: NavigationGridProps) => {
  const { robotPosition, obstacles, canAddObstacle, setSelectedTest } = props;

  const cellSize = 40;
  const offset = 40; // offset due to spacing taken up by axis labels

  const robotFootprintX = robotPosition.x * cellSize;
  const robotFootprintY = GRID_TOTAL_HEIGHT * cellSize - (robotPosition.y + 1) * cellSize - offset;
  const robotWidth = ROBOT_ACTUAL_GRID_WIDTH * cellSize;
  const robotHeight = ROBOT_ACTUAL_GRID_HEIGHT * cellSize;
  const robotCenterX = robotFootprintX + (cellSize * ROBOT_GRID_WIDTH - robotWidth) / 2;
  const robotCenterY = robotFootprintY + (cellSize * ROBOT_GRID_HEIGHT - robotHeight) / 2;

  const getDirectionRotationAngle = (direction: Direction) => {
    switch (direction) {
      case Direction.NORTH:
        return 0
      case Direction.EAST:
        return 90
      case Direction.SOUTH:
        return 180
      case Direction.WEST:
        return 270
      default:
        return null
    }
  }

  const robotAngle = getDirectionRotationAngle(robotPosition.d);

  const handleAddObstacle = (x: number, y: number, d: number) => {
    setSelectedTest((prev) => {
      const updated = {
        obstacles: [
          ...prev.obstacles,
          {
            id: prev.obstacles.length,
            x: x,
            y: y,
            d: d,
          },
        ],
      };
      return updated;
    });
  };

  const handleChangeDirection = (
    x: number,
    y: number,
    d: number
  ) => {
    setSelectedTest((prev) => {
      const directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST, Direction.SKIP];
      const new_d = directions[(directions.indexOf(d) + 1) % directions.length]

      const updatedObstacles = prev.obstacles.map((obstacle) =>
        obstacle.x === x && obstacle.y === y
          ? { ...obstacle, d: new_d }  // update direction of selected obstacle
          : obstacle
      );

      return { obstacles: updatedObstacles };
    });
  };


  return (
    <svg width={GRID_TOTAL_WIDTH * cellSize + offset} height={GRID_TOTAL_HEIGHT * cellSize + offset}>
      {/* Draw column labels (X-axis) */}
      {Array.from({ length: GRID_TOTAL_WIDTH }).map((_, col) => (
        <text
          key={`col-${col}`}
          x={(col + 1) * cellSize + offset / 2}
          y={GRID_TOTAL_HEIGHT * cellSize + offset / 2}
          textAnchor="middle"
          alignmentBaseline="middle"
          fontSize="14"
          fill="black"
        >
          {col}
        </text>
      ))}

      {/* Draw row labels (Y-axis) */}
      {Array.from({ length: GRID_TOTAL_HEIGHT }).map((_, row) => (
        <text
          key={`row-${row}`}
          x={offset / 2}
          y={row * cellSize + offset / 2}
          textAnchor="middle"
          alignmentBaseline="middle"
          fontSize="14"
          fill="black"
        >
          {GRID_TOTAL_HEIGHT - row - 1}
        </text>
      ))}

      {/* Draw the grid */}
      {Array.from({ length: GRID_TOTAL_HEIGHT }).map((_, row) =>
        Array.from({ length: GRID_TOTAL_WIDTH }).map((_, col) => (
          <rect
            key={`${col}-${row}`}
            x={col * cellSize + offset}
            y={(GRID_TOTAL_HEIGHT - row - 1) * cellSize} // invert y-axis
            width={cellSize}
            height={cellSize}
            fill="white"
            stroke="black"
            onClick={() =>
              canAddObstacle ? handleAddObstacle(col, row, Direction.NORTH) : undefined
            }
          />
        ))
      )}

      {/* Draw Obstacles */}
      {obstacles.map((obstacle, index) => {
        const x = obstacle.x * cellSize + offset;
        const y = (GRID_TOTAL_HEIGHT - obstacle.y - 1) * cellSize;
        const angle = getDirectionRotationAngle(obstacle.d);

        return <rect
          key={index}
          x={x}
          y={y}
          width={cellSize}
          height={cellSize}
          fill="yellow"
          stroke={angle !== null ? "red" : undefined}
          stroke-width="5"
          stroke-dasharray={
            angle !== null ?
              `${cellSize}, ${GRID_TOTAL_WIDTH * cellSize}`
              : undefined
          } // by default stroke only at north side of rect
          transform={
            angle !== null ?
              `rotate(${angle} ${x + cellSize / 2} ${y + cellSize / 2})`
              : undefined
          } // rotate around rect center depending on direction
          onClick={() => canAddObstacle ? handleChangeDirection(obstacle.x, obstacle.y, obstacle.d) : undefined}
        />
      })}

      {/* Draw the Robot Footprint */}
      <rect
        x={robotFootprintX}
        y={robotFootprintY}
        width={cellSize * ROBOT_GRID_WIDTH}
        height={cellSize * ROBOT_GRID_HEIGHT}
        fill="blue"
        fillOpacity={0.5}
      />

      {/* Draw the Actual Robot */}
      <rect
        x={robotCenterX}
        y={robotCenterY}
        width={robotWidth}
        height={robotHeight}
        fill="black"
        fillOpacity={0.8}
        stroke={robotAngle !== null ? "red" : undefined}
        stroke-width="5"
        stroke-dasharray={robotAngle !== null ?
          `${robotWidth}, ${GRID_TOTAL_WIDTH * cellSize}` : undefined
        } // by default stroke only at north side of robot
        transform={
          robotAngle !== null ?
            `rotate(${robotAngle}  ${robotCenterX + robotWidth / 2} ${robotCenterY + robotHeight / 2})`
            : undefined
        } // rotate around rect center depending on direction
      />
    </svg>
  );
};
