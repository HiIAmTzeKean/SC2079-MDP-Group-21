import json
import logging
import queue
import time
from multiprocessing import Process
from typing import Any, Optional

import requests

from .base_t2 import TaskTwo
from .communication.android import AndroidMessage
from .communication.camera import snap_using_picamera2
from .communication.pi_action import PiAction
from .constant.consts import FORWARD_SPEED_INDOOR, Category, manual_commands, stm32_prefixes
from .constant.settings import URL, API_TIMEOUT


logger = logging.getLogger(__name__)

ANDRIOD_CONTROLLER = False

action_list_init = [
    "frontuntil_first",
    "SNAP1_C",
]

action_list_first_left = [
    "left_arc",
    "frontuntil",
    "SNAP2_C",
]
action_list_first_right = [
    "right_arc",
    "frontuntil",
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
    f"T{FORWARD_SPEED_INDOOR}|0|20",
    f"r{FORWARD_SPEED_INDOOR}|0|50",
    "T30|0|20",
    "right",
    "r_ir",
    "left",
    # f"W{FORWARD_SPEED_INDOOR}|0|15",
]
action_list_second_right = [
    "frontuntil",
    "right",
    "L_ir",
    "u_turn_left",
    "stall",
    "l50|0|50",
    "L_ir",
    "left",
    "T50|0|60",
    "l50|0|50",
    "left",
    "right",
    "W50|0|20",
]

TaskTwoIndoor = TaskTwo(ANDRIOD_CONTROLLER, action_list_init, action_list_first_left, action_list_first_right, action_list_second_left, action_list_second_right)
