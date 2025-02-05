import { Obstacle, Position } from "./entity";

export interface AlgoInput {
  obstacles: Obstacle[];
  retrying: boolean;
  big_turn: number;
  robot_dir: number;
  robot_x: number;
  robot_y: number;
};

export interface AlgoOutput {
  data: {
    commands: string[],
    distance: number,
    path: Position[],
  },
  error: string | null;
}
