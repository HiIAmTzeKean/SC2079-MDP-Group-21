import React, { useEffect, useState } from "react";
import { NavigationGrid } from "./NavigationGrid";
import { CoreContainter } from "../CoreContainter";
import { Direction, Position } from "../../../schemas/entity";
import {
	GRID_ANIMATION_SPEED,
	GRID_TOTAL_WIDTH,
	ROBOT_INITIAL_POSITION,
} from "../../../constants";
import {
	FaCheckSquare,
	FaChevronLeft,
	FaChevronRight,
	FaPause,
	FaPlay,
	FaSitemap,
	FaSpinner,
	FaSquare,
} from "react-icons/fa";
import {
	AlgoTestDataInterface,
	AlgoTestEnum,
	AlgoTestEnumMapper,
} from "../../../tests/algorithm";
import { Button } from "../../common";
import toast from "react-hot-toast";
import { TestSelector } from "./TestSelector";
import { ServerStatus } from "./ServerStatus";
import useFetch from "../../../hooks/useFetch";
import { AlgoInput, AlgoOutput } from "../../../schemas/request";

export const AlgorithmCore = () => {
	const fetch = useFetch();

	// Robot's Positions
	const [robotPositions, setRobotPositions] = useState<Position[]>();
	const totalSteps = robotPositions?.length ?? 0;
	const [robotCommands, setRobotCommands] = useState<string[]>();
	const [robotMotions, setRobotMotions] = useState<string[]>();

	// Robot Starting Position	
	const [robotStartPosition, setRobotStartPosition] = useState<Position>(ROBOT_INITIAL_POSITION);
	const [robotStartX, setRobotStartX] = useState<number>(ROBOT_INITIAL_POSITION.x);
	const [robotStartY, setRobotStartY] = useState<number>(ROBOT_INITIAL_POSITION.y);
	const [robotStartDirection, setRobotStartDirection] = useState<Direction>(ROBOT_INITIAL_POSITION.d);

	const validateRobotPosition = (input: string) => {
		const number = Math.round(Number(input));
		if (number > GRID_TOTAL_WIDTH - 1) {
			return GRID_TOTAL_WIDTH - 1;
		} else if (number < 0) {
			return 0;
		} else {
			return number;
		}
	}

	useEffect(() => {
		const newPosition: Position = {
			x: robotStartX,
			y: robotStartY,
			d: robotStartDirection,
			s: null
		}
		setRobotStartPosition(newPosition);
		setCurrentRobotPosition(newPosition);
	}, [robotStartX, robotStartY, robotStartDirection]);

	// Algorithm Runtime & Cost
	const [algoRuntime, setAlgoRuntime] = useState<number | null>();
	const [algoCost, setAlgoCost] = useState<number | null>();

	// Select Tests
	const [selectedTestEnum, setSelectedTestEnum] = useState<AlgoTestEnum>(
		AlgoTestEnum.Custom
	);
	const [selectedTest, setSelectedTest] = useState<AlgoTestDataInterface>(
		AlgoTestEnumMapper[AlgoTestEnum.Custom]
	);

	// Select Tests
	useEffect(() => {
		const selectedTest = AlgoTestEnumMapper[selectedTestEnum];
		setSelectedTest(selectedTest);

		resetNavigationGrid();
	}, [selectedTestEnum]);

	const [isRetrying, setIsRetrying] = useState<boolean>(false);

	// Run Algorithm
	const [isAlgorithmLoading, setIsAlgorithmLoading] = useState(false);
	const [numberOfAlgoRuns, setNumberOfAlgoRuns] = useState<number>(1);

	// Run Algorithm
	const handleRunAlgorithm = async () => {
		if (startAnimation === true || isAlgorithmLoading === true) return;
		resetNavigationGrid();
		setIsAlgorithmLoading(true);

		const algoInput: AlgoInput = {
			obstacles: selectedTest.obstacles.map((o) => {
				return {
					id: o.id,
					x: o.x,
					y: o.y,
					d: o.d,
				};
			}),
			retrying: isRetrying,
			robot_dir: robotStartPosition.d,
			robot_x: robotStartPosition.x,
			robot_y: robotStartPosition.y,
			num_runs: numberOfAlgoRuns,
		};
		try {
			const algoOutput: AlgoOutput = await fetch.post("/simulator_path", algoInput);
			setRobotPositions(algoOutput.data.path);
			setRobotCommands(algoOutput.data.commands);
			setRobotMotions(algoOutput.data.motions);
			setCurrentStep(0);

			setAlgoRuntime(algoOutput.data.runtime);
			setAlgoCost(algoOutput.data.distance);
			toast.success("Algorithm ran successfully.");
		} catch (e) {
			toast.error("Failed to run algorithm. Server Error: " + e);
		}

		setIsAlgorithmLoading(false);
	};

	// Animation
	const [isManualAnimation, setIsManualAnimation] = useState(false);
	const [startAnimation, setStartAnimation] = useState(false);
	const [currentStep, setCurrentStep] = useState(-1);
	const [currentRobotPosition, setCurrentRobotPosition] =
		useState<Position>();

	// Animation
	useEffect(() => {
		if (robotPositions && startAnimation && currentStep + 1 < totalSteps) {
			const timer = setTimeout(() => {
				const nextStep = currentStep + 1;
				setCurrentStep(nextStep);

				// Handle Scan Animation
				if (robotPositions[nextStep].s)
					toast.success(
						`Image Scanned! ${robotPositions[nextStep].s}`
					);

				setCurrentRobotPosition(robotPositions[nextStep]);

				// Stop Animation at the last step
				if (nextStep === totalSteps - 1) {
					setStartAnimation(false);
				}
			}, GRID_ANIMATION_SPEED);
			return () => clearTimeout(timer);
		} else if (
			robotPositions &&
			isManualAnimation &&
			currentStep < totalSteps
		) {
			// User manually click through the steps
			// Handle Scan Animation
			if (robotPositions[currentStep].s)
				toast.success(
					`Image Scanned! ${robotPositions[currentStep].s}`
				);

			setCurrentRobotPosition(robotPositions[currentStep]);
		}
	}, [currentStep, totalSteps, startAnimation, isManualAnimation]);

	const resetNavigationGrid = () => {
		setCurrentStep(-1);
		setCurrentRobotPosition(robotStartPosition);
		setRobotPositions(undefined);
		setRobotCommands(undefined);
		setRobotMotions(undefined);

		setAlgoRuntime(null);
		setAlgoCost(null);
	};

	// TODO: FOR DEBUGGING, remove when done. to directly send commands to STM
	const [commandsInput, setCommandsInput] = useState<string>("");
	const [commandsOutput, setCommandsOutput] = useState<string>("");
	const convertToSTMCommands = () => {
		if (commandsInput === "") {
			setCommandsOutput("");
			return;
		}

		const commandsList: string[] = JSON.parse(commandsInput);
		let STMCommands = "";
		STMCommands += "stm_link = STMLink()\nstm_link.connect()\n";
		for (const cmd of commandsList) {
			if (cmd === "FIN" || cmd.startsWith("SNAP")) continue;

			const flag = cmd[0];
			const [speed, angle, val] = cmd.slice(1).split("|");
			STMCommands += `stm_link.send_cmd("${flag}",${speed},${angle},${val})\nstm_link.recv()\n`;
		}
		setCommandsOutput(STMCommands);
	};

	// TODO: REFACTOR!!! cleanup this magic spaghetti
	const [currentCommands, setCurrentCommands] = useState<string[]>([]);
	useEffect(() => {
		if (!robotCommands || !robotMotions) return;

		let mergedCommands: string[] = [];
		let currentGroup: string[] = [];
		// merge commands for the same motion
		robotCommands.forEach((command) => {
			if (command.startsWith('W') || command.startsWith('w') || command.startsWith('SNAP') || command === 'FIN') {
				// If it starts with W, w, SNAP or is FIN, group it
				currentGroup.push(command);
			} else {
				// If there is an ongoing group, merge it and push to the final result
				if (currentGroup.length > 0) {
					mergedCommands.push(currentGroup.join(' '));
					currentGroup = [];  // Reset the group
				}
				mergedCommands.push(command);  // Add the non-group command
			}
		});
		// If there's any remaining group, add it to the result
		if (currentGroup.length > 0) {
			mergedCommands.push(currentGroup.join(' '));
		}
		console.log(mergedCommands);


		// TODO: refactor to switch statement for ALL possible motions for easy change when there are extra commands for a motion after tuning
		let result: string[] = [
			"", // no motion at first robot position
			`${mergedCommands[0]} (${robotMotions[0]})` // first motion
		];
		let cmdPtr = 0;
		let prevMotion = robotMotions[0];

		for (let i = 1; i < robotMotions.length; i++) {
			const motion = robotMotions[i];
			const nextMotion = robotMotions[i + 1];

			if (motion == "CAPTURE") {
				prevMotion = motion;
				continue;
			}

			// continue with same FORWARD/REVERSE motion
			if (
				["FORWARD", "REVERSE"].includes(motion) &&
				motion === prevMotion
			) {
				if (nextMotion === "CAPTURE") {
					result.push(`${mergedCommands[cmdPtr]} (${motion}), ${mergedCommands[cmdPtr + 1]} (${nextMotion})`);
					cmdPtr += 1; // skip over CAPTURE commands
				}
				else {
					result.push(`${mergedCommands[cmdPtr]} (${motion})`);
				}
				prevMotion = motion;
				continue;
			}

			if (nextMotion === "CAPTURE") {
				cmdPtr += 1; // new command
				if (motion.includes("OFFSET")) {
					// OFFSET comes in 2 commands
					result.push(`${mergedCommands[cmdPtr]} ${mergedCommands[cmdPtr + 1]} (${motion}), ${mergedCommands[cmdPtr + 2]} (${nextMotion})`);
					cmdPtr += 2 // skip over extra OFFSET command & CAPTURE commands
				}
				else {
					result.push(`${mergedCommands[cmdPtr]} (${motion}), ${mergedCommands[cmdPtr + 1]} (${nextMotion})`);
					cmdPtr += 1 // skip over CAPTURE commands
				}
				prevMotion = motion;
				continue;
			}

			if (motion.includes("OFFSET")) {
				cmdPtr += 1; // new command
				// OFFSET comes in 2 commands
				result.push(`${mergedCommands[cmdPtr]} ${mergedCommands[cmdPtr + 1]} (${motion})`);
				cmdPtr += 1; // skip over extra OFFSET command
				prevMotion = motion;
				continue;
			}

			// handle other motions
			cmdPtr += 1; // new command
			result.push(`${mergedCommands[cmdPtr]} (${motion})`);
			prevMotion = motion;
		}
		setCurrentCommands(result);
	}, [robotMotions]);

	return (
		<CoreContainter title="Algorithm Simulator">
			{/* Server Status */}
			<ServerStatus />

			{/* Select Tests */}
			<TestSelector
				selectedTestEnum={selectedTestEnum}
				setSelectedTestEnum={setSelectedTestEnum}
				selectedTest={selectedTest}
				setSelectedTest={setSelectedTest}
			/>

			<div className="flex gap-8 mb-4 items-center">
				<span className="font-bold">Robot Start Position</span>
				<div>
					<label className="font-bold">X: </label>
					<input
						type="number"
						min={1}
						max={18}
						value={robotStartX}
						onChange={(e) => {
							setRobotStartX(validateRobotPosition(e.target.value))
						}}
						step={1}
						className="rounded-lg"
					/>
				</div>
				<div>
					<label className="font-bold">Y: </label>
					<input
						type="number"
						min={1}
						max={18}
						value={robotStartY}
						onChange={(e) => {
							setRobotStartY(validateRobotPosition(e.target.value))
						}}
						step={1}
						className="rounded-lg"
					/>
				</div>
				<div>
					<label className="font-bold">D: </label>
					<select
						value={robotStartDirection}
						onChange={(e) => {
							setRobotStartDirection(Number(e.target.value) as Direction)
						}}
					>
						<option value={Direction.NORTH}>NORTH</option>
						<option value={Direction.EAST}>EAST</option>
						<option value={Direction.SOUTH}>SOUTH</option>
						<option value={Direction.WEST}>WEST</option>
					</select>
				</div>
			</div>

			{/* TODO: Algo input parameters Retrying*/}
			<div className="flex gap-8 items-center justify-center mb-4">
				<div
					className="flex gap-2 items-center justify-center cursor-pointer"
					onClick={() => {
						setIsRetrying(!isRetrying);
					}}
				>
					{isRetrying ? <FaCheckSquare /> : <FaSquare />}
					Retrying (WIP, currently does nothing)
				</div>
			</div>

			{/* Run Algo N times*/}
			<div className="mb-4 flex justify-center items-center gap-8">
				<Button onClick={handleRunAlgorithm}>
					<span>Run Algorithm</span>
					{isAlgorithmLoading ? (
						<FaSpinner className="animate-spin" />
					) : (
						<FaSitemap className="text-[18px]" />
					)}
				</Button>
				<div className="flex justify-center items-center gap-2">
					<input
						className="w-20"
						type="number"
						min={1}
						onChange={(e) => {
							setNumberOfAlgoRuns(
								Math.round(Number(e.target.value))
							);
						}}
						value={numberOfAlgoRuns}
					/>
					<label>times</label>
				</div>
			</div>

			{/* Algo Runtime */}
			{robotPositions && algoRuntime && algoCost ? (
				<div className="flex flex-col justify-center items-center">
					<div className="">
						Average Runtime:&nbsp;
						<span className="font-bold">{algoRuntime}</span>&nbsp; s
					</div>
					<div className="">
						Average Cost:&nbsp;
						<span className="font-bold">{algoCost}</span>&nbsp;
						units
					</div>
				</div>
			) : null}

			{/* Animation */}
			{robotPositions && (
				<div className="mt-2 mb-4 flex flex-col justify-center items-center gap-2">
					{/* Start Animation */}
					<Button
						onClick={() => {
							if (startAnimation) {
								// Stop Animation
								setStartAnimation(false);
							} else {
								// Start Animation
								setIsManualAnimation(false);
								setStartAnimation(true);
								if (currentStep === totalSteps - 1) {
									setCurrentRobotPosition(robotPositions[0]);
									setCurrentStep(0);
								}
							}
						}}
					>
						<span>
							{startAnimation
								? "Stop Animation"
								: "Start Animation"}
						</span>
						{startAnimation ? <FaPause /> : <FaPlay />}
					</Button>

					{/* Slider */}
					<label
						htmlFor="steps-range"
						className="font-bold text-[14px] flex gap-2 items-center"
					>
						<FaChevronLeft
							className="cursor-pointer"
							onClick={() => {
								if (!startAnimation && currentStep - 1 >= 0) {
									setIsManualAnimation(true);
									setCurrentStep((prev) => prev - 1);
								}
							}}
						/>
						<span>
							Step: {currentStep + 1} / {totalSteps}
						</span>
						<FaChevronRight
							className="cursor-pointer"
							onClick={() => {
								if (
									!startAnimation &&
									currentStep + 1 < totalSteps
								) {
									setIsManualAnimation(true);
									setCurrentStep((prev) => prev + 1);
								}
							}}
						/>
					</label>
					<input
						id="steps-range"
						type="range"
						min={0}
						max={totalSteps - 1}
						value={currentStep}
						onChange={(e) => {
							setCurrentStep(Number(e.target.value));
							setIsManualAnimation(true);
						}}
						onPointerUp={() => setIsManualAnimation(false)}
						step={1}
						className="w-1/2 h-2 bg-gray-900 rounded-lg appearance-none cursor-pointer"
						disabled={startAnimation === true}
					/>
				</div>
			)}

			{/* Current Command */}
			{currentStep && currentCommands.length > 0 ? (
				<div className="mt-2 mb-4 flex flex-col justify-center items-center">
					<span className="font-bold">Command (Motion):</span>
					<span>{currentCommands[currentStep]}</span>
				</div>
			) : null
			}

			{/* Navigation Grid */}
			<NavigationGrid
				robotPosition={currentRobotPosition ?? robotStartPosition}
				robotPath={robotPositions?.slice(0, currentStep + 1)}
				obstacles={selectedTest.obstacles}
				canAddObstacle={selectedTestEnum === AlgoTestEnum.Custom}
				setSelectedTest={setSelectedTest}
			/>

			<div className="flex justify-between gap-8">
				<div className="flex flex-col gap-2">
					<span>Input list of command strings (in RPI format):</span>
					<textarea
						className="w-[400px] h-[200px]"
						value={commandsInput}
						onChange={(e) => setCommandsInput(e.target.value)}
					/>
					<Button onClick={() => convertToSTMCommands()}>
						Convert to STM commands
					</Button>
					<pre>{commandsOutput}</pre>
				</div>

				{robotCommands && (
					<div className="text-center">
						<span className="font-bold">Commands:</span>
						{robotCommands?.map((command, index) => (
							<span key={index} className="block">
								{index + 1}. {command}
							</span>
						))}
					</div>
				)}
			</div>
		</CoreContainter >
	);
};
