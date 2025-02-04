import { Obstacle } from "./obstacle";

export interface AlgoInput {
  obstacles: Obstacle[];
  retrying: Boolean;
  big_turn: Number;
  robot_dir: Number;
  robot_x: Number;
  robot_y: Number;
};
