import json
import logging
import queue
import time
from multiprocessing import Process
from typing import Any, Optional

import requests

from .base_rpi import RaspberryPi
from .communication.camera import snap_using_libcamera, snap_using_picamera2
from .communication.pi_action import PiAction
from .constant.consts import Category, manual_commands, stm32_prefixes
from .constant.settings import URL


logger = logging.getLogger(__name__)


class TaskTwo(RaspberryPi):
    def __init__(self) -> None:
        super().__init__()
        del self.path_queue
        del self.android_queue
        del self.android_link
        self.first_obstacle = True
        self.ready_snap = self.manager.Event()
        """Event to indicate that ready to snap"""

    def start(self) -> None:
        """Starts the RPi orchestrator"""
        logger.info("starting the start function")
        try:
            self.stm_link.connect()
            self.check_api()

            self.proc_recv_stm32 = Process(target=self.recv_stm)
            self.proc_command_follower = Process(target=self.command_follower)
            self.proc_rpi_action = Process(target=self.rpi_action)
            self.unpause.set()
            self.proc_recv_stm32.start()
            self.proc_command_follower.start()
            self.proc_rpi_action.start()

            self.set_actions()

            action_list_init = [
                "frontuntil"
            ]

            self.action_list_first_left = [
                "half_left",
                "half_right",
                "frontuntil"
            ]
            self.action_list_first_right = [
                "half_right",
                "half_left",
                "left_correct",
                "frontuntil"
            ]            
            self.action_list_second_left = [
                "W60|0|35",
                "left", #robot 15cm apart from wall, 20cm turn radius
                "R60|0|30",
                "T30|58|183",
                "r60|0|30", #15cm apart from wall on opposite side
                "R60|0|30",
                "right",
                "T60|0|20",
                "r60|0|50",
                "half_right",
                "R60|0|40",
                "r60|0|30",
                "half_left",
                "left_correct",
                "W60|0|15"
            ]
            self.action_list_second_right = [
                "W60|0|35",
                "right",
                "L60|0|30",
                "T30|-60.5|183",
                "l60|0|30",
                "L60|0|30",
                "left",
                "left_correct",
                "T60|0|20",
                "l60|0|50",
                "half_left",
                "left_correct",
                "L60|0|40",
                "l60|0|30",
                "half_right",
                "W60|0|15"
            ]

            logger.info("Child Processes started")
            # self.proc_android_controller.join()
            self.proc_recv_stm32.join()
            self.proc_command_follower.joina()
            self.proc_rpi_action.join()
        except KeyboardInterrupt:
            self.stop()

    def set_actions(self, action_list) -> None:
        """Sets the actions for the RPi"""
        for action in action_list:
            if action.startswith("SNAP"):
                self.command_queue.put(action)
                continue
            elif manual_commands.get(action) is None:
                # specify custom
                self.command_queue.put(action)
                continue
            elif action == "FIN":
                self.command_queue.put(Category.FIN.value)
                continue
            elif type(manual_commands[action]) == tuple:
                self.command_queue.put(manual_commands[action][0])
                self.command_queue.put(manual_commands[action][1])
                continue
            self.command_queue.put(manual_commands[action])

    def rpi_action(self) -> None:
        """
        [Child Process] For processing the actions that the RPi needs to take.
        """
        while True:
            action = self.rpi_action_queue.get()
            logger.debug(
                f"PiAction retrieved from queue: {action.cat} {action.value}")
            if action.cat == Category.SNAP.value:
                self.ready_snap.wait()
                results = self.recognize_image(
                    obstacle_id_with_signal=action.value)

                if self.first_obstacle:
                    self.first_obstacle = False
                    if results["image_id"] == "38":  # right
                        self.set_actions(self.action_list_first_left)
                    else:
                        self.set_actions(self.action_list_first_right)
                else:
                    # obstacle 2
                    if results["image_id"] == "38":
                        self.set_actions(self.action_list_second_right)
                    else:
                        self.set_actions(self.action_list_second_right)

                self.ready_snap.clear()
                self.unpause.set()
            elif action.cat == Category.STITCH.value:
                self.request_stitch()

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
                self.outstanding_stm_instructions.set(
                    self.outstanding_stm_instructions.get()+1)
                self.stm_link.send_cmd(parts[0][0], int(
                    parts[0][1:]), float(parts[1]), float(parts[2]))
                logger.debug(f"Sending to STM32: {command}")

            elif command.startswith("SNAP"):
                obstacle_id_with_signal = command.replace("SNAP", "")
                self.rpi_action_queue.put(
                    PiAction(cat=Category.SNAP, value=obstacle_id_with_signal))
                self.unpause.clear()

            elif command == Category.FIN.value:
                logger.info(
                    f"At FIN->self.current_location: {self.current_location}")
                self.unpause.clear()
                logger.debug("unpause cleared")
                logger.info("Commands queue finished.")
                self.rpi_action_queue.put(
                    PiAction(cat=Category.STITCH, value=""))
                self.finish_all.wait()
                self.finish_all.clear()
                logger.debug("All processes up to stich finished")
                self.stop()
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
                    if outstanding_stm_instructions - 1 == 0:
                        self.ready_snap.set()
                        self.unpause.clear()
                    self.outstanding_stm_instructions.set(
                        outstanding_stm_instructions - 1)
                    logger.debug(f"stm finish {message}")
                    logger.info("Releasing movement lock.")
                elif message.startswith("r"):
                    logger.debug(f"stm ack {message}")
                else:
                    logger.warning(
                        f"Ignored unknown message from STM: {message}")
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
            obstacle_id=obstacle_id,
            signal=signal,
            filename=filename,
            filename_send=filename_send,
            url=url,
            # auto_callibrate=False,
        )
        return results

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
