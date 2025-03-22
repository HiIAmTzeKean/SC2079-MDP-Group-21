import React, { useEffect, useState } from "react";
import { NavigationGrid } from "./NavigationGrid";
import { Direction, Position } from "../../schemas/entity";
import {
	GRID_ANIMATION_SPEED,
	GRID_TOTAL_WIDTH,
	ROBOT_INITIAL_POSITION,
} from "../../constants";
import {
	FaCheckSquare,
	FaChevronLeft,
	FaChevronRight,
	FaPause,
	FaPlay,
	FaSitemap,
	FaSpinner,
	FaSquare,
	FaList, // List Icon for Test All Button
} from "react-icons/fa";
import {
	AlgoTestDataInterface,
	AlgoTestEnum,
	AlgoTestEnumMapper,
	AlgoTestEnumsList, // List of all test enum values for iterating
} from "../../tests";
import { Button } from "../common";
import toast from "react-hot-toast";
import { TestSelector } from "./TestSelector";
import { ServerStatus } from "./ServerStatus";
import useFetch from "../../hooks/useFetch";
import { AlgoInput, AlgoOutput } from "../../schemas/request";

// Intraface to store test results for each test case
interface TestResult {
	testName: string;
	runtime: number;
	cost: number;
	success: boolean;
	obstaclesScanned: number;
	totalObstacles: number;
}

