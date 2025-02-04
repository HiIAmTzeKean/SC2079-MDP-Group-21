import { Obstacle } from "./obstacle";

export interface AlgoInput {
  cat: "obstacles";
  value: {
    obstacles: Obstacle[];
    mode: 0; // 0: Task 1
  };
  server_mode: "simulator";
}
