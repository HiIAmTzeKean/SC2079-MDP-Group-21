import logging

from .base_t2 import TaskTwo
from .constant.consts import FORWARD_SPEED_INDOOR, manual_commands


logger = logging.getLogger(__name__)

ANDRIOD_CONTROLLER = False

action_list_init = [
    "offset_right",
    "frontuntil_first",
    "SNAP1_C",
]

action_list_first_left = [
    "left_arc",
    "D0|0|0",
    "frontuntil",
    "D0|0|0",
    "backuntil",
    "SNAP2_C",
]
action_list_first_right = [
    "right_arc",
    "D0|0|0",
    "frontuntil",
    "D0|0|0",
    "backuntil",
    "SNAP2_C",
]
action_list_second_left = [
    "left",  # robot 15cm apart from wall, 20cm turn radius
    "R_ir",
    "t30|0|10",
    "u_turn_right",
    "offset_right",

    "r_ir",  # 15cm apart from wall on opposite side
    "front",
    "R_ir",
    "stall",
    "right",
    "offset_right",
    
    "front_past_2nd_obstacle",
    "right",
    "slight_back",
    "r20|0|40",
    "T50|-60|100",
    "frontuntil_end",
    "FIN",
]
action_list_second_right = [
    "right",
    "offset_right",
    "L_ir",
    "t30|0|10",
    "u_turn_left",
    
    "l_ir",
    "front",
    "L_ir",
    "stall",
    "left",

    "front_past_2nd_obstacle",
    "left",
    "slight_back",
    "l20|0|50",
    "T50|60|100",
    "frontuntil_end",
    "FIN",
]

TaskTwoIndoor = TaskTwo(ANDRIOD_CONTROLLER,
                        action_list_init,
                        action_list_first_left,
                        action_list_first_right,
                        action_list_second_left,
                        action_list_second_right,
                        manual_commands,
                    )
