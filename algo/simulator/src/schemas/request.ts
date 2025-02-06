import { Obstacle, Position } from "./entity";

export interface AlgoInput {
  obstacles: Obstacle[];
  retrying: boolean;
  big_turn: number;
  robot_dir: number;
  robot_x: number;
  robot_y: number;
  num_runs: number;
};

export interface AlgoOutput {
  data: {
    commands: string[],
    distance: number,
    runtime: number,
    path: Position[],
  },
  error: string | null;
}
