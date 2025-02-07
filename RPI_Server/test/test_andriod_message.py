import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from communication.android import AndroidMessage


info_message = AndroidMessage("info", "You are reconnected!")
print(info_message.to_string())