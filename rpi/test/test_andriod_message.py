import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from communication.android import AndroidMessage


info_message = AndroidMessage("info", "You are reconnected!")
print(info_message.to_string())
info_message = AndroidMessage("status", "finished")
print(info_message.to_string())
info_message = AndroidMessage("error", "Command queue empty (no obstacles)")
print(info_message.to_string())
info_message = AndroidMessage(
    "location",
    {
        "x": 1,
        "y": 2,
        "d": 3,
    },
)
print(info_message.to_string())
