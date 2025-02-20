import logging
import time
from multiprocessing import Process
import requests
from .base_rpi import RaspberryPi
from .communication.camera import snap_using_libcamera
from .communication.pi_action import PiAction
from .constant.consts import Category, stm32_prefixes
from .constant.settings import URL
from rpi.communication.stm32 import STMLink
from rpi.constant.command_utils import (
     exec_seq,
     cmd_front,
     cmd_left,
     cmd_right,
     cmd_back,
     cmd_bright,
     cmd_bleft,
     cmd_left_arc,
     cmd_right_arc
 )

logger = logging.getLogger(__name__)

class TaskTwo(RaspberryPi):
    def __init__(self) -> None:
        super().__init__()
        self.stm_link = STMLink()

    def start(self) -> None:
        """Starts the hardcoded execution sequence."""
        logger.info("Starting TaskTwo: Direct control over STM and Image Recognition")
        try:
            self.stm_link.connect()

            # Process for movement and image processing
            self.proc_execute_task = Process(target=self.execute_task)
            self.proc_execute_task.start()

            logger.info("TaskTwo process started")

        except KeyboardInterrupt:
            self.stop()

    def execute_task(self) -> None:
        #Step 1 move near object 
        cmd_front(self.stm_link)
        #Step 2 Turn left or right (need recognize the direction arrow)
        self.turning_decision()
        
        #Step 3 Move until near object (detect direction arrow)
        exec_seq(self.stm_link, ["frontuntil"])
        
        #Step 4 Turn left or right
        
        #Step 5
        #after turning, have to use IR sensor to detect whether obstacle is cleared 
        #don't have the flag yet I think

        #Step 6
        #Left Arrow, need go right
        #exec_seq(self.stm_link, ["right180"])
        #Right Arrow, need go left
        #exec_seq(stm_Link, ["left180"])

        #Step 7 clear the obstacle length, use IR sensor to determine? Need to discuss 
        #need to capture the distance travelled for later use Width
        #don't have the flag yet

        #Step 8
        #Left arrow #cmd_right
        #Right arrow #cmd_left

        #Step 9 I think need to know how far we traversed, not sure how this can be implemented but need to path find back..
        #self.stm_link.send_cmd("W",50,0,WidthHalf)
        
        #Step 10 Park
        
        #d1d2 not sure how we capturing the distance, same for Width

        #Step 4 to 10
        self.turning_decision2()

    
    def process_image(self, image_path: str) -> str:
        response = requests.post(f"http://{URL}/image_recognition", files={"file": open(image_path, "rb")})
    
        if response.status_code == 200:
            arrow_code = response.json().get("direction", "UNKNOWN")
            if arrow_code in ["38", "39"]:
                return arrow_code
        else:
            logger.error("Failed to process image")

        return "UNKNOWN"

    def turning_decision(self) -> None:
   
        logger.info("Snapping photo for arrow recognition")
        image_path = snap_using_libcamera()

        arrow_code = self.process_image(image_path)

        if arrow_code == "39":  # Left Arrow
            logger.info("Arrow detected: LEFT (39)")
            cmd_left_arc(self.stm_link)
        elif arrow_code == "38":  # Right Arrow
            logger.info("Arrow detected: RIGHT (38)")
            cmd_right_arc(self.stm_link)
        else:
            logger.warning("No valid arrow detected, stopping robot")
            self.stop_movement()  # Stop if no valid arrow is detected

    def turning_decision2(self) -> None:
   
        logger.info("Snapping photo for arrow recognition")
        image_path = snap_using_libcamera()

        arrow_code = self.process_image(image_path)

        if arrow_code == "39":  # Left Arrow
            logger.info("Arrow detected: LEFT (39)")
            cmd_left(self.stm_link)
            #self.IRclear()
            exec_seq(self.stm_Link, ["right180"])
            #self.IRclear()
            cmd_right(self.stm_link)
            #self.stm_link.send_cmd("T",50,0,d1d2)
            cmd_right(self.stm_link)
            #self.stm_link.send_cmd("T",50,0,WidthHalf)
            cmd_left(self.stm_link)
            self.stm_link.send_cmd("T",50,0,45)
        elif arrow_code == "38":  # Right Arrow
            logger.info("Arrow detected: RIGHT (38)")
            cmd_right(self.stm_link)
            #self.IRclear()
            exec_seq(self.stm_Link, ["left180"])
            #self.IRclear()
            cmd_left(self.stm_link)
            #self.stm_link.send_cmd("T",50,0,d1d2)
            cmd_left(self.stm_link)
            #self.stm_link.send_cmd("T",50,0,WidthHalf)
            cmd_right(self.stm_link)
            self.stm_link.send_cmd("T",50,0,45)
        else:
            logger.warning("No valid arrow detected, stopping robot")
            self.stop_movement()  # Stop if no valid arrow is detected