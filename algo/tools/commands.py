from tools.movement import Motion

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
    # FORWARD_DIST_AWAY = "W"         # go forward until within a certain distance.
    BACKWARD_DIST_TARGET = "t"      # go backward for a target distance/angle.
    # BACKWARD_DIST_AWAY = "w"        # go backward until a certain distance apart.

    # # IR Sensors based motion
    # FORWARD_IR_DIST_L = "L"         # go forward until left IR sensor is greater than value provided.
    # FORWARD_IR_DIST_R = "R"         # go forward until right IR sensor is greater than value provided.
    # BACKWARD_IR_DIST_L = "l"        # go backward until left IR sensor is greater than value provided.
    # BACKWARD_IR_DIST_R = "r"        # go backward until right IR sensor is greater than value provided.

    # unit distance
    UNIT_DIST = 10

    # # turn angles
    # FORWARD_TURN_ANGLE = 20
    # BACKWARD_TURN_ANGLE = 18

    def __init__(self, straight_speed: int = 50, turn_speed: int = 50):
        """
        A class to generate commands for the robot to follow

        range of speed: 0-100
        """
        self.straight_speed = straight_speed
        self.turn_speed = turn_speed

    def _generate_command(self, motion: Motion, num_motions: int = 1):
        if num_motions > 1:
            dist = num_motions * self.UNIT_DIST
            angle = num_motions * 90
        else:
            dist = self.UNIT_DIST
            angle = 90

        if motion == Motion.FORWARD:
            return [f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{self.SEP}0{self.SEP}{dist}{self.END}"]
        elif motion == Motion.REVERSE:
            return [f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{self.SEP}0{self.SEP}{dist}{self.END}"]

        elif motion == Motion.FORWARD_LEFT_TURN:
            return [f"{self.FORWARD_DIST_TARGET}{self.turn_speed}{self.SEP}-23{self.SEP}{angle}{self.END}"]
        elif motion == Motion.FORWARD_RIGHT_TURN:
            return [f"{self.FORWARD_DIST_TARGET}{self.turn_speed}{self.SEP}23{self.SEP}{angle}{self.END}"]
        elif motion == Motion.REVERSE_LEFT_TURN:
            return [f"{self.BACKWARD_DIST_TARGET}{self.turn_speed}{self.SEP}-23{self.SEP}{angle}{self.END}"]
        elif motion == Motion.REVERSE_RIGHT_TURN:
            return [f"{self.BACKWARD_DIST_TARGET}{self.turn_speed}{self.SEP}23{self.SEP}{angle}{self.END}"]

        # cannot combine with other motions
        elif motion == Motion.FORWARD_OFFSET_LEFT:
            # break it down into 2 steps
            cmd1 = f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{
                self.SEP}-23{self.SEP}{45}{self.END}"
            cmd2 = f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{
                self.SEP}23{self.SEP}{45}{self.END}"
        elif motion == Motion.FORWARD_OFFSET_RIGHT:
            # break it down into 2 steps
            cmd1 = f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{
                self.SEP}23{self.SEP}{45}{self.END}"
            cmd2 = f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{
                self.SEP}-23{self.SEP}{45}{self.END}"
        elif motion == Motion.REVERSE_OFFSET_LEFT:
            # break it down into 2 steps
            cmd1 = f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{
                self.SEP}-25{self.SEP}{45}{self.END}"
            cmd2 = f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{
                self.SEP}25{self.SEP}{45}{self.END}"
        elif motion == Motion.REVERSE_OFFSET_RIGHT:
            # break it down into 2 steps
            cmd1 = f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{
                self.SEP}25{self.SEP}{45}{self.END}"
            cmd2 = f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{
                self.SEP}-25{self.SEP}{45}{self.END}"
        else:
            raise ValueError(f"Invalid motion {
                             motion}. This should never happen.")
        return [cmd1, cmd2]

    def generate_commands(self, motions):
        """
        Generate commands based on the list of motions
        """
        if not motions:
            return []
        commands = []
        prev_motion = motions[0]
        num_motions = 1
        for motion in motions[1:]:
            # if combinable motions
            if motion == prev_motion and motion.is_combinable():
                # increment the number of combined motions
                num_motions += 1
            # convert prev motion to command
            else:
                if prev_motion == Motion.CAPTURE:
                    commands.append(f"SNAP")
                    prev_motion = motion
                    continue
                else:
                    cur_cmd = self._generate_command(prev_motion, num_motions)
                commands.extend(cur_cmd)
                num_motions = 1

            prev_motion = motion

        # add the last command
        if prev_motion == Motion.CAPTURE:
            commands.append(f"SNAP_C")
        else:
            cur_cmd = self._generate_command(prev_motion, num_motions)
            commands.extend(cur_cmd)

        # add the final command
        commands.append(f"{self.FIN}")
        return commands
