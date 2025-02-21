import os
import sys
import logging
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from communication.android import AndroidLink, AndroidMessage
from communication.pi_action import PiAction

logger = logging.getLogger(__name__)

android_link = AndroidLink()
android_link.connect()
android_link.send(AndroidMessage("info", "You are reconnected!"))
for i in range(1):
    msg = android_link.recv()
    logger.info(msg)
    message: dict = json.loads(msg)
    action = PiAction(**message)
    logger.info(action.value)
    android_link.send(AndroidMessage("info", f"you sent: {message}"))

android_link.disconnect()
