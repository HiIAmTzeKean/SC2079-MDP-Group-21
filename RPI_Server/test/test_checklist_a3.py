import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from communication.stm32 import STMLink


distance = 50
stm_link = STMLink()
stm_link.send_cmd("t",50,0,distance)
