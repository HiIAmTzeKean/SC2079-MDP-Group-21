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
import { obstacles_5_BriefingSlides } from "./5 Obstacles- From Briefing Slide";
import { A5Task } from "./TaskA5";
import { Past_Semester_1 } from "./Past Semester 1";
import { Past_Semester_2 } from "./Past Semester 2";
import { obstacles8tightspaces } from "./8 Obstacles, tight spaces";
import { Past_Semester_3 } from "./Past Semester 3";
import { Obstacles_8_long } from "./8 Obstacles long";
import { FailTest } from "./Fail Test";






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
	obstacles_5_BriefingSlides = "5 Obstacles - From Briefing Slide",
	A5Task = "A5Task",
	Past_Semester_1 = "Past_Semester_1",
	Past_Semester_2 = "Past_Semester_2",
	obstacles8tightspaces = "8 Obstacles, tight spaces",
	Past_Semester_3 = "Past Semester 3",
	Obstacles_8_long = "8 Obstacles long",
	FailTest = "Fail Test",






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
	AlgoTestEnum.obstacles_5_BriefingSlides,
	AlgoTestEnum.A5Task,
	AlgoTestEnum.Past_Semester_1,
	AlgoTestEnum.Past_Semester_2,
	AlgoTestEnum.obstacles8tightspaces,
	AlgoTestEnum.Past_Semester_3,
	AlgoTestEnum.Obstacles_8_long,
	AlgoTestEnum.FailTest,





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
	[AlgoTestEnum.obstacles_5_BriefingSlides]: obstacles_5_BriefingSlides,
	[AlgoTestEnum.A5Task]: A5Task,
	[AlgoTestEnum.Past_Semester_1]: Past_Semester_1,
	[AlgoTestEnum.Past_Semester_2]: Past_Semester_2,
	[AlgoTestEnum.obstacles8tightspaces]: obstacles8tightspaces,
	[AlgoTestEnum.Past_Semester_3]: Past_Semester_3,
	[AlgoTestEnum.Obstacles_8_long]: Obstacles_8_long,
	[AlgoTestEnum.FailTest]: FailTest,



};
