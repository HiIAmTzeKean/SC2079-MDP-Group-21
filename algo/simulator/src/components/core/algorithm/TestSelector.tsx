import React, { useState } from "react";
import { Button, ModalContainer } from "../../common";
import { SiSpeedtest } from "react-icons/si";
import {
  FaCheckSquare,
  FaSquare,
} from "react-icons/fa";
import {
  AlgoTestDataInterface,
  AlgoTestEnum,
  AlgoTestEnumsList,
} from "../../../tests/algorithm";
import { CustomTest } from "./CustomTest";

interface TestSelectorProps {
  selectedTestEnum: AlgoTestEnum;
  setSelectedTestEnum: React.Dispatch<React.SetStateAction<AlgoTestEnum>>;
  selectedTest: AlgoTestDataInterface; // For Managing Custom Obstacles
  setSelectedTest: React.Dispatch<React.SetStateAction<AlgoTestDataInterface>>; // For Managing Custom Obstacles
  setAlgoRuntime: React.Dispatch<string>; // For reseting AlgoRuntime when changing the test
}

export const TestSelector = (props: TestSelectorProps) => {
  const {
    selectedTestEnum,
    setSelectedTestEnum,
    selectedTest,
    setSelectedTest,
    setAlgoRuntime,
  } = props;

  const [isTestModalOpen, setIsTestModalOpen] = useState(false);

  return (
    <div className="mt-2 mb-4 flex justify-center items-center gap-2">
      {/* Button */}
      <Button onClick={() => setIsTestModalOpen(true)}>
        <span>Select Test - {selectedTestEnum}</span>
        <SiSpeedtest className="w-[18px] h-[18px]" />
      </Button>

      {/* Manage Custom Obstacles */}
      {selectedTestEnum === AlgoTestEnum.Custom &&
        <CustomTest
          selectedTest={selectedTest}
          setSelectedTest={setSelectedTest}
        />
      }

      {/* Test Modal */}
      {isTestModalOpen && (
        <ModalContainer title="Tests" onClose={() => setIsTestModalOpen(false)}>
          <div className="flex flex-col items-start gap-2">
            {AlgoTestEnumsList.map((algoTest) => (
              <TestItem
                key={algoTest}
                test={algoTest}
                isSelected={algoTest === selectedTestEnum}
                setSelectedTestEnum={setSelectedTestEnum}
                setIsTestModalOpen={setIsTestModalOpen}
                setAlgoRuntime={setAlgoRuntime}
              />
            ))}
          </div>
        </ModalContainer>
      )}
    </div>
  );
};

interface TestItemProps {
  test: AlgoTestEnum;
  isSelected?: boolean;
  setSelectedTestEnum: React.Dispatch<React.SetStateAction<AlgoTestEnum>>;
  setIsTestModalOpen: React.Dispatch<React.SetStateAction<boolean>>;
  setAlgoRuntime: React.Dispatch<string>; // For reseting AlgoRuntime when changing the test
}

const TestItem = (props: TestItemProps) => {
  const {
    test,
    isSelected = false,
    setSelectedTestEnum,
    setIsTestModalOpen,
    setAlgoRuntime,
  } = props;

  return (
    <div
      className="group/test flex gap-2 items-center justify-center cursor-pointer"
      onClick={() => {
        setSelectedTestEnum(test);
        setIsTestModalOpen(false);
        setAlgoRuntime("");
      }}
    >
      {isSelected ? (
        <FaCheckSquare />
      ) : (
        <>
          <FaCheckSquare className="hidden group-hover/test:inline" />
          <FaSquare className="inline group-hover/test:hidden" />
        </>
      )}
      <div
        className={`${isSelected && "font-bold"} group-hover/test:font-bold`}
      >
        {test}
      </div>
    </div>
  );
};
