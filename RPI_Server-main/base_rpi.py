import json
import logging
import os
import queue
import time
from multiprocessing import Manager, Process
from typing import Optional

import requests
from communication.android import AndroidLink, AndroidMessage
from communication.pi_action import PiAction
from communication.stm32 import STMLink
from constant.consts import SYMBOL_MAP
from constant.settings import API_IP, API_PORT


logger = logging.getLogger(__name__)


class RaspberryPi:
    def __init__(self) -> None:
        """
        Initializes the Raspberry Pi.
        """
        self.android_link = AndroidLink()
        self.stm_link = STMLink()

        self.manager = Manager()

        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        self.movement_lock = self.manager.Lock()  # locks the movement

        #       self.retrylock = self.manager.Lock() #locks the retry

        self.android_queue = self.manager.Queue()  # Messages to send to Android
        # Messages that need to be processed by RPi
        self.rpi_action_queue = self.manager.Queue()
        # Messages that need to be processed by STM32, as well as snap commands
        self.command_queue = self.manager.Queue()
        # X,Y,D coordinates of the robot passed from the command_queue
        self.path_queue = self.manager.Queue()

        self.proc_recv_android = None  # recieve android
        self.proc_recv_stm32 = None  # recieve stm
        self.proc_android_sender = None  # subprocess to send to androi
        self.proc_command_follower = None  # commands given by the algo
        self.proc_rpi_action = None  # proc action
        self.rs_flag = False
        self.success_obstacles = self.manager.list()
        self.failed_obstacles = self.manager.list()
        self.obstacles = self.manager.dict()
        self.current_location = self.manager.dict()
        self.failed_attempt = False

    def stop(self) -> None:
        """Stops all processes on the RPi and disconnects with Android and STM32"""
        self.android_link.disconnect()
        self.stm_link.disconnect()
        self.clear_queues()
        logger.info("Program exited!")

    def reconnect_android(self):
        """Handles the reconnection to Android in the event of a lost connection."""
        logger.info("Reconnection handler is watching...")

        while True:
            # Wait for android connection to drop
            self.android_dropped.wait()

            logger.error("Android is down")

            # Kill child processes
            logger.debug("Stopping android child processes")
            self.proc_android_sender.kill()
            self.proc_recv_android.kill()

            # Wait for the child processes to finish
            self.proc_android_sender.join()
            self.proc_recv_android.join()
            assert self.proc_android_sender.is_alive() is False
            assert self.proc_recv_android.is_alive() is False
            logger.debug("Android process stopped")

            # Clean up old sockets
            self.android_link.disconnect()
            self.android_link.connect()

            # Recreate Android processes
            self.proc_recv_android = Process(target=self.recv_android)
            self.proc_android_sender = Process(target=self.android_sender)
            self.proc_recv_android.start()
            self.proc_android_sender.start()

            logger.info("Android processes restarted")
            self.android_queue.put(AndroidMessage("info", "You are reconnected!"))
            self.android_queue.put(AndroidMessage("mode", "path"))

            self.android_dropped.clear()

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
            logger.warning("API Connection Error")
            return False
        except requests.Timeout:
            logger.warning("API Timeout")
            return False
        except Exception as e:
            logger.warning(f"API Exception: {e}")
            return False
