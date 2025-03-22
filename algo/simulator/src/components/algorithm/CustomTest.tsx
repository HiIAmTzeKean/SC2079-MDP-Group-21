import React, { useState } from "react";
import { Button, ModalContainer } from "../common";
import { FaBox, FaPlus, FaRecycle, FaTrash } from "react-icons/fa";
import { MdDelete } from "react-icons/md";
import {
    AlgoTestDataInterface,
} from "../../tests";
import {
    Obstacle,
    Direction,
    DirectionStringMapping,
} from "../../schemas/entity";
import toast from "react-hot-toast";
import { GRID_TOTAL_HEIGHT, GRID_TOTAL_WIDTH, OBSTACLE_GRID_PADDING, ROBOT_GRID_HEIGHT, ROBOT_GRID_WIDTH, ROBOT_INITIAL_POSITION } from "../../constants";

interface CustomTestProps {
    selectedTest: AlgoTestDataInterface;
    setSelectedTest: React.Dispatch<React.SetStateAction<AlgoTestDataInterface>>;
}

export const CustomTest = (props: CustomTestProps) => {
    const {
        selectedTest,
        setSelectedTest,
    } = props;

    // Custom Obstacle
    const [isManageObstaclesModalOpen, setIsManageObstaclesModalOpen] =
        useState(false);
    const [customObstacle_X, setCustomObstacle_X] = useState<number>(0);
    const [customObstacle_Y, setCustomObstacle_Y] = useState<number>(0);
    const [customObstacle_Direction, setCustomObstacle_Direction] =
        useState<Direction>(Direction.NORTH);
    const handleAddCustomObstacle = () => {
        // Check that cell is not occupied by Robot
        if (
            0 <= customObstacle_X &&
            customObstacle_X <= ROBOT_GRID_WIDTH - 1 &&
            0 <= customObstacle_Y &&
            customObstacle_Y <= ROBOT_GRID_HEIGHT - 1
        ) {
            return toast.error("Cell is occupied by the Robot!");
        }
        // Check that cell is not occupied by existing Obstacle
        if (
            selectedTest.obstacles.filter(
                (o) => o.x === customObstacle_X && o.y === customObstacle_Y
            ).length > 0
        ) {
            toast.error("Placing multiple obstacles on the same cell! Please manually edit the direction in 'Manage Obstacles'.");
        }

        const updated = {
            obstacles: [
                ...selectedTest.obstacles,
                {
                    id: selectedTest.obstacles.length + 1,
                    x: customObstacle_X,
                    y: customObstacle_Y,
                    d: customObstacle_Direction,
                },
            ],
        };
        setSelectedTest(updated);
    };

    const handleClearAllObstacles = () => {
        setSelectedTest({ obstacles: [] });
    }

    // ensure obstacles are not placed too close to each other or the boundaries
    const getForbiddenCells = (obstacleCell: { x: number, y: number }) => {
        const forbiddenArea = new Set<{ x: number, y: number }>();
        for (let i = -OBSTACLE_GRID_PADDING; i <= OBSTACLE_GRID_PADDING; i++) {
            for (let j = -OBSTACLE_GRID_PADDING; j <= OBSTACLE_GRID_PADDING; j++) {
                const x = obstacleCell.x + i;
                const y = obstacleCell.y + j;
                if (0 <= x && x < GRID_TOTAL_WIDTH && 0 <= y && y < GRID_TOTAL_HEIGHT) {
                    forbiddenArea.add({ x, y })
                }
            }
        }
        return forbiddenArea;
    }

    const [numberOfRandomObstacles, setNumberOfRandomObstacles] = useState<number>(1)
    // NOTE: some unreachable obstacles may still be generated especially since we do not account for direction
    const handleGenerateRandomObstacles = () => {
        const directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST];

        const forbiddenCells: Set<{ x: number, y: number }> = getForbiddenCells(
            { x: ROBOT_INITIAL_POSITION.x, y: ROBOT_INITIAL_POSITION.y }
        );

        const obstacles: Obstacle[] = Array.from({ length: numberOfRandomObstacles }, (_, i) => {
            let x: number, y: number;

            do {
                // random int in the range [padding, GRID_TOTAL_WIDTH - padding - 1] inclusive
                x = Math.floor(Math.random() * (GRID_TOTAL_WIDTH - 2 * OBSTACLE_GRID_PADDING));
                y = Math.floor(Math.random() * (GRID_TOTAL_HEIGHT - 2 * OBSTACLE_GRID_PADDING));
            } while (Array.from(forbiddenCells).some((cell) => cell.x === x && cell.y === y));
            // create forbidden area for new obstacle
            getForbiddenCells({ x, y }).forEach(cell => forbiddenCells.add(cell))

            const d = directions[Math.floor(Math.random() * directions.length)];
            return { x, y, id: i + 1, d };
        });

        setSelectedTest({ obstacles });
    };

    const validateObstaclePosition = (input: string) => {
        const number = Math.round(Number(input));
        if (number > GRID_TOTAL_WIDTH - 1) {
            return GRID_TOTAL_WIDTH - 1;
        } else if (number < 0) {
            return 0;
        } else {
            return number;
        }
    };

    return (
        <div>
            {/* Manage Custom Obstacles */}
            <div className="flex items-center justify-center gap-2">
                <Button onClick={() => setIsManageObstaclesModalOpen(true)}>
                    <span>Manage Obstacles</span>
                    <FaBox />
                </Button>
                <span className="w-40 text-center">
                    Click on grid cell to add obstacle or change direction
                </span>
            </div>


            {/* Manage Custom Obstacles Modal */}
            {isManageObstaclesModalOpen && (
                <ModalContainer
                    title="Manage Obstacles"
                    onClose={() => setIsManageObstaclesModalOpen(false)}
                >
                    {/* Generate Random Obstacles */}

                    <div className="flex gap-2 mb-4 align-center justify-center">
                        <Button
                            onClick={() => handleGenerateRandomObstacles()}>
                            <span>Generate Random Obstacles</span>
                            <FaRecycle />
                        </Button>
                        <input
                            id="steps-range"
                            type="range"
                            min={1}
                            max={8}
                            value={numberOfRandomObstacles}
                            onChange={(e) => {
                                setNumberOfRandomObstacles(Number(e.target.value));
                            }}
                            step={1}
                            className="h-2 w-10 bg-gray-900 rounded-lg appearance-none cursor-pointer self-center"
                        />
                        <label className="self-center font-bold">
                            {numberOfRandomObstacles}
                        </label>
                    </div>


                    <div className="flex flex-col justify-center items-start">
                        {/* Obstacles List with Delete */}
                        {selectedTest.obstacles.map((obstacle) => (
                            <CustomObstacleItem
                                obstacle={obstacle}
                                setSelectedTest={setSelectedTest}
                            />
                        ))}

                        {/* Add Obstacle */}
                        <div className="w-full flex flex-col justify-center items-center mt-4">
                            {/* Title */}
                            <div className="font-bold text-[18px] mb-2">
                                - Add Obstacles -
                            </div>

                            {/* X */}
                            <div className="flex gap-2 items-center my-2">
                                <label className="font-bold">X: </label>
                                <input
                                    type="number"
                                    min={0}
                                    max={19}
                                    value={customObstacle_X}
                                    onChange={(e) => {
                                        setCustomObstacle_X(
                                            validateObstaclePosition(
                                                e.target.value
                                            )
                                        );
                                    }}
                                    step={1}
                                    className="rounded-lg"
                                />
                            </div>

                            {/* Y */}
                            <div className="flex gap-2 items-center mb-4">
                                <label className="font-bold">Y: </label>
                                <input
                                    type="number"
                                    min={0}
                                    max={19}
                                    value={customObstacle_Y}
                                    onChange={(e) => {
                                        setCustomObstacle_Y(
                                            validateObstaclePosition(
                                                e.target.value
                                            )
                                        );
                                    }}
                                    step={1}
                                    className="rounded-lg"
                                />
                            </div>

                            {/* Direction */}
                            <div className="flex gap-2 items-center mb-4">
                                <label className="font-bold">Direction: </label>
                                <Button
                                    className={`${customObstacle_Direction === Direction.NORTH &&
                                        "!text-gray-300"
                                        }`}
                                    onClick={() =>
                                        setCustomObstacle_Direction(Direction.NORTH)
                                    }
                                >
                                    N ↑
                                </Button>
                                <Button
                                    className={`${customObstacle_Direction === Direction.SOUTH &&
                                        "!text-gray-300"
                                        }`}
                                    onClick={() =>
                                        setCustomObstacle_Direction(Direction.SOUTH)
                                    }
                                >
                                    S ↓
                                </Button>
                                <Button
                                    className={`${customObstacle_Direction === Direction.EAST &&
                                        "!text-gray-300"
                                        }`}
                                    onClick={() =>
                                        setCustomObstacle_Direction(Direction.EAST)
                                    }
                                >
                                    E →
                                </Button>
                                <Button
                                    className={`${customObstacle_Direction === Direction.WEST &&
                                        "!text-gray-300"
                                        }`}
                                    onClick={() =>
                                        setCustomObstacle_Direction(Direction.WEST)
                                    }
                                >
                                    W ←
                                </Button>
                                <Button
                                    className={`${customObstacle_Direction === Direction.SKIP &&
                                        "!text-gray-300"
                                        }`}
                                    onClick={() =>
                                        setCustomObstacle_Direction(Direction.SKIP)
                                    }
                                >
                                    SKIP
                                </Button>
                            </div>

                            <div className="flex flex-col gap-4 items-center">
                                {/* Add Obstacle Button */}
                                <Button onClick={handleAddCustomObstacle}>
                                    <span>Add</span>
                                    <FaPlus />
                                </Button>

                                {/* Add Obstacle Button */}
                                <Button className="bg-red-600" onClick={handleClearAllObstacles}>
                                    <span>Clear All</span>
                                    <FaTrash />
                                </Button>
                            </div>
                        </div>
                    </div>
                </ModalContainer>
            )}
        </div>
    );
};

interface CustomObstacleItemProps {
    obstacle: Obstacle;
    setSelectedTest: React.Dispatch<React.SetStateAction<AlgoTestDataInterface>>;
}

const CustomObstacleItem = (props: CustomObstacleItemProps) => {
    const { setSelectedTest, obstacle } = props;
    const { x, y, d, id } = obstacle;

    const handleRemoveObstacle = () => {
        setSelectedTest((prev) => {
            const cleanedObstacles = prev.obstacles.filter(
                (o) => !(o.id === obstacle.id)
            )
                .map((o, index) => ({ ...o, id: index + 1 })); // reassign IDs starting from 1

            return {
                obstacles: cleanedObstacles,
            };
        });
    };

    return (
        <div className="flex items-center w-full gap-2 font-bold">
            <span>{id}.</span>
            <span>X: {x},</span>
            <span>Y: {y},</span>
            <span>Face: {DirectionStringMapping[d]}</span>
            <div className="flex-1 flex justify-end">
                <MdDelete
                    title="Remove"
                    className="text-[20px] hover:text-red-600 cursor-pointer"
                    onClick={handleRemoveObstacle}
                />
            </div>
        </div>
    );
};
