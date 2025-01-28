from pickle import TUPLE

from tools.consts import WIDTH, HEIGHT, Direction, Motion


class CommandGenerator:
    SEP = "|"
    END = "\n"
    RCV = 'r'
    FIN = 'FIN'
    INFO_MARKER = 'M'
    INFO_DIST = 'D'

    # Flags
    FORWARD_DIST_TARGET = "T"
    FORWARD_DIST_AWAY = "W"
    BACKWARD_DIST_TARGET = "t"
    BACKWARD_DIST_AWAY = "w"

    # IR Sensors based motion
    FORWARD_IR_DIST_L = "L"
    FORWARD_IR_DIST_R = "R"
    BACKWARD_IR_DIST_L = "l"
    BACKWARD_IR_DIST_R = "r"

    # unit distance
    UNIT_DIST = 10

    # turn angles
    FORWARD_TURN_ANGLE = 20
    BACKWARD_TURN_ANGLE = 18

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
            cmd1 = f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{self.SEP}-23{self.SEP}{45}{self.END}"
            cmd2 = f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{self.SEP}23{self.SEP}{45}{self.END}"
        elif motion == Motion.FORWARD_OFFSET_RIGHT:
            # break it down into 2 steps
            cmd1 = f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{self.SEP}23{self.SEP}{45}{self.END}"
            cmd2 = f"{self.FORWARD_DIST_TARGET}{self.straight_speed}{self.SEP}-23{self.SEP}{45}{self.END}"
        elif motion == Motion.REVERSE_OFFSET_LEFT:
            # break it down into 2 steps
            cmd1 = f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{self.SEP}-25{self.SEP}{45}{self.END}"
            cmd2 = f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{self.SEP}25{self.SEP}{45}{self.END}"
        elif motion == Motion.REVERSE_OFFSET_RIGHT:
            # break it down into 2 steps
            cmd1 = f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{self.SEP}25{self.SEP}{45}{self.END}"
            cmd2 = f"{self.BACKWARD_DIST_TARGET}{self.straight_speed}{self.SEP}-25{self.SEP}{45}{self.END}"
        else:
            raise ValueError(f"Invalid motion {motion}. This should never happen.")
        return [cmd1, cmd2]

    def generate_commands(self, motions, testing=True):
        """
        Generate commands based on the list of motions
        """
        if not motions:
            return []
        commands = []
        prev_motion = motions[0]
        # cur_cmd = self._generate_command(prev_motion)
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
                if testing:
                    cur_cmd = self._generate_testing_command(prev_motion, num_motions)
                else:
                    cur_cmd = self._generate_command(prev_motion, num_motions)
                commands.extend(cur_cmd)
                num_motions = 1

            prev_motion = motion

        # add the last command
        if prev_motion == Motion.CAPTURE:
            commands.append(f"SNAP_C")
        if testing:
            cur_cmd = self._generate_testing_command(prev_motion, num_motions)
            commands.extend(cur_cmd)

        else:
            cur_cmd = self._generate_command(prev_motion, num_motions)
            commands.extend(cur_cmd)

        # add the final command
        commands.append(f"{self.FIN}")
        return commands

    def _generate_testing_command(self, motion: Motion, num_motions: int = 1):
        # for each command, output a string in the format of: "send_cmd(Flag, speed, degree, distance);"
        if num_motions > 1:
            dist = num_motions * self.UNIT_DIST
            angle = num_motions * 90
        else:
            dist = self.UNIT_DIST
            angle = 90

        if motion == Motion.FORWARD:
            return [f"send_cmd(\"{self.FORWARD_DIST_TARGET}\", {self.straight_speed}, 0, {dist})"]
        elif motion == Motion.REVERSE:
            return [f"send_cmd(\"{self.BACKWARD_DIST_TARGET}\", {self.straight_speed}, 0, {dist})"]
        elif motion == Motion.FORWARD_LEFT_TURN:
            return [f"send_cmd(\"{self.FORWARD_DIST_TARGET}\", {self.turn_speed}, -23, {angle})"]
        elif motion == Motion.FORWARD_RIGHT_TURN:
            return [f"send_cmd(\"{self.FORWARD_DIST_TARGET}\", {self.turn_speed}, 23, {angle})"]
        elif motion == Motion.REVERSE_LEFT_TURN:
            return [f"send_cmd(\"{self.BACKWARD_DIST_TARGET}\", {self.turn_speed}, -25, {angle})"]
        elif motion == Motion.REVERSE_RIGHT_TURN:
            return [f"send_cmd(\"{self.BACKWARD_DIST_TARGET}\", {self.turn_speed}, 25, {angle})"]

        # cannot combine with other motions
        elif motion == Motion.FORWARD_OFFSET_LEFT:
            # break it down into 2 steps
            func1 = f"send_cmd(\"{self.FORWARD_DIST_TARGET}\", {self.straight_speed}, -23, 45)"
            func2 = f"send_cmd(\"{self.FORWARD_DIST_TARGET}\", {self.straight_speed}, 23, 45)"
        elif motion == Motion.FORWARD_OFFSET_RIGHT:
            # break it down into 2 steps
            func1 = f"send_cmd(\"{self.FORWARD_DIST_TARGET}\", {self.straight_speed}, 23, 45)"
            func2 = f"send_cmd(\"{self.FORWARD_DIST_TARGET}\", {self.straight_speed}, -23, 45)"
        elif motion == Motion.REVERSE_OFFSET_LEFT:
            # break it down into 2 steps
            func1 = f"send_cmd(\"{self.BACKWARD_DIST_TARGET}\", {self.straight_speed}, -25, 45)"
            func2 = f"send_cmd(\"{self.BACKWARD_DIST_TARGET}\", {self.straight_speed}, 25, 45)"
        elif motion == Motion.REVERSE_OFFSET_RIGHT:
            # break it down into 2 steps
            func1 = f"send_cmd(\"{self.BACKWARD_DIST_TARGET}\", {self.straight_speed}, 25, 45)"
            func2 = f"send_cmd(\"{self.BACKWARD_DIST_TARGET}\", {self.straight_speed}, -25, 45)"
        else:
            raise ValueError(f"Invalid motion {motion}. This should never happen.")
        return [func1, func2]


def is_valid(center_x: int, center_y: int):
    """Checks if given position is within bounds

    Inputs
    ------
    center_x (int): x-coordinate
    center_y (int): y-coordinate

    Returns
    -------
    bool: True if valid, False otherwise
    """
    return 0 < center_x < WIDTH - 1 and 0 < center_y < HEIGHT - 1
