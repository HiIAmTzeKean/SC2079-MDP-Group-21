import { Obstacle } from "../../schemas/entity";
import { AlgoTestBasicMock } from "./basic_mock";
import { AlgoTestBasicUTurn } from "./basic_u_turn";
import { AlgoTestCorners } from "./corners";
import { AlgoTestCustom } from "./custom";
import { AlgoTestObstacles_5_Basic } from "./obstacles_5";
import { AlgoTestObstacles_7_A, AlgoTestObstacles_7_B } from "./obstacles_7";
import { AlgoTestShapes_V } from "./shapes";
import {
	AlgoTestCollisionCheck_A,
	AlgoTestCollisionCheck_B,
	AlgoTestCollisionCheck_C,
} from "./collision_check";
import { AlgoTestOfficialMockLayout } from "./official_mock_layout";

/** Interface for Algorithm Test Data
 * @param obstacles An array of Obstacles.
 */
export interface AlgoTestDataInterface {
	obstacles: Obstacle[];
}

export enum AlgoTestEnum {
	Custom = "Custom",
	Basic_Mock = "Basic Mock",
	Basic_U_Turn = "Basic U-Turn",
	Corners = "Corners",
	Obstacles_7_A = "7 Obstacles (A)",
	Obstacles_7_B = "7 Obstacles (B)",
	Shapes_V = "V Shape",
	Obstacles_5_Basic = "5 Obstacles (Basic)",
	AlgoTestCollisionCheck_A = "Collision Checking (A)",
	AlgoTestCollisionCheck_B = "Collision Checking (B)",
	AlgoTestCollisionCheck_C = "Collision Checking (C)",
	AlgoTestOfficialMockLayout = "Official Mock Layout",
}

export const AlgoTestEnumsList = [
	AlgoTestEnum.Custom,
	AlgoTestEnum.Basic_Mock,
	AlgoTestEnum.Basic_U_Turn,
	AlgoTestEnum.Corners,
	AlgoTestEnum.Obstacles_7_A,
	AlgoTestEnum.Obstacles_7_B,
	AlgoTestEnum.Shapes_V,
	AlgoTestEnum.Obstacles_5_Basic,
	AlgoTestEnum.AlgoTestCollisionCheck_A,
	AlgoTestEnum.AlgoTestCollisionCheck_B,
	AlgoTestEnum.AlgoTestCollisionCheck_C,
	AlgoTestEnum.AlgoTestOfficialMockLayout,
];

export const AlgoTestEnumMapper = {
	[AlgoTestEnum.Custom]: AlgoTestCustom,
	[AlgoTestEnum.Basic_Mock]: AlgoTestBasicMock,
	[AlgoTestEnum.Basic_U_Turn]: AlgoTestBasicUTurn,
	[AlgoTestEnum.Corners]: AlgoTestCorners,
	[AlgoTestEnum.Obstacles_7_A]: AlgoTestObstacles_7_A,
	[AlgoTestEnum.Obstacles_7_B]: AlgoTestObstacles_7_B,
	[AlgoTestEnum.Shapes_V]: AlgoTestShapes_V,
	[AlgoTestEnum.Obstacles_5_Basic]: AlgoTestObstacles_5_Basic,
	[AlgoTestEnum.AlgoTestCollisionCheck_A]: AlgoTestCollisionCheck_A,
	[AlgoTestEnum.AlgoTestCollisionCheck_B]: AlgoTestCollisionCheck_B,
	[AlgoTestEnum.AlgoTestCollisionCheck_C]: AlgoTestCollisionCheck_C,
	[AlgoTestEnum.AlgoTestOfficialMockLayout]: AlgoTestOfficialMockLayout,
};
