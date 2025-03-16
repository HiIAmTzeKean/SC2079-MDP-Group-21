import logging

from .base_t2 import TaskTwo
from .constant.consts import FORWARD_SPEED_OUTDOOR


logger = logging.getLogger(__name__)

ANDRIOD_CONTROLLER = False

action_list_init = [
    "frontuntil_first",
    "SNAP1_C",
]

action_list_first_left = [
    "half_left",
    "front",
    "half_right",
    "SNAP2_C",
]
action_list_first_right = [
    "half_right",
    "front",
    "half_left",
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
    "right",
    f"T{FORWARD_SPEED_OUTDOOR}|0|20",
    f"r{FORWARD_SPEED_OUTDOOR}|0|50",
    "T30|0|20",
    "right",
    "r_ir",
    "left",
    # f"W{FORWARD_SPEED_OUTDOOR}|0|15",
]
action_list_second_right = [
    "frontuntil",
    "right",
    "L_ir",
    "u_turn_left",
    "stall",
    "l_ir",
    "L_ir",
    "left",
    f"T{FORWARD_SPEED_OUTDOOR}|0|20",
    f"l{FORWARD_SPEED_OUTDOOR}|0|50",
    "half_left",
    f"L{FORWARD_SPEED_OUTDOOR}|0|40",
    "l_ir",
    "half_right",
    f"W{FORWARD_SPEED_OUTDOOR}|0|15",
]

TaskTwoOutdoor = TaskTwo(ANDRIOD_CONTROLLER, action_list_init, action_list_first_left, action_list_first_right, action_list_second_left, action_list_second_right)
