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

STALL_TIME = 0.1

FORWARD_SPEED_INDOOR = 80
TRACKING_SPEED_INDOOR = 80

manual_commands: dict[str, Union[tuple[Any, ...], str]] = {
    "front": f"T{FORWARD_SPEED_INDOOR}|0|10",
    "frontuntil_first": f"W{TRACKING_SPEED_INDOOR}|0|20",
    "frontuntil_end": f"W{TRACKING_SPEED_INDOOR}|0|20",
    "frontuntil": f"W{TRACKING_SPEED_INDOOR}|0|33",
    "front_past_2nd_obstacle": f"D",
    
    "backuntil": f"w{TRACKING_SPEED_INDOOR}|0|33",
    "slight_back": f"t{FORWARD_SPEED_INDOOR}|0|20",
    "slight_back_2nd_right": f"t{FORWARD_SPEED_INDOOR}|0|20",
    
    "R_ir": f"R{TRACKING_SPEED_INDOOR}|0|30",
    "L_ir": f"L{TRACKING_SPEED_INDOOR}|0|30",
    "r_ir": f"r{TRACKING_SPEED_INDOOR}|0|50",
    "l_ir": f"l{TRACKING_SPEED_INDOOR}|0|50",
    
    "left": "T40|-35|90", #24 cm turn radius
    "right": "T40|35|90", #24 cm turn radius
    "offset_right": "T25|-10|0.1",
    "half_left": "T50|-45|47",
    "half_right": "T50|45|47",
}
             
manual_commands["left_arc"] = (manual_commands["half_left"], manual_commands["half_right"], manual_commands["half_right"],  manual_commands["half_left"])
manual_commands["right_arc"] = (manual_commands["half_right"], manual_commands["half_left"], manual_commands["half_left"], manual_commands["half_right"])
manual_commands["u_turn_right"] = (manual_commands["right"], manual_commands["right"])
manual_commands["u_turn_left"] = (manual_commands["left"], manual_commands["left"])


FORWARD_SPEED_OUTDOOR = 70
US_SPEED_OUTDOOR = 70
IR_SPEED_OUTDOOR = 50

manual_commands_outdoor: dict[str, Union[tuple[Any, ...], str]] = {
    "front": f"T{FORWARD_SPEED_OUTDOOR}|0|10",
    "frontuntil_first": f"W{US_SPEED_OUTDOOR}|0|20",
    "frontuntil_end": f"W{US_SPEED_OUTDOOR}|0|20",
    "frontuntil": f"W{US_SPEED_OUTDOOR}|0|33",
    "front_past_2nd_obstacle": f"D",
    
    "backuntil": f"w{US_SPEED_OUTDOOR}|0|33",
    "slight_back": f"t{FORWARD_SPEED_OUTDOOR}|0|30",
    "slight_back_2nd_right": f"t{FORWARD_SPEED_OUTDOOR}|0|30",
    
    "R_ir": f"R{IR_SPEED_OUTDOOR}|0|30",
    "L_ir": f"L{IR_SPEED_OUTDOOR}|0|30",
    "r_ir": f"r{IR_SPEED_OUTDOOR}|0|50",
    "l_ir": f"l{IR_SPEED_OUTDOOR}|0|50",
    
    "left": "T40|-35|90", #24 cm turn radius
    "right": "T40|35|90", #24 cm turn radius
    "offset_right": "T25|-10|0.1",
    "half_left": "T50|-45|47",
    "half_right": "T50|45|47",
}
             
manual_commands_outdoor["left_arc"] = (manual_commands_outdoor["half_left"], manual_commands_outdoor["half_right"], manual_commands_outdoor["half_right"],  manual_commands_outdoor["half_left"])
manual_commands_outdoor["right_arc"] = (manual_commands_outdoor["half_right"], manual_commands_outdoor["half_left"], manual_commands_outdoor["half_left"], manual_commands_outdoor["half_right"])
manual_commands_outdoor["u_turn_right"] = (manual_commands_outdoor["right"], manual_commands_outdoor["right"])
manual_commands_outdoor["u_turn_left"] = (manual_commands_outdoor["left"], manual_commands_outdoor["left"])

stm32_prefixes = ("T", "t", "w", "W", "D", "d","P","L","R",'l','r')
