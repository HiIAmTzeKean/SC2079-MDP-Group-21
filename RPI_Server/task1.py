import json
import logging
import queue
import time
from multiprocessing import Process
from typing import Optional

import requests
from base_rpi import RaspberryPi
from communication.android import AndroidMessage
from communication.camera import snap_using_libcamera
from communication.pi_action import PiAction
from constant.consts import Category, manual_commands, stm32_prefixes
from constant.settings import API_IP, API_PORT


logger = logging.getLogger(__name__)


class TaskOne(RaspberryPi):
    def __init__(self) -> None:
        super().__init__()

    def start(self) -> None:
        """Starts the RPi orchestrator"""
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

            self.android_queue.put(AndroidMessage("info", "Robot is ready!"))
            self.android_queue.put(AndroidMessage("mode", "path"))

            # TODO check why reconnect again
            # self.reconnect_android()
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
                for obs in action.value[Category.OBSTACLE.value]:
                    self.obstacles[obs["id"]] = obs
                self.request_algo(action.value)

            elif action.cat == "snap":
                self.recognize_image(obstacle_id_with_signal=action.value)

            elif action.cat == "stitch":
                self.request_stitch()

    # TODO
    def command_follower(self) -> None:
        """
        [Child Process]
        """
        while True:
            command: str = self.command_queue.get()
            logger.debug(f"Command Dequeued: {command}")

            # Wait for unpause event to be true [Main Trigger]
            self.unpause.wait()

            # Acquire lock first (needed for both moving, and snapping pictures)
            logger.debug("Acquiring movement lock...")
            self.movement_lock.acquire()

            logger.debug(f"Getting Prefix: {command}")
            if command.startswith(stm32_prefixes):
                strings = str(command)
                # strings += "\n"
                parts = strings.split("|")
                first_part = parts[0]
                flag = first_part[0]
                speed = int(first_part[1:])
                angle = int(parts[1])
                val = int(parts[2])

                self.stm_link.send_cmd(flag, speed, angle, val)
                logger.debug(f"Sending to STM32: {command}")

            elif command.startswith("SNAP"):
                obstacle_id_with_signal = command.replace("SNAP", "")

                self.rpi_action_queue.put(PiAction(cat=Category.SNAP, value=obstacle_id_with_signal))
                time.sleep(1)
                try:
                    self.movement_lock.release()
                    logger.debug(f"movement_lock and retrylock released")
                except:
                    pass

            elif command == "FIN":
                logger.info(
                        f"At FIN, self.failed_obstacles: {self.failed_obstacles}"
                        f"\nself.current_location: {self.current_location}"
                )
                self.unpause.clear()
                logger.debug("unpause cleared")
                try:
                    logger.debug("releasing movement_lock.")
                    self.movement_lock.release()
                except:
                    pass
                logger.info("Commands queue finished.")
                self.android_queue.put(AndroidMessage("status", "finished"))
                self.rpi_action_queue.put(PiAction(cat=Category.STITCH, value=""))
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
            self.android_queue.put(AndroidMessage("info", "You are reconnected!"))
            self.android_queue.put(AndroidMessage("mode", "path"))

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
            except queue.Empty:
                logger.debug("Queue Empty!")
                continue

            try:
                self.android_link.send(message)
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

            # TODO check what is fD
            if message.startswith("fD"):
                logger.debug("fD from STM32 received.")
                cur_location = self.path_queue.get_nowait()
                logger.debug("Goes through cur_location")
                logger.debug(f"Value of cur_location: {cur_location}")

                self.current_location["x"] = cur_location["x"]
                self.current_location["y"] = cur_location["y"]
                self.current_location["d"] = cur_location["d"]
                logger.info(f"self.current_location = {self.current_location}")
                self.android_queue.put(
                    AndroidMessage(
                        "location",
                        {
                            "x": cur_location["x"],
                            "y": cur_location["y"],
                            "d": cur_location["d"],
                        },
                    )
                )
                try:
                    logger.debug("fD from STM32 received, releasing movement lock and retrylock.")
                    self.movement_lock.release()
                except:
                    pass
            else:
                logger.warning(f"Ignored unknown message from STM: {message}")
                try:
                    logger.debug("unknown message from STM32 received, releasing movement lock and retrylock.")
                    self.movement_lock.release()
                except:
                    pass

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
                continue

            message: dict = json.loads(android_str)

            ## Command: Set obstacles ##
            if message["cat"] == Category.OBSTACLE.value:
                self.rpi_action_queue.put(PiAction(**message))
                logger.debug(f"PiAction obstacles appended to queue: {message}")

            elif message["cat"] == Category.MANUAL.value:
                command = manual_commands.get(message["value"])
                if not command:
                    logger.error("Invalid manual command!")
                self.stm_link.send_cmd(*command)
                
            ## Command: Start Moving ##
            # TODO check with android team if they want to use control
            elif message["cat"] == "control":
                if message["value"] == "start":
                    # Check API
                    # TODO handle the error
                    if not self.check_api():
                        logger.error("API is down! Start command aborted.")
                        self.android_queue.put(AndroidMessage("error", "API is down, start command aborted."))

                    # Commencing path following
                    if not self.command_queue.empty():
                        self.unpause.set()
                        
                        logger.info("Start command received, starting robot on path!")
                        self.android_queue.put(AndroidMessage("info", "Starting robot on path!"))
                        self.android_queue.put(AndroidMessage("status", "running"))
                    else:
                        logger.warning("The command queue is empty, please set obstacles.")
                        self.android_queue.put(AndroidMessage("error", "Command queue empty (no obstacles)"))

    # TODO fix this section
    def recognize_image(self, obstacle_id_with_signal: str) -> None:
        """
        RPi snaps an image and calls the API for image-rec.
        The response is then forwarded back to the android

        :param obstacle_id_with_signal: eg: SNAP<obstacle_id>_<C/L/R>
        """
        obstacle_id, signal = obstacle_id_with_signal.split("_")
        logger.info(f"Capturing image for obstacle id: {obstacle_id}")
        self.android_queue.put(AndroidMessage("info", f"Capturing image for obstacle id: {obstacle_id}"))
        url = f"http://{API_IP}:{API_PORT}/image"

        filename = f"/home/pi/cam/{int(time.time())}_{obstacle_id}_{signal}.jpg"
        filename_send = f"{int(time.time())}_{obstacle_id}_{signal}.jpg"
        results = snap_using_libcamera(
            obstacle_id=obstacle_id,
            signal=signal,
            filename=filename,
            filename_send=filename_send,
            url=url,
            auto_callibrate=False,
        )
        self.android_queue.put(AndroidMessage(cat=Category.IMAGE_REC.value, value=results))

    def request_algo(self, data, robot_x=1, robot_y=1, robot_dir=0, retrying=False) -> None:
        """
        Requests for a series of commands and the path from the Algo API.
        The received commands and path are then queued in the respective queues
        """
        logger.info("Requesting path from algo...")
        # TODO check if line below is needed
        self.android_queue.put(AndroidMessage(cat=Category.INFO.value, value="Requesting path from algo..."))

        logger.info(f"data: {data}")
        body = {
            **data,
            "big_turn": "0",
            "robot_x": robot_x,
            "robot_y": robot_y,
            "robot_dir": robot_dir,
            "retrying": retrying,
        }

        response = requests.post(url=f"http://{API_IP}:{API_PORT}/path", json=body)

        # TODO if the response fails, we should retry
        if response.status_code != 200:
            self.android_queue.put(AndroidMessage("error", "Error when requesting path from Algo API."))
            logger.error("Error when requesting path from Algo API.")
            return

        # Parse response
        result = json.loads(response.content)["data"]
        commands = result["commands"]
        path = result["path"]

        # Log commands received
        logger.debug(f"Commands received from API: {commands}")

        # Put commands and paths into respective queues
        self.clear_queues()
        for c in commands:
            self.command_queue.put(c)
        for p in path[1:]:  # ignore first element as it is the starting position of the robot
            self.path_queue.put(p)

        self.android_queue.put(
            AndroidMessage(
                cat=Category.INFO.value,
                value="Commands and path received Algo API. Robot is ready to move.",
            )
        )
        logger.info("Commands and path received Algo API. Robot is ready to move.")

    def request_stitch(self) -> None:
        """Sends stitch request to the image recognition API to stitch the different images together

        if the API is down, an error message is sent to the Android
        """
        response = requests.get(f"http://{API_IP}:{API_PORT}/stitch")

        if response.status_code != 200:
            self.android_queue.put(AndroidMessage(Category.ERROR.value, "Error when requesting stitch from the API."))
            logger.error("Error when requesting stitch from the API.")
            return

        logger.info("Images stitched!")
        self.android_queue.put(AndroidMessage("info", "Images stitched!"))
