import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from communication.android import AndroidLink, AndroidMessage


android_link = AndroidLink()
android_link.connect()
android_link.send(AndroidMessage("info", "You are reconnected!"))
android_link.recv()
android_link.disconnect()