export const AlgorithmMenu = () => {
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
		AlgoTestEnum.Misc_Custom
	);
	const [selectedTest, setSelectedTest] = useState<AlgoTestDataInterface>(
		AlgoTestEnumMapper[AlgoTestEnum.Misc_Custom]
	);

	// state variables for Test All Results
	const [testAllResults, setTestAllResults] = useState<TestResult[]>([]);
	const [isTestingAll, setIsTestingAll] = useState<boolean>(false);
	const [showTestResults, setShowTestResults] = useState<boolean>(false);

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

	// Check if all obstacles were scanned in the path
	const checkAllObstaclesScanned = (path: Position[], obstacles: any[]): { scanned: number, total: number } => {
		// Collect all obstacle IDs in the path that were scanned
		const scannedIDs = new Set<string>();
		// Check each position in the path
		path.forEach(pos => {
			if (pos.s) {
				// If there's a scan value, add it to scanned IDs
				scannedIDs.add(pos.s);
			}
		});

		return {
			scanned: scannedIDs.size,
			total: obstacles.length
		};
	};

	// Run Algorithm for a specific test case
	const runAlgorithmForTest = async (testEnum: AlgoTestEnum): Promise<TestResult | null> => {
		const test = AlgoTestEnumMapper[testEnum]; // Get test data for the specified enum

		// Set up algorithm input with test case obstacles and default robot position
		const algoInput: AlgoInput = {
			obstacles: test.obstacles.map((o) => {
				return {
					id: o.id,
					x: o.x,
					y: o.y,
					d: o.d,
				};
			}),
			retrying: isRetrying,
			robot_dir: ROBOT_INITIAL_POSITION.d,
			robot_x: ROBOT_INITIAL_POSITION.x,
			robot_y: ROBOT_INITIAL_POSITION.y,
			num_runs: numberOfAlgoRuns,
		};

		try {
			const algoOutput: AlgoOutput = await fetch.post("/simulator_path", algoInput);

			// Check if all obstacles were scanned
			const scanResult = checkAllObstaclesScanned(algoOutput.data.path, test.obstacles);
			const allObstaclesScanned = scanResult.scanned === scanResult.total;

			return {
				testName: testEnum,
				runtime: algoOutput.data.runtime,
				cost: algoOutput.data.distance,
				success: allObstaclesScanned, // Only successful if all obstacles scanned
				obstaclesScanned: scanResult.scanned,
				totalObstacles: scanResult.total
			};
		} catch (e) {
			return {
				testName: testEnum,
				runtime: 0,
				cost: 0,
				success: false,
				obstaclesScanned: 0,
				totalObstacles: test.obstacles.length
			};
		}
	};

	// Run Algorithm on all test cases
	const handleTestAll = async () => {
		if (isAlgorithmLoading || isTestingAll) return;

		setIsTestingAll(true);
		setShowTestResults(true);
		setTestAllResults([]);

		const results: TestResult[] = [];
		let completedTests = 0;
		const totalTests = AlgoTestEnumsList.length;

		toast.success("Starting to test all algorithm test cases...");

		// Iterate through all test cases
		for (const testEnum of AlgoTestEnumsList) {
			// Skip Custom test
			if (testEnum === AlgoTestEnum.Misc_Custom) {
				completedTests++;
				continue;
			}

			// Show loading for current test case
			toast.loading(`Testing ${testEnum} (${completedTests + 1}/${totalTests})...`,
				{ id: `test-${testEnum}` });

			// Run algorithm for the current test case	
			const result = await runAlgorithmForTest(testEnum);
			if (result) {
				results.push(result);
				if (result.success) {
					toast.success(`Completed ${testEnum}`, { id: `test-${testEnum}` });
				} else if (result.obstaclesScanned > 0) {
					toast.error(`Partial scan in ${testEnum}: ${result.obstaclesScanned}/${result.totalObstacles}`, { id: `test-${testEnum}` });
				} else {
					toast.error(`Failed ${testEnum}`, { id: `test-${testEnum}` });
				}
			} else {
				toast.error(`Failed ${testEnum}`, { id: `test-${testEnum}` });
			}

			completedTests++;
		}

		// Update state with all test results and reset flags
		setTestAllResults(results);
		setIsTestingAll(false);
		toast.success("Completed testing all algorithm test cases!");
	};

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

			// Check if all obstacles were scanned
			const scanResult = checkAllObstaclesScanned(algoOutput.data.path, selectedTest.obstacles);
			if (scanResult.scanned === scanResult.total) {
				toast.success("Algorithm ran successfully. All obstacles scanned!");
			} else {
				toast.error(`Algorithm ran, but only scanned ${scanResult.scanned}/${scanResult.total} obstacles.`);
			}
		} catch (e) {
			toast.error("Failed to run algorithm. Server Error: " + e);
		}

		setIsAlgorithmLoading(false);
	};

	// Animation
	const [isManualAnimation, setIsManualAnimation] = useState(false);
	const [startAnimation, setStartAnimation] = useState(false);
	const [currentStep, setCurrentStep] = useState(-1);
	const [currentRobotPosition, setCurrentRobotPosition] = useState<Position>();
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
		} else if ( // User manually click through the steps
			robotPositions &&
			isManualAnimation &&
			currentStep < totalSteps
		) {
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

	return (
		<div className="flex flex-col justify-center items-center my-2">
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
			{/* <div className="flex gap-8 items-center justify-center mb-4">
				<div
					className="flex gap-2 items-center justify-center cursor-pointer"
					onClick={() => {
						setIsRetrying(!isRetrying);
					}}
				>
					{isRetrying ? <FaCheckSquare /> : <FaSquare />}
					Retrying (WIP, currently does nothing)
				</div>
			</div> */}

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
				<Button
					onClick={isTestingAll || isAlgorithmLoading ? undefined : handleTestAll}
				>
					<span>Test All Cases</span>
					{isTestingAll ? (
						<FaSpinner className="animate-spin" />
					) : (
						<FaList className="text-[18px]" />
					)}
				</Button>
				{/* Toggle button to show/hide test results */}
				{testAllResults.length > 0 && (
					<Button
						onClick={() => setShowTestResults(!showTestResults)}
					>
						<span>{showTestResults ? 'Hide Results' : 'Show Results'}</span>
					</Button>
				)}
			</div>

			{/* Test results table */}
			{showTestResults && testAllResults.length > 0 && (
				<div className="mb-4 p-4 border rounded">
					<h3 className="text-center font-bold text-lg mb-2">Test Results</h3>
					<div className="max-h-64 overflow-y-auto">
						<table className="w-full border-collapse">
							<thead>
								<tr className="bg-gray-100">
									<th className="border p-2 text-left">Test Case</th>
									<th className="border p-2 text-right">Runtime (s)</th>
									<th className="border p-2 text-right">Cost</th>
									<th className="border p-2 text-center">Status</th>
								</tr>
							</thead>
							<tbody>
								{testAllResults.map((result, index) => (
									<tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : ''}>
										<td className="border p-2">{result.testName}</td>
										<td className="border p-2 text-right">{result.runtime.toFixed(2)}</td>
										<td className="border p-2 text-right">{result.cost.toFixed(2)}</td>
										<td className="border p-2 text-center">
											{result.success ? (
												<span className="text-green-600 font-bold">Success</span>
											) : (
												<span className="text-red-600 font-bold">Failed</span>
											)}
										</td>
									</tr>
								))}
							</tbody>
						</table>
					</div>
				</div>
			)}

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

			{/* Navigation Grid */}
			<NavigationGrid
				robotPosition={currentRobotPosition ?? robotStartPosition}
				robotPath={robotPositions?.slice(0, currentStep + 1)}
				obstacles={selectedTest.obstacles}
				canAddObstacle={selectedTestEnum === AlgoTestEnum.Misc_Custom}
				setSelectedTest={setSelectedTest}
			/>

			<div className="flex justify-center gap-8">
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
		</div>
	);
};
