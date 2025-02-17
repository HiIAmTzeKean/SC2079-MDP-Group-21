import json
import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from communication.android import AndroidLink, AndroidMessage
from communication.stm32 import STMLink
from constant.consts import Category


android_link = AndroidLink()
stm_link = STMLink()
android_link.connect()
android_link.send(AndroidMessage("info", "You are reconnected!"))

while True:
    android_str = android_link.recv()
    if android_str is None:
        continue
    message: dict = json.loads(android_str)
    print(f"Message received: {message}")
    if message["cat"] == Category.MANUAL.value:
        # send to stm
        stm_link.send_cmd("t",50,0,10)
        android_link.send(AndroidMessage("info", "Moved!"))
    elif message["cat"] == "FIN":
        break

android_link.disconnect()
