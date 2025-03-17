import logging

from .base_t2 import TaskTwo
from .constant.consts import FORWARD_SPEED_OUTDOOR, manual_commands_outdoor


logger = logging.getLogger(__name__)

ANDRIOD_CONTROLLER = False

action_list_init = [
    "frontuntil_first",
    "SNAP1_C",
]

action_list_first_left = [
    "left_arc",
    "frontuntil",
    "backuntil",
    "SNAP2_C",
]
action_list_first_right = [
    "right_arc",
    "frontuntil",
    "backuntil",
    "SNAP2_C",
]
action_list_second_left = [
    "frontuntil",
    "left",  # robot 15cm apart from wall, 20cm turn radius
    "R_ir",
    "u_turn_right",
    "stall",
    
    "r_ir",  # 15cm apart from wall on opposite side
    "R_ir",
    "stall",
    
    "right",
    f"T{FORWARD_SPEED_INDOOR}|0|20",
    f"r{FORWARD_SPEED_INDOOR}|0|50",
    f"T{FORWARD_SPEED_INDOOR}|0|20",
    "right",
    "r_ir",
    "slight_back",
    "left",
    "frontuntil_end",
]
action_list_second_right = [
    "frontuntil",
    "right",
    "L_ir",
    "u_turn_left",
    "stall",
    
    "l_ir",
    "L_ir",
    "stall",
    
    "left",
    f"T{FORWARD_SPEED_INDOOR}|0|20",
    f"l{FORWARD_SPEED_INDOOR}|0|50",
    f"T{FORWARD_SPEED_INDOOR}|0|20",
    "left",
    "l_ir",
    "slight_back_2nd_right",
    "right",
    "frontuntil_end",
]

TaskTwoOutdoor = TaskTwo(ANDRIOD_CONTROLLER,
                         action_list_init,
                         action_list_first_left,
                         action_list_first_right,
                         action_list_second_left,
                         action_list_second_right,
                         manual_commands_outdoor,
                    )
