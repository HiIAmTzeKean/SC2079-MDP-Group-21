import json
import logging
import queue
import time
from multiprocessing import Process
from typing import Any, Optional

import requests

from ..base_rpi import RaspberryPi
from ..communication.android import AndroidMessage
from ..communication.camera import snap_using_libcamera, snap_using_picamera
from ..communication.pi_action import PiAction
from ..constant.consts import Category, manual_commands, stm32_prefixes
from ..constant.settings import URL


logger = logging.getLogger(__name__)


class TaskA5(RaspberryPi):
    def __init__(self) -> None:
        super().__init__()

    def start(self) -> None:
        """Starts the RPi orchestrator"""
        logger.info("starting the start function")
        try:
            ### Start up initialization ###
            self.android_link.connect()
            self.android_queue.put(AndroidMessage(cat="info", value="You are connected to the RPi!"))
            self.stm_link.connect()
            self.check_api()

            # Define child processes
            self.proc_recv_android = Process(target=self.recv_android)
            self.proc_recv_stm32 = Process(target=self.recv_stm)
            self.proc_android_controller = Process(target=self.android_controller)
            self.proc_command_follower = Process(target=self.command_follower)
            self.proc_rpi_action = Process(target=self.rpi_action)

            # Start child processes
            self.proc_recv_android.start()
            self.proc_recv_stm32.start()
            self.proc_android_controller.start()
            self.proc_command_follower.start()
            self.proc_rpi_action.start()

            logger.info("Child Processes started")

            self.android_queue.put(AndroidMessage(Category.INFO.value, "Robot is ready!"))
            self.android_queue.put(AndroidMessage(Category.MODE.value, "path"))
            
            # Reconnect Android if connection is lost
            # Handled in main process
            self.reconnect_android()
        except KeyboardInterrupt:
            self.stop()

    def rpi_action(self) -> None:
        """
        [Child Process] For processing the actions that the RPi needs to take.
        """
        while True:
            action = self.rpi_action_queue.get()
            logger.debug(f"PiAction retrieved from queue: {action.cat} {action.value}")
            ## obstacle ID
            if action.cat == Category.OBSTACLE.value:
                # for _ in action.value[Category.OBSTACLE.value]:
                #     self.obstacles += 1
                self.current_location["x"] = int(action.value["robot_x"])
                self.current_location["y"] = int(action.value["robot_y"])
                self.current_location["d"] = int(action.value["robot_dir"])
                self.request_algo(action.value)

            elif action.cat == Category.SNAP.value:
                # while True:
                #     # wait for all STM instructions to finish
                #     with self.outstanding_stm_instructions.get_lock():
                #         if self.outstanding_stm_instructions.value == 0:
                #             break
                self.recognize_image(obstacle_id_with_signal=action.value)

            elif action.cat == Category.STITCH.value:
                # while True:
                    # wait for all STM instructions to finish
                    # with self.obstacles.get_lock():
                    #     if self.outstanding_stm_instructions.value == 0:
                    #         break
                self.request_stitch()

    # TODO
    def command_follower(self) -> None:
        """
        [Child Process]
        """
        while True:
            command: str = self.command_queue.get()
            logger.debug(f"command dequeued: {command}")

            self.unpause.wait()

            # Acquire lock first (needed for both moving, and snapping pictures)
            logger.debug("Acquiring movement lock...")
            self.movement_lock.acquire()

            logger.debug(f"command for movement lock: {command}")
            if command.startswith(stm32_prefixes):
                strings = str(command)
                # t|100|100|100
                parts = strings.split("|")
                self.stm_link.send_cmd(parts[0][0], int(parts[0][1:]), int(parts[1]), int(parts[2]))
                logger.debug(f"Sending to STM32: {command}")

            elif command.startswith("SNAP"):
                obstacle_id_with_signal = command.replace("SNAP", "")

                self.rpi_action_queue.put(PiAction(cat=Category.SNAP, value=obstacle_id_with_signal))
                time.sleep(1)

            elif command == Category.FIN.value:
                logger.info(f"At FIN->self.current_location: {self.current_location}")
                self.unpause.clear()
                logger.debug("unpause cleared")
                try:
                    logger.debug("releasing movement_lock.")
                    self.movement_lock.release()
                except:
                    pass
                logger.info("Commands queue finished.")
                self.android_queue.put(AndroidMessage(Category.STATUS.value, "finished"))
                self.rpi_action_queue.put(PiAction(cat=Category.STITCH, value=""))
                self.finish_all.wait()
                self.finish_all.clear()
                logger.debug("All processes up to stich finished")
                self.stop()
            else:
                raise Exception(f"Unknown command: {command}")

    def reconnect_android(self) -> None:
        """Handles the reconnection to Android in the event of a lost connection."""
        logger.info("Reconnection handler is watching...")

        while True:
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
                # blocks for 0.5 seconds to check if there are any messages
                # in the queue
                message = self.android_queue.get(timeout=0.5)
                self.android_link.send(message)
            except queue.Empty:
                continue
            except OSError:
                self.android_dropped.set()
                logger.error("OSError. Event set: Android dropped")
            except Exception as e:
                logger.error(f"Error sending message to Android: {e}")

    def recv_stm(self) -> None:
        """
        [Child Process] Receive acknowledgement messages from STM32, and release the movement lock
        """
        while True:
            message: str = self.stm_link.wait_receive()
            
            try:
                if message.startswith("f"):
                    cur_location = self.path_queue.get_nowait()

                    self.current_location["x"] = cur_location["x"]
                    self.current_location["y"] = cur_location["y"]
                    self.current_location["d"] = cur_location["d"]
                    logger.info(f"current location = {self.current_location}")
                    self.android_queue.put(
                        AndroidMessage(
                            Category.LOCATION.value,
                            {
                                "x": cur_location["x"],
                                "y": cur_location["y"],
                                "d": cur_location["d"],
                            },
                        )
                    )
                    logger.debug(f"stm finish {message}")
                    logger.info("Releasing movement lock.")
                    self.movement_lock.release()
                elif message.startswith("r"):
                    logger.debug(f"stm ack {message}")
                else:
                    logger.warning(f"Ignored unknown message from STM: {message}")
            except Exception as e:
                logger.error(f"Error in recv_stm: {e}")
                 
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

            ## Command: Set obstacles ##
            logger.info(f"message obtained is {message['cat']}")
            if message["cat"] == Category.OBSTACLE.value:
                self.rpi_action_queue.put(PiAction(cat=Category.OBSTACLE, value=message["value"]))
                logger.debug(f"PiAction obstacles appended to queue: {message}")

            elif message["cat"] == Category.MANUAL.value:
                command = manual_commands.get(message["value"])
                if command is None:
                    logger.error("Invalid manual command!")
                self.stm_link.send_cmd(**command)
                
            ## Command: Start Moving ##
            elif message["cat"] == "control":
                if message["value"] == "start":
                    # Commencing path following
                    if not self.command_queue.empty():
                        self.unpause.set()
                        
                        logger.info("Start command received, starting robot on path!")
                        self.android_queue.put(AndroidMessage(Category.INFO.value, "Starting robot on path!"))
                    else:
                        logger.warning("The command queue is empty, please set obstacles.")
                        self.android_queue.put(AndroidMessage(Category.ERROR.value, "Command queue empty (no obstacles)"))

    # TODO fix the library camera call
    def recognize_image(self, obstacle_id_with_signal: str) -> None:
        """
        RPi snaps an image and calls the API for image-rec.
        The response is then forwarded back to the android

        :param obstacle_id_with_signal: eg: SNAP<obstacle_id>_<C/L/R>
        """
        obstacle_id, signal = obstacle_id_with_signal.split("_")
        logger.info(f"Capturing image for obstacle id: {obstacle_id}")
        self.android_queue.put(AndroidMessage(Category.INFO.value, f"Capturing image for obstacle id: {obstacle_id}"))
        url = f"{URL}/image"

        filename = f"/home/rpi21/cam/{int(time.time())}_{obstacle_id}_{signal}.jpg"
        filename_send = f"{int(time.time())}_{obstacle_id}_{signal}.jpg"
        results = snap_using_picamera(
            obstacle_id=obstacle_id,
            signal=signal,
            filename=filename,
            filename_send=filename_send,
            url=url,
            # auto_callibrate=False,
        )
        self.android_queue.put(AndroidMessage(Category.IMAGE_REC.value, value=results))
        if results["image_id"] != "NA":
            self.stop()
            time.sleep(100)
        self.movement_lock.release()
        

    # TODO implement retrying flag
    def request_algo(self, data: dict, retrying=False) -> None:
        """
        Requests for a series of commands and the path from the Algo API.
        The received commands and path are then queued in the respective queues
        """
        logger.debug("Requesting path from algo")
        self.android_queue.put(AndroidMessage(cat=Category.INFO.value, value="Requesting path from algo..."))

        body = {
            **data,
            "robot_x": 10,
            "robot_y": 1,
            "robot_dir": 0,
            "retrying": retrying,
        }
        logger.debug(f"{body}")
        response = requests.post(url=f"{URL}/path", json=body, timeout=3.0)

        if response.status_code != 200:
            logger.error("Error when requesting path from Algo API.")
            self.android_queue.put(AndroidMessage(Category.ERROR.value, "Error when requesting path from Algo API."))
            return

        result = json.loads(response.content)["data"]
        commands = result["commands"]
        path = result["path"]
        logger.debug(f"Commands received from API: {commands}")
        
        self.clear_queues()

        if commands == []:
            logger.error("Command queue is empty")
            return

        for c in commands:
            self.command_queue.put(c)
            
        for p in path:
            self.path_queue.put(p)

        self.android_queue.put(
            AndroidMessage(
                cat=Category.INFO.value,
                value="Commands and path received Algo API. Robot is ready to move.",
            )
        )
        logger.info("Robot is ready to move.")

    def request_stitch(self) -> None:
        """Sends stitch request to the image recognition API to stitch the different images together

        if the API is down, an error message is sent to the Android
        """
        response = requests.get(url=f"{URL}/stitch", timeout=2.0)

        # TODO should retry if the response fails
        if response.status_code != 200:
            self.android_queue.put(AndroidMessage(Category.ERROR.value, "Error when requesting stitch from the API."))
            logger.error("Error when requesting stitch from the API.")
            return

        self.android_queue.put(AndroidMessage(Category.INFO.value, "Images stitched!"))
        logger.info("Images stitched!")
        self.finish_all.set()
