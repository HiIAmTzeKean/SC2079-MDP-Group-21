import React, { useEffect, useState } from "react";
import { NavigationGrid } from "./NavigationGrid";
import { CoreContainter } from "../CoreContainter";
import { Position } from "../../../schemas/entity";
import {
  GRID_ANIMATION_SPEED,
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

  // Algorithm Runtime & Cost
  const [algoRuntime, setAlgoRuntime] = useState<number | null>();
  const [algoCost, setAlgoCost] = useState<number | null>();

  // Select Tests
  const [selectedTestEnum, setSelectedTestEnum] = useState<AlgoTestEnum>(
    AlgoTestEnum.Basic_Mock
  );
  const [selectedTest, setSelectedTest] = useState<AlgoTestDataInterface>(
    AlgoTestEnumMapper[AlgoTestEnum.Basic_Mock]
  );

  // Select Tests
  useEffect(() => {
    const selectedTest = AlgoTestEnumMapper[selectedTestEnum];
    setSelectedTest(selectedTest);

    resetNavigationGrid();
  }, [selectedTestEnum]);

  const [isBigTurn, setIsBigTurn] = useState<boolean>(true);
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
      big_turn: isBigTurn ? 1 : 0,
      robot_dir: ROBOT_INITIAL_POSITION.d,
      robot_x: ROBOT_INITIAL_POSITION.x,
      robot_y: ROBOT_INITIAL_POSITION.y,
      num_runs: numberOfAlgoRuns
    };
    try {
      const algoOutput: AlgoOutput = await fetch.post(
        "/path",
        algoInput
      );
      setRobotPositions(algoOutput.data.path);
      setRobotCommands(algoOutput.data.commands);
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
  const [currentStep, setCurrentStep] = useState(0);
  const [currentRobotPosition, setCurrentRobotPosition] = useState<Position>();

  // Animation
  useEffect(() => {
    if (robotPositions && startAnimation && currentStep + 1 < totalSteps) {
      const timer = setTimeout(() => {
        const nextStep = currentStep + 1;
        setCurrentStep(nextStep);

        // Handle Scan Animation
        if (robotPositions[nextStep].s)
          toast.success("Image Scanned!");

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
        toast.success("Image Scanned!");

      setCurrentRobotPosition(robotPositions[currentStep]);

    }
  }, [currentStep, totalSteps, startAnimation, isManualAnimation]);

  const resetNavigationGrid = () => {
    setCurrentStep(0);
    setCurrentRobotPosition(ROBOT_INITIAL_POSITION);
    setRobotPositions(undefined);
    setRobotCommands(undefined);

    setAlgoRuntime(null);
    setAlgoCost(null);
  }

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

      {/* Algo input parameters Big Turn & Retrying*/}
      <div className="flex gap-8 items-center justify-center mb-4">
        <div
          className="flex gap-2 items-center justify-center cursor-pointer"
          onClick={() => {
            setIsBigTurn(!isBigTurn)
          }}
        >
          {isBigTurn
            ? <FaCheckSquare />
            : <FaSquare />
          }
          Big Turn
        </div>
        <div
          className="flex gap-2 items-center justify-center cursor-pointer"
          onClick={() => {
            setIsRetrying(!isRetrying)
          }}
        >
          {isRetrying
            ? <FaCheckSquare />
            : <FaSquare />
          }
          Retrying
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
              setNumberOfAlgoRuns(Math.round(Number(e.target.value)));
            }}
            value={numberOfAlgoRuns}
          />
          <label>times</label>
        </div>
      </div>

      {/* Algo Runtime */}
      {robotPositions && algoRuntime && algoCost &&
        <div className="flex flex-col justify-center items-center">
          <div className="">
            Average Runtime:&nbsp;
            <span className="font-bold">{algoRuntime}</span>&nbsp;
            s
          </div>
          <div className="">
            Average Cost:&nbsp;
            <span className="font-bold">{algoCost}</span>&nbsp;
            units
          </div>
        </div>
      }

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
            <span>{startAnimation ? "Stop Animation" : "Start Animation"}</span>
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
                if (!startAnimation && currentStep + 1 < totalSteps) {
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
        robotPosition={currentRobotPosition ?? ROBOT_INITIAL_POSITION}
        robotPath={robotPositions?.slice(0, currentStep + 1)}
        obstacles={selectedTest.obstacles}
        canAddObstacle={selectedTestEnum === AlgoTestEnum.Custom}
        setSelectedTest={setSelectedTest}
      />

      {robotCommands &&
        <div className="flex justify-center">
          <div className="w-[500px] text-center">
            <span className="font-bold">Commands:</span>
            {robotCommands?.map((command, index) => (
              <span key={index} className="block">{index + 1}. {command}</span>
            ))}
          </div>
        </div>}
    </CoreContainter>
  );
};
