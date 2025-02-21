from enum import Enum


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
    SNAP = 'snap'
    LOCATION = 'location' # the current location of the robot (in Path mode)
    FAILED = 'failed'
    SUCCESS = 'success'
    ERROR = 'error'
    OBSTACLE = 'obstacle' # list of obstacles
    IMAGE_REC = 'image-rec' # image recognition results
    STATUS = 'status' # status updates of the robot (`running` or `finished`)

manual_commands = {
    "front": ("T", 50, 0, 10),
    "back": ("t", 50, 0, 10),
    "left": ("T", 50, -25, 90),
    "right": ("T", 50, 25, 90),
    "bright": ("t", 30, 20, 90),
    "bleft": ("t", 30, -20, 90)
}
