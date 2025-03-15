from enum import Enum
from typing import Any, Union


SYMBOL_MAP = {
    "10": "Bullseye",
    "11": "One",
    "12": "Two",
    "13": "Three",
    "14": "Four",
    "15": "Five",
    "16": "Six",
    "17": "Seven",
    "18": "Eight",
    "19": "Nine",
    "20": "A",
    "21": "B",
    "22": "C",
    "23": "D",
    "24": "E",
    "25": "F",
    "26": "G",
    "27": "H",
    "28": "S",
    "29": "T",
    "30": "U",
    "31": "V",
    "32": "W",
    "33": "X",
    "34": "Y",
    "35": "Z",
    "36": "Up Arrow",
    "37": "Down Arrow",
    "38": "Right Arrow",
    "39": "Left Arrow",
    "40": "Stop"
}

class Category(Enum):
    INFO = 'info'
    MODE = 'mode' # the current mode of the robot (`manual` or `path`)
    PATH = 'path'
    MANUAL = 'manual'
    SNAP = 'snap'
    LOCATION = 'location' # the current location of the robot (in Path mode)
    FAILED = 'failed'
    SUCCESS = 'success'
    ERROR = 'error'
    OBSTACLE = 'obstacles' # list of obstacles
    IMAGE_REC = 'image-rec' # image recognition results
    STATUS = 'status' # status updates of the robot (`running` or `finished`)
    STITCH = 'stitch'
    FIN = 'FIN'


FORWARD_SPEED = 60

manual_commands: dict[str, Union[tuple[Any, ...], str]] = {
    "front": f"T{FORWARD_SPEED}|0|10",
    "frontuntil": f"W{FORWARD_SPEED}|0|40",
    "front_R_ir": "R30|0|30",
    "front_L_ir": "L30|0|30",
    "back": "t50|0|10",
    "left": "T30|-60.5|91.5", #20cm turn radius
    "right": "T30|58|91.5",
    "half_right": "T20|25|45",
    "half_left": "T20|-25|45",
    "slight_back": "t20|0|1",
    "left_correct": "T25|10|0.1"
}

                        
manual_commands["left_arc"] = (manual_commands["half_left"], manual_commands["half_right"], manual_commands["slight_back"],  manual_commands["half_right"], manual_commands["half_left"])
manual_commands["right_arc"] = (manual_commands["half_right"], manual_commands["half_left"], manual_commands["slight_back"], manual_commands["half_left"], manual_commands["half_right"])

stm32_prefixes = ("T", "t", "w", "W", "D", "d","P","L","R",'l','r')
