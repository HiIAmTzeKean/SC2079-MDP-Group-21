import json
import logging
import queue
import time
from multiprocessing import Process
from typing import Optional

import requests

from .base_rpi import RaspberryPi
from .communication.android import AndroidMessage
from .communication.camera import snap_using_picamera2
from .communication.pi_action import PiAction
from .constant.consts import FORWARD_SPEED_OUTDOOR, STALL_TIME, Category, stm32_prefixes
from .constant.settings import API_TIMEOUT, URL


logger = logging.getLogger(__name__)

class TaskTwo(RaspberryPi):
    def __init__(self, android_controller, action_list_init, action_list_first_left, action_list_first_right, action_list_second_left, action_list_second_right, manual_commands) -> None:
        super().__init__()
        del self.path_queue
        self.first_obstacle = True
        self.ready_snap = self.manager.Event()
        """Event to indicate that ready to snap"""
        self.snap_pending = self.manager.Value("i", 1)
        """locks the movement"""
        self.ANDRIOD_CONTROLLER = android_controller
        self.action_list_init = action_list_init
        self.action_list_first_left = action_list_first_left
        self.action_list_first_right = action_list_first_right
        self.action_list_second_left = action_list_second_left
        self.action_list_second_right = action_list_second_right
        self.manual_commands = manual_commands

    def start(self) -> None:
        """Starts the RPi orchestrator"""
        logger.info("starting the start function")
        try:
            if self.ANDRIOD_CONTROLLER:
                self.android_link.connect()
            self.stm_link.connect()
            self.check_api()

            self.proc_recv_stm32 = Process(target=self.recv_stm)
            self.proc_command_follower = Process(target=self.command_follower)
            self.proc_rpi_action = Process(target=self.rpi_action)
            self.proc_android_controller = Process(target=self.android_controller)
            self.proc_recv_android = Process(target=self.recv_android)
            
            self.set_actions(self.action_list_init)
            self.unpause.set()
            
            if self.ANDRIOD_CONTROLLER:
                self.proc_android_controller.start()
                self.proc_recv_android.start()
                self.unpause.clear()
            self.proc_recv_stm32.start()
            self.proc_command_follower.start()
            self.proc_rpi_action.start()
            if self.ANDRIOD_CONTROLLER:
                self.reconnect_android()

            logger.info("Child Processes started")
            self.finish_all.wait()
            self.stop()
            processes = [getattr(self, attr) for attr in dir(self) if attr.startswith("proc_")]
            for process in processes:
                try:
                    process.join()
                except Exception as e:
                    logger.error(f"Error joining process, likely already killed: {e}")
            return
        except KeyboardInterrupt:
            self.stop()

    def set_actions(self, action_list: list) -> None:
        """Sets the actions for the RPi"""
        for action in action_list:
            logger.debug(f"putting action {action} in queue")
            if action.startswith("SNAP"):
                self.command_queue.put(action)
                continue
            elif self.manual_commands.get(action) is None:
                # specify custom
                self.command_queue.put(action)
                continue
            elif action == "FIN":
                self.command_queue.put(Category.FIN.value)
                continue
            elif action == "front_past_2nd_obstacle":
                self.command_queue.put(f"T{FORWARD_SPEED_OUTDOOR}|0|{self.second_obstacle_dist.get()+31+60}")
                continue
            elif type(self.manual_commands[action]) == tuple:
                for item in self.manual_commands[action]:
                    self.command_queue.put(item)
                continue
            self.command_queue.put(self.manual_commands[action])

    def rpi_action(self) -> None:
        """
        [Child Process] For processing the actions that the RPi needs to take.
        """
        while True:
            action = self.rpi_action_queue.get()
            logger.debug(f"PiAction retrieved from queue: {action.cat} {action.value}")
            if action.cat == Category.SNAP.value:
                self.ready_snap.wait()
                results = self.recognize_image(obstacle_id_with_signal=action.value)

                if self.first_obstacle:
                    self.snap_pending.set(1)
                    self.first_obstacle = False
                    if results["image_id"] == "38":  # right
                        self.set_actions(self.action_list_first_right)
                    else:
                        self.set_actions(self.action_list_first_left)
                else:
                    # obstacle 2
                    self.snap_pending.set(0)
                    if results["image_id"] == "38":
                        self.set_actions(self.action_list_second_right)
                    else:
                        self.set_actions(self.action_list_second_left)
                self.ready_snap.clear()
                self.unpause.set()
            elif action.cat == Category.STITCH.value:
                self.request_stitch()

    def reconnect_android(self) -> None:
        """Handles the reconnection to Android in the event of a lost connection."""
        logger.info("Reconnection handler is watching...")

        while True and not self.completed:
            # Wait for android connection to drop
            self.android_dropped.wait()

            logger.error("Android is down")

            # Kill child processes
            logger.debug("Stopping android child processes")
            self.proc_android_controller.kill()
            self.proc_recv_android.kill()

            # Wait for the child processes to finish
            self.proc_android_controller.join()
            self.proc_recv_android.join()
            assert self.proc_android_controller.is_alive() is False
            assert self.proc_recv_android.is_alive() is False
            logger.debug("Android process stopped")

            # Clean up old sockets
            self.android_link.disconnect()
            self.android_link.connect()

            # Recreate Android processes
            self.proc_recv_android = Process(target=self.recv_android)
            self.proc_android_controller = Process(target=self.android_controller)
            self.proc_recv_android.start()
            self.proc_android_controller.start()

            logger.info("Android processes restarted")
            self.android_queue.put(AndroidMessage(Category.INFO.value, "You are reconnected!"))
            self.android_queue.put(AndroidMessage(Category.MODE.value, "path"))

            self.android_dropped.clear()
    
    def android_controller(self) -> None:
        """
        [Child process] Responsible for retrieving messages
        from android_queue and sending them over the Android link.
        """
        while True:
            try:
                # blocks for 0.05 seconds to check if there are any messages
                # in the queue
                message = self.android_queue.get(timeout=0.05)
                self.android_link.send(message)
            except queue.Empty:
                continue
            except OSError:
                self.android_dropped.set()
                logger.error("OSError. Event set: Android dropped")
            except Exception as e:
                logger.error(f"Error sending message to Android: {e}")
            
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
                logger.debug("OSError. Event set: Android dropped")

            if android_str is None:
                logger.debug("Empty message from andriod")
                continue

            message: dict = json.loads(android_str)

            if message["cat"] == "control":
                # Commencing path following
                if not self.command_queue.empty():
                    self.unpause.set()

                    logger.info("Start command received, starting robot on path!")
                    self.android_queue.put(AndroidMessage(Category.INFO.value, "Starting robot on path!"))
                else:
                    logger.warning("The command queue is empty, please set obstacles.")
                    self.android_queue.put(
                        AndroidMessage(Category.ERROR.value, "Command queue empty (no obstacles)")
                    )

    def command_follower(self) -> None:
        """
        [Child Process]
        """
        while True:
            self.unpause.wait()

            command: str = self.command_queue.get()
            logger.debug(f"command dequeued: {command}")

            logger.debug(f"command for movement lock: {command}")
            if command.startswith(stm32_prefixes):
                strings = str(command)
                parts = strings.split("|")
                self.outstanding_stm_instructions.set(self.outstanding_stm_instructions.get() + 1)
                self.stm_link.send_cmd(parts[0][0], int(parts[0][1:]), float(parts[1]), float(parts[2]))
                logger.debug(f"Sending to STM32: {command}")

            elif command.startswith("SNAP"):
                obstacle_id_with_signal = command.replace("SNAP", "")
                self.rpi_action_queue.put(PiAction(cat=Category.SNAP, value=obstacle_id_with_signal))
                self.unpause.clear()
            
            elif command == "stall":
                logger.info("stalling robot")
                while self.outstanding_stm_instructions.get() != 0:
                    pass
                time.sleep(STALL_TIME)
                logger.info("stall complete")
                self.unpause.set()

            elif command == Category.FIN.value:
                while self.outstanding_stm_instructions.get() != 0:
                    pass
                logger.info(f"At FIN->self.current_location: {self.current_location}")
                self.completed = True
                if self.ANDRIOD_CONTROLLER:
                    self.android_queue.put(AndroidMessage(Category.STATUS.value, "finished"))
                self.unpause.clear()
                logger.debug("unpause cleared")
                logger.info("Commands queue finished.")
                self.rpi_action_queue.put(PiAction(cat=Category.STITCH, value=""))
                self.finish_all.wait()
                self.finish_all.clear()
                logger.debug("All processes up to stich finished")
                break
            else:
                raise Exception(f"Unknown command: {command}")

    def recv_stm(self) -> None:
        """
        [Child Process] Receive acknowledgement messages from STM32, and release the movement lock
        """
        while True:
            message: str = self.stm_link.wait_receive()

            try:
                if message.startswith("f"):
                    logger.debug(f"stm finish {message}")
                    outstanding_stm_instructions = self.outstanding_stm_instructions.get()
                    self.outstanding_stm_instructions.set(outstanding_stm_instructions - 1)
                    if outstanding_stm_instructions - 1 == 0 and self.snap_pending.get() == 1:
                        logger.info("clear unpause")
                        self.ready_snap.set()
                        # self.unpause.clear()
                    logger.debug(f"stm finish {message}, outstanding is {outstanding_stm_instructions - 1}")
                    
                elif message.startswith("r"):
                    logger.debug(f"stm ack {message}")
                elif message.startswith ("D"):
                    logger.debug(f"stm reporting dist {message}")
                    outstanding_stm_instructions = self.outstanding_stm_instructions.get()
                    self.outstanding_stm_instructions.set(outstanding_stm_instructions - 1)
                    logger.debug(f"stm message split {message.split('D')}")
                    detected_dist = int(eval(message.split("D")[1].lstrip().split("\n")[0]))
                    if detected_dist > 0:
                        detected_dist += 20
                    self.second_obstacle_dist.set(detected_dist)
                    logger.info(f"we eating D at {self.second_obstacle_dist.get()}")
                else:
                    logger.error(f"Ignored unknown message from STM: {message}")
                    outstanding_stm_instructions = self.outstanding_stm_instructions.get()
                    self.outstanding_stm_instructions.set(outstanding_stm_instructions - 1)
            except Exception as e:
                logger.error(f"Error in recv_stm: {e}")

    def recognize_image(self, obstacle_id_with_signal: str) -> str:
        """
        RPi snaps an image and calls the API for image-rec.
        The response is then forwarded back to the android

        :param obstacle_id_with_signal: eg: SNAP<obstacle_id>_<C/L/R>
        """
        obstacle_id, signal = obstacle_id_with_signal.split("_")
        logger.info(f"Capturing image for obstacle id: {obstacle_id}")
        url = f"{URL}/image"

        filename = f"/home/rpi21/cam/{int(time.time())}_{obstacle_id}_{signal}.jpg"
        filename_send = f"{int(time.time())}_{obstacle_id}_{signal}.jpg"
        results = snap_using_picamera2(
            filename=filename,
            filename_send=filename_send,
            url=url,
        )
        logger.info(results)
        return results

    def request_stitch(self) -> None:
        """Sends stitch request to the image recognition API to stitch the different images together

        if the API is down, an error message is sent to the Android
        """
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.get(url=f"{URL}/stitch", timeout=API_TIMEOUT)
            if response.status_code != 200:
                logger.error(f"Error when requesting stitch from the API. Attempt {attempt + 1} of {max_retries}")
                continue
            logger.info("Images stitched!")
            self.finish_all.set()
            return

        logger.error("Failed to request stitch from the API after multiple attempts.")
