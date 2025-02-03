import json
import logging
import queue
from multiprocessing import Process
from typing import Optional

from base_rpi import RaspberryPi
from communication.android import AndroidMessage
from communication.pi_action import PiAction
from constant.consts import Category, manual_commands


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

            ### Start up complete ###

            # Send success message to Android
            self.android_queue.put(AndroidMessage("info", "Robot is ready!"))
            self.android_queue.put(AndroidMessage("mode", "path"))

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
            if action.cat == "obstacles":
                for obs in action.value["obstacles"]:
                    self.obstacles[obs["id"]] = obs
                self.request_algo(action.value)
            ## snap image
            elif action.cat == "snap":
                self.recognise_image(obstacle_id_with_signal=action.value)
            ## stitch
            elif action.cat == "stitch":
                self.request_stitch()

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

            if message.startswith("fD"):
                logger.debug("fD from STM32 received.")
                logger.debug(f"Get current queue: {self.command_queue.qsize()}")
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
                    logger.debug("In recv_stm: fD from STM32 received, releasing movement lock and retrylock.")
                    self.movement_lock.release()
                except:
                    pass
            else:
                logger.warning(f"In recv_stm: Ignored unknown message from STM: {message}")
                try:
                    logger.debug(
                        "In recv_stm: unkown message from STM32 received, releasing movement lock and retrylock."
                    )
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

            elif message["cat"] == "manual":
                command = manual_commands.get(message["value"])
                if command:
                    self.stm_link.send_cmd(*command)
                else:
                    logger.error("Invalid manual command!")
                continue

            ## Command: Start Moving ##
            elif message["cat"] == "control":
                if message["value"] == "start":
                    # Check API
                    if not self.check_api():
                        logger.error("In recv_android: API is down! Start command aborted.")
                        self.android_queue.put(AndroidMessage("error", "API is down, start command aborted."))

                    # Commencing path following
                    if not self.command_queue.empty():
                        logger.info("Gryo reset!")
                        # self.stm_link.send("RS00")
                        # Main trigger to start movement #
                        self.unpause.set()
                        logger.info("In recv_android: Start command received, starting robot on path!")
                        self.android_queue.put(AndroidMessage("info", "Starting robot on path!"))
                        self.android_queue.put(AndroidMessage("status", "running"))
                    else:
                        logger.warning("In recv_android: The command queue is empty, please set obstacles.")
                        self.android_queue.put(
                            AndroidMessage("error", "Command queue is empty, did you set obstacles?")
                        )
