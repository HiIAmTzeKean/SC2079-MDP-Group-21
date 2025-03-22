import { Obstacle } from "../schemas/entity";
import {
	Basic_Mock,
	Basic_Corners,
	Basic_UTurn,
	Basic_ShapeV,
	Basic_CollisionCheckA,
	Basic_CollisionCheckB,
	Basic_CollisionCheckC,
} from "./basic";
import { Misc_Custom, Misc_TaskA5, Misc_FailTest } from "./misc";
import {
	Obstacles5_Basic,
	Obstacles5_BriefingSlides,
	Obstacles5_OfficialMockLayout,
	Obstacles5_A
} from "./obstacles_5";
import {
	Obstacles6_PastSem1,
	Obstacles6_A
} from "./obstacles_6";
import {
	Obstacles7_A,
	Obstacles7_B,
	Obstacles7_PastSem1,
	Obstacles7_PastSem2
} from "./obstacles_7";
import {
	Obstacles8_TightSpaces,
	Obstacles8_Long,
	Obstacles8_A,
	Obstacles8_B
} from "./obstacles_8";

/** Interface for Algorithm Test Data
 * @param obstacles An array of Obstacles.
 */
export interface AlgoTestDataInterface {
	obstacles: Obstacle[];
}

export enum AlgoTestEnum {
	Misc_Custom = "Custom",
	Misc_TaskA5 = "Task A5",
	Misc_FailTest = "Fail Test",

	Basic_Mock = "Basic Mock",
	Basic_UTurn = "Basic U-Turn",
	Basic_Corners = "Corners",
	Basic_ShapeV = "V Shape",
	Basic_CollisionCheckA = "Collision Checking (A)",
	Basic_CollisionCheckB = "Collision Checking (B)",
	Basic_CollisionCheckC = "Collision Checking (C)",

	Obstacles5_Basic = "5 Obstacles (Basic)",
	Obstacles5_BriefingSlides = "5 Obstacles (Briefing Slides)",
	Obstacles5_OfficialMockLayout = "5 Obstacles (Official Mock Layout)",
	Obstacles5_A = "5 Obstacles (A)",

	Obstacles6_PastSem1 = "6 Obstacles (Past Semester 1)",
	Obstacles6_A = "6 Obstacles (A)",

	Obstacles7_A = "7 Obstacles (A)",
	Obstacles7_B = "7 Obstacles (B)",
	Obstacles7_PastSem1 = "7 Obstacles (Past Semester 1)",
	Obstacles7_PastSem2 = "7 Obstacles (Past Semester 2)",

	Obstacles8_TightSpaces = "8 Obstacles (Tight Spaces)",
	Obstacles8_Long = "8 Obstacles (Long)",
	Obstacles8_A = "8 Obstacles (A)",
	Obstacles8_B = "8 Obstacles (B)",
}

export const AlgoTestEnumsList = [
	AlgoTestEnum.Misc_Custom,
	AlgoTestEnum.Misc_TaskA5,
	AlgoTestEnum.Misc_FailTest,

	AlgoTestEnum.Basic_Mock,
	AlgoTestEnum.Basic_UTurn,
	AlgoTestEnum.Basic_Corners,
	AlgoTestEnum.Basic_ShapeV,
	AlgoTestEnum.Basic_CollisionCheckA,
	AlgoTestEnum.Basic_CollisionCheckB,
	AlgoTestEnum.Basic_CollisionCheckC,

	AlgoTestEnum.Obstacles5_Basic,
	AlgoTestEnum.Obstacles5_BriefingSlides,
	AlgoTestEnum.Obstacles5_OfficialMockLayout,
	AlgoTestEnum.Obstacles5_A,

	AlgoTestEnum.Obstacles6_PastSem1,
	AlgoTestEnum.Obstacles6_A,

	AlgoTestEnum.Obstacles7_A,
	AlgoTestEnum.Obstacles7_B,
	AlgoTestEnum.Obstacles7_PastSem1,
	AlgoTestEnum.Obstacles7_PastSem2,

	AlgoTestEnum.Obstacles8_TightSpaces,
	AlgoTestEnum.Obstacles8_Long,
	AlgoTestEnum.Obstacles8_A,
	AlgoTestEnum.Obstacles8_B,
];

export const AlgoTestEnumMapper = {
	[AlgoTestEnum.Misc_Custom]: Misc_Custom,
	[AlgoTestEnum.Misc_TaskA5]: Misc_TaskA5,
	[AlgoTestEnum.Misc_FailTest]: Misc_FailTest,

	[AlgoTestEnum.Basic_Mock]: Basic_Mock,
	[AlgoTestEnum.Basic_UTurn]: Basic_UTurn,
	[AlgoTestEnum.Basic_Corners]: Basic_Corners,
	[AlgoTestEnum.Basic_ShapeV]: Basic_ShapeV,
	[AlgoTestEnum.Basic_CollisionCheckA]: Basic_CollisionCheckA,
	[AlgoTestEnum.Basic_CollisionCheckB]: Basic_CollisionCheckB,
	[AlgoTestEnum.Basic_CollisionCheckC]: Basic_CollisionCheckC,

	[AlgoTestEnum.Obstacles5_Basic]: Obstacles5_Basic,
	[AlgoTestEnum.Obstacles5_BriefingSlides]: Obstacles5_BriefingSlides,
	[AlgoTestEnum.Obstacles5_OfficialMockLayout]: Obstacles5_OfficialMockLayout,
	[AlgoTestEnum.Obstacles5_A]: Obstacles5_A,

	[AlgoTestEnum.Obstacles6_PastSem1]: Obstacles6_PastSem1,
	[AlgoTestEnum.Obstacles6_A]: Obstacles6_A,

	[AlgoTestEnum.Obstacles7_A]: Obstacles7_A,
	[AlgoTestEnum.Obstacles7_B]: Obstacles7_B,
	[AlgoTestEnum.Obstacles7_PastSem1]: Obstacles7_PastSem1,
	[AlgoTestEnum.Obstacles7_PastSem2]: Obstacles7_PastSem2,

	[AlgoTestEnum.Obstacles8_TightSpaces]: Obstacles8_TightSpaces,
	[AlgoTestEnum.Obstacles8_Long]: Obstacles8_Long,
	[AlgoTestEnum.Obstacles8_A]: Obstacles8_A,
	[AlgoTestEnum.Obstacles8_B]: Obstacles8_B,
};
