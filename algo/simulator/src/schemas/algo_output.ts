import { RobotPosition } from "./robot";

export interface AlgoOutput {
  data: {
    commands: string[],
    distance: number,
    path: RobotPosition[],
  },
  error: string | null;
}