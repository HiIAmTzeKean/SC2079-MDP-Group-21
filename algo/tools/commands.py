from algo.tools.movement import Motion
from algo.entities.entity import Obstacle
from algo.tools.consts import OFFSET, OBSTACLE_SIZE, W_COMMAND_FLAG

"""
Generate commands in format requested by STM (refer to commands_FLAGS.h in STM repo): 
    "{flag}{speed}|{angle}|{val}\n"

    <speed>: 1-3 chars
    - specify speed to drive, from 0 to 100 (integer).

    <angle>: 1+ chars, in degrees
    - specify angle to steer, from -25 to 25 (float).
    - negative angle: steer left, positive angle: steer right.

    <val>: 1+ chars, in cm
    - specify distance to drive, from 0 to 500 (float).
    - (ONLY FOR DIST_TARGET commands) when <angle> != 0: specify turn angle to complete, from 0 to 360 (float).

        e.g., to drive forward at speed 50 for 30cm going straight: 'T50|0|30\n'
        e.g., to drive backward at speed 20 until 5cm away while wheels are steering left 10 degrees: 'w20|-10|5\n'
"""


class CommandGenerator:
    # commented flags are unused

    # FULL_STOP = 'S'                 # bring car to a complete stop
    SEP = "|"
    END = "\n"
    # RCV = 'r'
    FIN = 'FIN'
    # INFO_MARKER = 'M'              # signal command has been passed. (used for tracking)
    # INFO_DIST = 'D'                # signal start/stop of accumulative distance tracking

    # Flags
    FORWARD_DIST_TARGET = "T"       # go forward for a target distance/angle.
    FORWARD_DIST_AWAY = "W"         # go forward until within a certain distance away from obstacle (more accurate than target dist, within 50cm range)
    BACKWARD_DIST_TARGET = "t"      # go backward for a target distance/angle.
    BACKWARD_DIST_AWAY = "w"        # go backward until a certain distance away from obstacle (more accurate than target dist, within 50cm range)

    # # IR Sensors based motion
    # FORWARD_IR_DIST_L = "L"         # go forward until left IR sensor is greater than value provided.
    # FORWARD_IR_DIST_R = "R"         # go forward until right IR sensor is greater than value provided.
    # BACKWARD_IR_DIST_L = "l"        # go backward until left IR sensor is greater than value provided.
    # BACKWARD_IR_DIST_R = "r"        # go backward until right IR sensor is greater than value provided.

    # unit distance
    UNIT_DIST: float = 10

    def __init__(self, straight_speed: int = 50, turn_speed: int = 30) -> None:
        """
        A class to generate commands for the robot to follow

        range of speed: 0-100
        """
        self.straight_speed: int = straight_speed
        self.turn_speed: int = turn_speed

    def _generate_command(self, motion: Motion, num_motions: int = 1) -> list[str]:
        """Generates movement commands based on motion type. 

        Tune accordingly to the robot's hardware. 
        Ideally the tuning should be on STM side, but if that is not feasible then tuning on algo side can be done.

        Args:
            motion (Motion): Type of motion to execute.
            num_motions (int, optional): Number of repeated motions. Defaults to 1.

        Returns:
            list[str]: List of command strings.
        """
        if num_motions > 1:
            # straight-line motions can be combined into 1 command
            dist = num_motions * self.UNIT_DIST
        else:
            dist = self.UNIT_DIST

        if motion == Motion.FORWARD:
            return [f"T{self.straight_speed}|{0}|{dist}"]
        elif motion == Motion.REVERSE:
            # return [f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{self.SEP}{0}{self.SEP}{dist}"]

            # Servo tends to drift left when reversing so we force it to the right every 20cm intervals
            realign_cmds = [
                f"T{25}|{30}|{0.1}",
            ]
            cmds = []
            # Re-align servo every 20cm
            for _ in range(dist // 20):
                cmds.append(
                    f"t{35}|{0}|{20}")
                cmds.extend(realign_cmds)

            remaining_dist = dist % 20
            if remaining_dist > 0:
                cmds.append(
                    f"t{35}|{0}|{remaining_dist}")
                # Re-align servo only for distances >= 5cm
                if remaining_dist >= 5:
                    cmds.extend(realign_cmds)
            return cmds

        # TODO tune commands according to actual robot's hardware.
        # commented out commands were the desired movement but because of hardware limitations we had to add additional commands to compensate
        # we tuned our turns to use 3 point turns (turn 45 degrees, reverse, turn 45 degrees again)
        elif motion == Motion.FORWARD_LEFT_TURN:
            # return [f"T{self.turn_speed}|{-25}|{90}"]
            return [
                f"T{30}|{-50}|{46}",
                f"t{25}|{0}|{23}",
                f"T{30}|{-50}|{45.5}",
                # turn right on the spot to re-align servo after left turn
                f"T{25}|{10}|{0.1}",
                f"t{25}|{0}|{3}"
            ]
        elif motion == Motion.FORWARD_RIGHT_TURN:
            # return [f"T{self.turn_speed}|{25}|{90}"]
            return [
                f"T{30}|{50}|{46}",
                f"t{25}|{0}|{20}",
                f"T{30}|{50}|{45.7}",
                f"t{25}|{0}|{4}",
            ]
        elif motion == Motion.REVERSE_LEFT_TURN:
            # return [f"t{self.turn_speed}|{-25}|{90}"]
            return [
                f"T{25}|{0}|{3}",
                f"t{30}|{-50}|{46}",
                f"T{25}|{0}|{22}",
                f"t{30}|{-50}|{46.5}",
                # turn right on the spot to re-align servo after left turn
                f"T{25}|{10}|{0.1}"
            ]
        elif motion == Motion.REVERSE_RIGHT_TURN:
            # return [f"t{self.turn_speed}|{25}|{90}"]
            return [
                f"T{25}|{0}|{6}",
                f"t{30}|{48}|{45.4}",
                f"T{25}|{0}|{14}",
                f"t{30}|{48}|{45.5}"
            ]
        else:
            raise ValueError(
                f"Invalid motion {motion}. This should never happen.")

    def _generate_away_command(self, view_state, obstacle: Obstacle) -> list[str]:
        """
            Generate commands to calibrate robot position before scanning obstacle
        """
        # dist btw obstacle & view state position - offset since sensor is at front of car - obstacle size + extra clearance if needed
        CLEARANCE = 0.3

        unit_dist_from_obstacle = max(
            abs(view_state.x - obstacle.x),
            abs(view_state.y - obstacle.y)
        ) - OFFSET - OBSTACLE_SIZE + CLEARANCE
        dist_away = int(unit_dist_from_obstacle * self.UNIT_DIST)
        return [f"{self.FORWARD_DIST_AWAY}{self.straight_speed}{self.SEP}{0}{self.SEP}{dist_away}",
                f"{self.BACKWARD_DIST_AWAY}{self.straight_speed}{self.SEP}{0}{self.SEP}{dist_away}"]

    def generate_commands(self, motions: list[Motion], obstacle_id_with_signals: list[str], scanned_obstacles: list[Obstacle], optimal_path) -> list[str]:
        """
        Generate commands based on the list of motions
        """
        if not motions:
            return []
        view_states = [
            position for position in optimal_path if position.screenshot_id != None]
        commands: list[str] = []
        prev_motion: Motion = motions[0]
        num_motions: int = 1
        snap_count: int = 0
        for motion in motions[1:]:
            # if combinable motions
            if motion == prev_motion and motion.is_combinable():
                # increment the number of combined motions
                num_motions += 1
            # convert prev motion to command
            else:
                if prev_motion == Motion.CAPTURE:
                    if (
                        W_COMMAND_FLAG
                        # only use w/W commands when robot is directly in front center of obstacle
                        and "C" in obstacle_id_with_signals[snap_count]
                    ):
                        commands.extend(
                            self._generate_away_command(
                                view_states[snap_count], scanned_obstacles[snap_count])
                        )
                    commands.append(
                        f"SNAP{obstacle_id_with_signals[snap_count]}")
                    snap_count += 1
                    prev_motion = motion
                    continue
                else:
                    cur_cmd = self._generate_command(prev_motion, num_motions)
                commands.extend(cur_cmd)
                num_motions = 1  # reset since new motion
            prev_motion = motion

        # add the last command
        if prev_motion == Motion.CAPTURE:
            if (
                W_COMMAND_FLAG
                # only use w/W commands when robot is directly in front center of obstacle
                and "C" in obstacle_id_with_signals[snap_count]
            ):
                commands.extend(
                    self._generate_away_command(
                        view_states[snap_count], scanned_obstacles[snap_count])
                )
            commands.append(
                f"SNAP{obstacle_id_with_signals[snap_count]}")
        else:
            cur_cmd = self._generate_command(prev_motion, num_motions)
            commands.extend(cur_cmd)

        # add the final command
        commands.append(f"{self.FIN}")
        return commands
