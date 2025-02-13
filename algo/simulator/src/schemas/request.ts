import { Obstacle, Position } from "./entity";

export interface AlgoInput {
	obstacles: Obstacle[];
	retrying: boolean;
	robot_dir: number;
	robot_x: number;
	robot_y: number;
	num_runs: number;
}

export interface AlgoOutput {
	data: {
		commands: string[];
		distance: number;
		runtime: number;
		path: Position[];
		motions: string[];
	};
	error: string | null;
}
