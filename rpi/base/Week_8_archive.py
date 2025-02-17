#!/usr/bin/env python3
import json
import os
import queue
import time
from multiprocessing import Manager, Process
from typing import Optional

import cv2
import requests
from communication.android import AndroidLink, AndroidMessage
from communication.camera import snap_using_libcamera, snap_using_picamera
from communication.pi_action import PiAction
from communication.stm32 import STMLink
from constant.consts import SYMBOL_MAP
from constant.settings import API_IP, API_PORT
from picamera import PiCamera
from picamera.array import PiRGBArray


logger = logging.getLogger(__name__)

class RaspberryPi:
    """
    Class that represents the Raspberry Pi.
    """

    def __init__(self) -> None:
        """
        Initializes the Raspberry Pi.
        """
        self.android_link = AndroidLink()
        self.stm_link = STMLink()

        self.manager = Manager()

        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        self.movement_lock = self.manager.Lock() #locks the movement
        
#       self.retrylock = self.manager.Lock() #locks the retry

        self.android_queue = self.manager.Queue()  # Messages to send to Android
        # Messages that need to be processed by RPi
        self.rpi_action_queue = self.manager.Queue()
        # Messages that need to be processed by STM32, as well as snap commands
        self.command_queue = self.manager.Queue()
        # X,Y,D coordinates of the robot passed from the command_queue
        self.path_queue = self.manager.Queue()

        self.proc_recv_android = None # recieve android
        self.proc_recv_stm32 = None # recieve stm
        self.proc_android_sender = None #subprocess to send to androi
        self.proc_command_follower = None #commands given by the algo
        self.proc_rpi_action = None #proc action
        self.rs_flag = False
        self.success_obstacles = self.manager.list()
        self.failed_obstacles = self.manager.list()
        self.obstacles = self.manager.dict()
        self.current_location = self.manager.dict()
        self.failed_attempt = False

    def start(self):
        """Starts the RPi orchestrator"""
        try:
            ### Start up initialization ###

            self.android_link.connect()
            self.android_queue.put(AndroidMessage(
                'info', 'You are connected to the RPi!'))
            self.stm_link.connect()
            self.check_api()

            # Define child processes
            self.proc_recv_android = Process(target=self.recv_android)
            self.proc_recv_stm32 = Process(target=self.recv_stm)
            self.proc_android_sender = Process(target=self.android_sender)
            self.proc_command_follower = Process(target=self.command_follower)
            self.proc_rpi_action = Process(target=self.rpi_action)

            # Start child processes
            self.proc_recv_android.start()
            self.proc_recv_stm32.start()
            self.proc_android_sender.start()
            self.proc_command_follower.start()
            self.proc_rpi_action.start()

            logger.info("Child Processes started")

            ### Start up complete ###

            # Send success message to Android
            self.android_queue.put(AndroidMessage('info', 'Robot is ready!'))
            self.android_queue.put(AndroidMessage('mode', 'path'))
            self.reconnect_android()

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stops all processes on the RPi and disconnects with Android and STM32"""
        self.android_link.disconnect()
        self.stm_link.disconnect()
        logger.info("In stop Program exited!")

    def reconnect_android(self):
        """Handles the reconnection to Android in the event of a lost connection."""
        logger.info("Reconnection handler is watching...")

        while True:
            # Wait for android connection to drop
            self.android_dropped.wait()

            logger.error("In reconnect_android: Android is down")

            # Kill child processes
            logger.debug("In reconnect_android: Stopping android child processes")
            self.proc_android_sender.kill()
            self.proc_recv_android.kill()

            # Wait for the child processes to finish
            self.proc_android_sender.join()
            self.proc_recv_android.join()
            assert self.proc_android_sender.is_alive() is False
            assert self.proc_recv_android.is_alive() is False
            logger.debug("In reconnect_android: Android process stopped")

            # Clean up old sockets
            self.android_link.disconnect()

            # Reconnect
            self.android_link.connect()

            # Recreate Android processes
            self.proc_recv_android = Process(target=self.recv_android)
            self.proc_android_sender = Process(target=self.android_sender)

            # Start previously killed processes
            self.proc_recv_android.start()
            self.proc_android_sender.start()

            logger.info("In reconnect_android: Android processes restarted")
            self.android_queue.put(AndroidMessage(
                "info", "You are reconnected!"))
            self.android_queue.put(AndroidMessage('mode', 'path'))

            self.android_dropped.clear()
## main function
    def recv_android(self) -> None:
        """
        [Child Process] Processes the messages received from Android
        """
        while True:
            android_str: Optional[str] = None
            try:
                android_str = self.android_link.recv()
            except OSError:
                self.android_dropped.set()
                logger.debug("In recv_android: Event set: Android connection dropped")

            if android_str is None:
                continue

            message: dict = json.loads(android_str)

            ## Command: Set obstacles ##
            if message['cat'] == "obstacles":
                self.rpi_action_queue.put(PiAction(**message))
                logger.debug(
                    f"In recv_android: PiAction obstacles appended to queue: {message}")
            elif message['cat'] == "manual":
                if message['value'] == "front":
                    self.stm_link.send_cmd("T", 50, 0, 10)
                    continue
                elif message['value'] == "back":
                    self.stm_link.send_cmd("t", 50, 0, 10)
                    continue
                
                elif message['value'] == "left":
                    self.stm_link.send_cmd("T", 50, -25, 90)
                    continue
                
                elif message['value'] == "right":
                    self.stm_link.send_cmd("T", 50, 25, 90)
                    continue
                
                elif message['value'] == "bright":
                    self.stm_link.send_cmd("t", 30, 20, 90)
                    continue
                
                elif message['value'] == "bleft":
                    self.stm_link.send_cmd("t", 30, -20, 90)
                    continue
                else:
                    logger.error(
                            "In recv_android: Invalid manual command!")
                    continue
            ## Command: Start Moving ##
            elif message['cat'] == "control":
                if message['value'] == "start":
                    # Check API
                    if not self.check_api():
                        logger.error(
                            "In recv_android: API is down! Start command aborted.")
                        self.android_queue.put(AndroidMessage(
                            'error', "API is down, start command aborted."))

                    # Commencing path following
                    if not self.command_queue.empty():
                        logger.info("Gryo reset!")
                        #self.stm_link.send("RS00")
                        # Main trigger to start movement #
                        self.unpause.set()
                        logger.info(
                            "In recv_android: Start command received, starting robot on path!")
                        self.android_queue.put(AndroidMessage(
                            'info', 'Starting robot on path!'))
                        self.android_queue.put(
                            AndroidMessage('status', 'running'))
                    else:
                        logger.warning(
                            "In recv_android: The command queue is empty, please set obstacles.")
                        self.android_queue.put(AndroidMessage(
                            "error", "Command queue is empty, did you set obstacles?"))

    def recv_stm(self) -> None:
        """
        [Child Process] Receive acknowledgement messages from STM32, and release the movement lock
        """
        while True:
            
            #message: str = self.stm_link.recv()
            message: str = self.stm_link.wait_receive()
            #message = "f"
            #logger.debug(f"In recv_stm: PROCESS RUNNING Receiving from STM32 before: {message}")

            if message.startswith("fD"):
                # if self.rs_flag == False:
                    # self.rs_flag = True
                    # logger.debug("In recv_stm: fD from STM32 received.")
                    # logger.debug(f"In recv_stm: Get current queue: {self.command_queue.qsize()}")
                logger.debug("In recv_stm: fD from STM32 received.")
                logger.debug(f"In recv_stm: Get current queue: {self.command_queue.qsize()}")
                cur_location = self.path_queue.get_nowait()
                logger.debug("In recv_stm: Goes through cur_location")
                logger.debug(f"In recv_stm: Value of cur_location: {cur_location}")

                self.current_location['x'] = cur_location['x']
                self.current_location['y'] = cur_location['y']
                self.current_location['d'] = cur_location['d']
                logger.info(
                    f"In recv_stm: self.current_location = {self.current_location}")
                self.android_queue.put(AndroidMessage('location', {
                    "x": cur_location['x'],
                    "y": cur_location['y'],
                    "d": cur_location['d'],
                }))
                
                #self.movement_lock.release()
                #logger.debug("In recv_stm:f from STM32 received, movement lock released.")
                #self.retrylock.release()
                #logger.debug("In recv_stm: Can't release retrylock")
                try:
                    logger.debug("In recv_stm: fD from STM32 received, releasing movement lock and retrylock.")
                    self.movement_lock.release()
                    self.retrylock.release()
                except:
                    pass
            else:
                #self.movement_lock.release()
                #logger.debug("In recv_stm:f from STM32 received, movement lock released.")
                #self.retrylock.release()
                logger.warning(
                    f"In recv_stm: Ignored unknown message from STM: {message}")
                try:
                    logger.debug("In recv_stm: unkown message from STM32 received, releasing movement lock and retrylock.")
                    self.movement_lock.release()
                    self.retrylock.release()
                except:
                    pass
    def android_sender(self) -> None:
        """
        [Child process] Responsible for retrieving messages from android_queue and sending them over the Android link. 
        """
        while True:
            # Retrieve from queue
            try:
                message: AndroidMessage = self.android_queue.get(timeout=0.5)
            except queue.Empty:
                #logger.debug("Queue Empty!")
                continue

            try:
                self.android_link.send(message)
            except OSError:
                self.android_dropped.set()
                logger.debug("In android_sender: Event set: Android dropped")

    def command_follower(self) -> None:
        """
        [Child Process] 
        """
        while True:
            # Retrieve next movement command
            command: str = self.command_queue.get()
            logger.debug(f"In command_follower: Command Dequeued: {command}")
            # Wait for unpause event to be true [Main Trigger]
            try:
                logger.debug("In command_follower: wait for retrylock")
                self.retrylock.acquire()
                self.retrylock.release()
            except Exception as e:
                logger.debug(f"In command_follower: wait for unpause: {e}")
                self.unpause.wait()
            # Acquire lock first (needed for both moving, and snapping pictures)
            logger.debug("In command_follower: Acquiring movement lock...")
            self.movement_lock.acquire()
            # STM32 Commands - Send straight to STM32
            stm32_prefixes = ("T", "t", "w", "W", "D", "d")
            logger.debug(f"In command_follower: Getting Prefix: {command}")
            
            if command.startswith(stm32_prefixes):
                strings = str(command)
                #strings += "\n"
                parts = strings.split('|')
                first_part = parts[0]
                flag = first_part[0]
                speed = int(first_part[1:])
                angle = int(parts[1])
                val = int(parts[2])
                    
                self.stm_link.send_cmd(flag,speed,angle,val)
                logger.debug(f"In command_follower: Sending to STM32: {command}")
            
            # Snap command
            elif command.startswith("SNAP"):
                obstacle_id_with_signal = command.replace("SNAP", "")
                
                self.rpi_action_queue.put(
                    PiAction(cat="snap", value=obstacle_id_with_signal))
                time.sleep(1)
                try:
                    self.movement_lock.release()
                    self.retrylock.release()
                    logger.debug(
                        f"In recognise_image: movement_lock and retrylock released")
                except:
                    pass

            # End of path (TBD)
            elif command == "FIN":
                logger.info(
                    f"In command_follower: At FIN, self.failed_obstacles: {self.failed_obstacles}")
                logger.info(
                    f"In command_follower: At FIN, self.current_location: {self.current_location}")
#                 if len(self.failed_obstacles) != 0 and self.failed_attempt == False:
# 
#                     new_obstacle_list = list(self.failed_obstacles)
#                     for i in list(self.success_obstacles):
#                         # {'x': 5, 'y': 11, 'id': 1, 'd': 4}
#                         i['d'] = 8
#                         new_obstacle_list.append(i)
# 
#                     logger.info("In command_follower: Attempting to go to failed obstacles")
#                     self.failed_attempt = True
#                     self.request_algo({'obstacles': new_obstacle_list, 'mode': '0'},
#                                       self.current_location['x'], self.current_location['y'], self.current_location['d'], retrying=True)
#                     self.retrylock = self.manager.Lock()
#                     self.movement_lock.release()
#                     continue
                
                self.unpause.clear()
                logger.debug(f"In command_follower: unpause cleared")
                try:
                    logger.debug(f"In command_follower: releasing movement_lock.")
                    self.movement_lock.release()
                except:
                    pass
                logger.info("In command_follower: Commands queue finished.")
                self.android_queue.put(AndroidMessage(
                    "info", "Commands queue finished."))
                self.android_queue.put(AndroidMessage("status", "finished"))
                self.rpi_action_queue.put(PiAction(cat="stitch", value=""))
            else:
                raise Exception(f"In command_follower: Unknown command: {command}")
            
    ## action for the rpi to snap or stitch
    def rpi_action(self):
        """
        [Child Process] 
        """
        while True:
            action: PiAction = self.rpi_action_queue.get()
            logger.debug(
                f"In rpi_action: PiAction retrieved from queue: {action.cat} {action.value}")
            ## obstacle ID
            if action.cat == "obstacles":
                for obs in action.value['obstacles']:
                    self.obstacles[obs['id']] = obs
                self.request_algo(action.value)
            ## snap image
            elif action.cat == "snap":
                self.recognise_image(obstacle_id_with_signal=action.value)
            ## stitch
            elif action.cat == "stitch":
                self.request_stitch()

    def recognise_image(self, obstacle_id_with_signal: str) -> None:
        """
        RPi snaps an image and calls the API for image-rec.
        The response is then forwarded back to the android
        :param obstacle_id_with_signal: eg: SNAP<obstacle_id>_<C/L/R>
        """
        obstacle_id, signal = obstacle_id_with_signal.split("_")
        logger.info(f"In recognise_image: Capturing image for obstacle id: {obstacle_id}")
        self.android_queue.put(AndroidMessage(
            "info", f"Capturing image for obstacle id: {obstacle_id}"))
        #obstacle_id, signal = "1","C"
        url = f"http://{API_IP}:{API_PORT}/image"
        filename = f"/home/pi/cam/{int(time.time())}_{obstacle_id}_{signal}.jpg"
        filename_send = f"{int(time.time())}_{obstacle_id}_{signal}.jpg"
        results=snap_using_libcamera(self,obstacle_id,signal,filename,filename_send,url,False)
        

        # results = json.loads(response.content)
        

        # logger.info(f"In recognise_image: results: {results}")
        # logger.info(f"In recognise_image: self.obstacles: {self.obstacles}")
        # logger.info(
            # f"In recognise_image: Image recognition results: {results} ({SYMBOL_MAP.get(results['image_id'])})")

        # if results['image_id'] == 'NA':
            # self.failed_obstacles.append(
                # self.obstacles[int(results['obstacle_id'])])
            # logger.info(
                # f"In recognise_image: Added Obstacle {results['obstacle_id']} to failed obstacles.")
            # logger.info(f"In recognise_image: self.failed_obstacles: {self.failed_obstacles}")
        # else:
            # self.success_obstacles.append(
                # self.obstacles[int(results['obstacle_id'])])
            # logger.info(
                # f"In recognise_image: self.success_obstacles: {self.success_obstacles}")
        self.android_queue.put(AndroidMessage("image-rec", results))

    def request_algo(self, data, robot_x=1, robot_y=1, robot_dir=0, retrying=False):
        """
        Requests for a series of commands and the path from the Algo API.
        The received commands and path are then queued in the respective queues
        """
        logger.info("In request_algo: Requesting path from algo...")
        self.android_queue.put(AndroidMessage(
            "info", "Requesting path from algo..."))
        logger.info(f"In request_algo: In request_algo: data: {data}")
        body = {**data, "big_turn": "0", "robot_x": robot_x,
                "robot_y": robot_y, "robot_dir": robot_dir, "retrying": retrying}
        url = f"http://{API_IP}:{API_PORT}/path"
        response = requests.post(url, json=body)

        # Error encountered at the server, return early
        if response.status_code != 200:
            self.android_queue.put(AndroidMessage(
                "error", "Error when requesting path from Algo API."))
            logger.error(
                "In request_algo: Error when requesting path from Algo API.")
            return

        # Parse response
        result = json.loads(response.content)['data']
        commands = result['commands']
        path = result['path']

        # Log commands received
        logger.debug(f"In request_algo: Commands received from API: {commands}")

        # Put commands and paths into respective queues
        self.clear_queues()
        for c in commands:
            self.command_queue.put(c)
        for p in path[1:]:  # ignore first element as it is the starting position of the robot
            self.path_queue.put(p)

        self.android_queue.put(AndroidMessage(
            "info", "Commands and path received Algo API. Robot is ready to move."))
        logger.info(
            "In request_algo: Commands and path received Algo API. Robot is ready to move.")

    def request_stitch(self):
        """Sends a stitch request to the image recognition API to stitch the different images together"""
        url = f"http://{API_IP}:{API_PORT}/stitch"
        response = requests.get(url)

        # If error, then log, and send error to Android
        if response.status_code != 200:
            # Notify android
            self.android_queue.put(AndroidMessage(
                "error", "Something went wrong when requesting stitch from the API."))
            logger.error(
                "In request_stitch: Error when requesting stitch from the API.")
            return

        logger.info("Images stitched!")
        self.android_queue.put(AndroidMessage("info", "Images stitched!"))

    def clear_queues(self) -> None:
        """Clear both command and path queues"""
        while not self.command_queue.empty():
            self.command_queue.get()
        while not self.path_queue.empty():
            self.path_queue.get()

    def check_api(self) -> bool:
        """Check whether server is up and running

        Returns:
            bool: True if running, False if not.
        """
        # Check image recognition API
        url = f"http://{API_IP}:{API_PORT}/status"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                logger.debug("API is up!")
                return True
            return False
        # If error, then log, and return False
        except ConnectionError:
            logger.warning("In check_api: API Connection Error")
            return False
        except requests.Timeout:
            logger.warning("In check_api: API Timeout")
            return False
        except Exception as e:
            logger.warning(f"In check_api: API Exception: {e}")
            return False


if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()
