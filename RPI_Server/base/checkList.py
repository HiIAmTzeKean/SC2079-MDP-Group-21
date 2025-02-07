import json
import logging
import os
import queue
import time
from multiprocessing import Manager, Process
from typing import Any, Optional

import requests
from communication.android import AndroidDummy, AndroidLink, AndroidMessage
from communication.pi_action import PiAction
from communication.stm32 import STMLink


logger = logging.getLogger(__name__)

class RaspberryPi:

    def __init__(self) -> None:
        """
        Initializes the Raspberry Pi
        """
        #self.android_link = AndroidDummy()
        self.android_link = AndroidLink()
        self.stm_link = STMLink()

        self.manager = Manager()

        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        self.movement_lock = self.manager.Lock()
        self.android_queue = self.manager.Queue()
        
        self.rpi_action_queue = self.manager.Queue()
        self.command_queue = self.manager.Queue()

        self.path_queue = self.manager.Queue()

        self.proc_recv_android = None
        self.proc_recv_stm32 = None
        self.proc_android_sender = None
        self.proc_command_follower = None
        self.proc_rpi_action = None
        self.rs_flag = False
        self.success_obstacles = self.manager.list()
        self.failed_obstacles = self.manager.list()
        self.obstacles = self.manager.dict()
        self.current_location = self.manager.dict()
        self.failed_attempt = False
    
    def start(self):
        """Starts RPi shenanigans"""
        self.android_link.connect()
        self.android_queue.put(AndroidMessage('info', "You are connected to the RPi!"))
        self.stm_link.connect()

        # Define Child Processes
        self.proc_recv_android = Process(target=self.recv_android)
        self.proc_recv_stm32 = Process(target=self.recv_stm)
        self.proc_android_sender = Process(target=self.android_sender)
        self.proc_command_follower = Process(target=self.command_follower)
        self.proc_rpi_action = Process(target=self.rpi_action)

        # Start Child Processes
        self.proc_recv_android.start()
        self.proc_recv_stm32.start()
        self.proc_android_sender.start()
        self.proc_command_follower.start()
        self.proc_rpi_action.start()

        logger.info("Child Processes Started")
        self.android_queue.put(AndroidMessage('info', 'Robot is ready!'))
        self.android_queue.put(AndroidMessage('mode', 'path'))
        

    def stop(self):
        """
        Stop all processes on RPI and disconnects gracefully with Android and STM32
        """
        self.android_link.disconnect()
        self.stm_link.disconnect()
        logger.info("Program Exited!")

    def recv_android(self) -> None:
        """
        [Child Process] Processes the messages received from Android
        """
        while True:
            msg_str: Optional[str] = None
            try:
                msg_str = self.android_link.recv()
            except OSError:
                self.android_dropped.set()
                logger.debug("Event set: connection dropped")
            
            if msg_str is None:
                continue

            message: dict = json.loads(msg_str)

            ## Command: Set Obstacles ##
            if message['cat'] == "obstacles":
                self.rpi_action_queue.put(PiAction(**message))
                logger.debug(
                    f"Set obstacles PiAction added to queue: {message}")
                
            elif message['cat'] == "control":
                if message['value'] == "start":
                    # Check API
                    """
                    Dummy API for now
                    """
                    
                    if not self.command_queue.empty():
                        self.unpause.set()
                        logger.info("""
                            Start command received, starting robot path!
                        """)
                        self.android_queue.put(AndroidMessage(
                            'info', 'Starting robot on path!'))
                        self.android_queue.put(
                            AndroidMessage('status', 'running'))
                    else:
                        logger.warning(
                            "The command queue is empty, please set obstacles.")
                        self.android_queue.put(AndroidMessage(
                            "error", "Command queue is empty, did you set obstacles?"))

    def rpi_action(self):
        """
        [Child Process]
        """

        while True:
            action: PiAction = self.rpi_action_queue.get()
            logger.debug(
                f"PiCation Retrieve from queue: {action.cat} {action.value}"
            )
            if action.cat == "obstacles":
                for obs in action.value['obstacles']:
                    self.obstacles[obs['id']] = obs
                self.request_algo(action.value)
            elif action.cat == "snap":
                self.snap_and_rec(obstacle_id_with_signal=action.value)
            elif action.cat == "stitch":
                self.request_stitch()
            elif action.cat == "manual":
                self.request_algo(action.value)

    def request_algo(self, data, robot_x=1, robot_y=1, robot_dir=0, retrying=False) -> None:
        """
        Requests for a series of commands etc
        The received commands and path are then queued in the respective queues
        """
        API_IP = "0.0.0.0"
        API_PORT = 5000       
        logger.info("Requesting path from algo")
        self.android_queue.put(AndroidMessage("info", "Requesting path from algo..."))
        logger.info(f"data: {data}")
        body = {**data, "big_turn": "0", "robot_x": robot_x,
                "robot_y": robot_y, "robot_dir": robot_dir, "retrying": retrying}
        url = f"http://{API_IP}:{API_PORT}/path"
        response = requests.post(url, json=body)

        if response.status_code != 200:
            self.android_queue.put(AndroidMessage(
                "error", "Something went wrong when requesting path from Algo API."))
            logger.error(
                "Something went wrong when requesting path from Algo API.")
            return
        result = json.loads(response.content)['data']
        commands = result['commands']
        path = result['path']

        # Log commands received
        logger.debug(f"Commands received from API: {commands}")

        # Put commands and paths into respective queues
        self.clear_queues()
        for c in commands:
            self.command_queue.put(c)
        for p in path[1:]:  # ignore first element as it is the starting position of the robot
            self.path_queue.put(p)

        self.android_queue.put(AndroidMessage(
            "info", "Commands and path received Algo API. Robot is ready to move."))
        logger.info(
            "Commands and path received Algo API. Robot is ready to move.")

    def request_stitch(self):
        """
        Sitch the images together??
        """


    def recv_stm(self) -> None:
        """
        [Child Process] Receive Acknowledgements
        """
        while True:
            message: str = self.stm_link.recv()

            if message.startswith("f"):
                if self.rs_flag == False:
                    self.rs_flag = True
                    logger.debug("f from STM32 received.")
                    continue
                try:
                    self.movement_lock.release()
                    try:
                        self.retrylock.release()
                    except:
                        pass
                except Exception:
                    logger.warning("Tried to release a released lock")
            else:
                logger.warning(f"""
                Ignored Unknown message from STM: {message}
                """)

    def command_follower(self) -> None:
        """
        [Child Process] Command Follow up
        """
        while True:
            #Retrieving next movement command
            command: str = self.command_queue.get()
            logger.debug("Wait for unpause")

            try:
                logger.debug("wait for retry lock")
                self.retrylock.acquire()
                self.retrylock.release()
            except:
                logger.debug("Wait for unpause")
                self.unpause.wait()
            logger.debug("wait for movelock")
            self.movement_lock.acquire()

            stm32_prefixes = ("T", "t", "w", "W")

            if command.startswith(stm32_prefixes):
                self.stm_link.send(command)
                logger.debug(f"Sending to STM32: {command}")
            
            elif command.startswith("SNAP"):
                logger.debug("Taking Picture lol")
            
            elif command == "FIN":
                logger.info("Finish liao?")
            
    def android_sender(self) -> None:
        """
        [Child Process] Sending to android moment
        """
        while True:
            try:
                message: AndroidMessage = self.android_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                self.android_link.send(message)
            except OSError:
                self.android_dropped.set()
                logger("Event moment")

    def clear_queues(self):
        """Clear both command and path queues"""
        while not self.command_queue.empty():
            self.command_queue.get()
        while not self.path_queue.empty():
            self.path_queue.get()


if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()

