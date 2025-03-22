import json
import logging
import queue
import time
from multiprocessing import Process
from typing import Any, Optional

import requests

import os
import sys

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
        self.unpause.clear()
        self.clear_queues()
        logger.debug("All ready")
        try:
            self.stm_link.connect()

            # Define child processes
            self.proc_recv_android = Process(target=self.recv_android)
            self.proc_command_follower = Process(target=self.command_follower)
            self.proc_recv_stm32 = Process(target=self.recv_stm)
            self.proc_rpi_action = Process(target=self.rpi_action)

            # Start child processes
            self.proc_recv_android.start()
            self.proc_recv_stm32.start()
            self.proc_command_follower.start()
            self.proc_rpi_action.start()

            logger.info("Child Processes started")
            while True:
                continue
        except Exception as e:
            pass

    def rpi_action(self) -> None:
        """
        [Child Process] For processing the actions that the RPi needs to take.
        """
        while True:
            try:
                action = self.rpi_action_queue.get()
            except Exception as e:
                continue
            
            logger.debug(f"PiAction retrieved from queue: {action.cat} {action.value}")
            ## obstacle ID
            if action.cat == Category.OBSTACLE.value:
                self.request_algo({})

            elif action.cat == Category.SNAP.value:
                self.recognize_image(obstacle_id_with_signal=action.value)

            elif action.cat == Category.STITCH.value:
                self.request_stitch()

    # TODO
    def command_follower(self) -> None:
        """
        [Child Process]
        """
        while True:
            self.unpause.wait()
            
            command: str = self.command_queue.get()
            logger.debug(f"command dequeued: {command}")

            logger.debug("Acquiring movement lock...")
            self.movement_lock.acquire()
            if command.startswith(stm32_prefixes):
                strings = str(command)
                # t|100|100|100
                parts = strings.split("|")
                self.stm_link.send_cmd(parts[0][0], int(parts[0][1:]), float(parts[1]), float(parts[2]))
                logger.debug(f"Sending to STM32: {command}")

            elif command.startswith("SNAP"):
                obstacle_id_with_signal = command.replace("SNAP", "")
                self.rpi_action_queue.put(PiAction(cat=Category.SNAP, value=obstacle_id_with_signal))

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
                # self.android_queue.put(AndroidMessage(Category.STATUS.value, "finished"))
                self.rpi_action_queue.put(PiAction(cat=Category.STITCH, value=""))
                self.finish_all.wait()
                self.finish_all.clear()
                logger.debug("All processes up to stich finished")
                self.stop()
            else:
                raise Exception(f"Unknown command: {command}")


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
        self.rpi_action_queue.put(PiAction(cat=Category.OBSTACLE, value=""))
        logger.debug("PiAction obstacles obtained")

    def recognize_image(self, obstacle_id_with_signal: str) -> None:
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
        results = snap_using_picamera(
            obstacle_id=obstacle_id,
            signal=signal,
            filename=filename,
            filename_send=filename_send,
            url=url,
            # auto_callibrate=False,
        )
        
        ## Checklist component
        self.movement_lock.release()
        
    def request_algo(self, data: dict, retrying=False) -> None:
        """
        Requests for a series of commands and the path from the Algo API.
        The received commands and path are then queued in the respective queues
        """
        logger.debug("Requesting path from algo")
        
        self.check_api()
        
        # incase android cannot support we will use this
        data = {
            "obstacles": [
                {
                "x": 1,
                "y": 11,
                "d": 4,
                "id": 0
                },
                {
                "x": 19,
                "y": 9,
                "d": 6,
                "id": 1
                }
            ],
            "retrying": False,
            "robot_dir": 0,
            "robot_x": 1,
            "robot_y": 1
        }

        body = {
            **data,
            "robot_x": data["robot_x"],
            "robot_y": data["robot_y"],
            "robot_dir": data["robot_dir"],
            "retrying": retrying,
        }
        logger.debug(f"{body}")
        response = requests.post(url=f"{URL}/path", json=body, timeout=10.0)

        if response.status_code != 200:
            logger.error("Error when requesting path from Algo API.")
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
        
        logger.info("Robot is ready to move.")
        self.unpause.set()

    def request_stitch(self) -> None:
        """Sends stitch request to the image recognition API to stitch the different images together

        if the API is down, an error message is sent to the Android
        """
        response = requests.get(url=f"{URL}/stitch", timeout=2.0)

        # TODO should retry if the response fails
        if response.status_code != 200:
            logger.error("Error when requesting stitch from the API.")
            return

        logger.info("Images stitched!")
        self.finish_all.set()
