import logging
import multiprocessing as mp
from abc import ABC, abstractmethod
from multiprocessing import Manager, Process
from queue import Queue

import requests

from .communication.android import AndroidLink, AndroidMessage
from .communication.pi_action import PiAction
from .communication.stm32 import STMLink
from .constant.settings import API_IP, API_PORT


logger = logging.getLogger(__name__)


class RaspberryPi(ABC):
    def __init__(self) -> None:
        """
        Initializes the Raspberry Pi.
        """
        self.android_link = AndroidLink()
        self.stm_link = STMLink()

        self.manager = Manager()

        self.android_dropped = self.manager.Event()
        """Event to indicate that the connection with Android has been dropped"""
        # self.outstanding_stm_instructions = self.manager.Value("i", 0)
        # """Number of outstanding instructions for STM32"""
        self.unpause = self.manager.Event()
        """Event to indicate that the robot has been unpaused"""
        self.finish_all = self.manager.Event()
        """Event to indicate that all processes should finish"""

        self.movement_lock = self.manager.Lock()
        """locks the movement"""
        self.android_queue: Queue[AndroidMessage] = self.manager.Queue()
        """Messages to send to Android"""
        self.rpi_action_queue: Queue[PiAction] = self.manager.Queue()
        """Messages that need to be processed by RPi"""
        self.command_queue = self.manager.Queue()
        """Commands that need to be exec by STM32 & snap from ALGO"""
        self.path_queue = self.manager.Queue()
        """X,Y,D coordinates of the robot passed from the command_queue"""

        self.proc_recv_android: Process
        """receive android"""
        self.proc_recv_stm32: Process
        """recieve stm"""
        self.proc_android_controller: Process
        """subprocess to control messages for tx/rx with android"""
        self.proc_command_follower: Process
        """commands given by the algo"""
        self.proc_rpi_action: Process
        """proc action"""

        # self.obstacles = self.manager.Value("i", 0)
        # """Number of obstacles left to detect by the robot"""

        self.current_location = self.manager.dict()

        self.failed_attempt = False

    @abstractmethod
    def start(self) -> None:
        pass

    def stop(self) -> None:
        """Stops all processes on the RPi and disconnects with Android and STM32"""
        self.android_link.disconnect()
        self.stm_link.disconnect()
        self.clear_queues()
        self.clear_proccess()
        logger.info("Program exited!")

    def clear_proccess(self) -> None:
        # get all self attributes that start with 'proc_'
        processes = [getattr(self, attr) for attr in dir(self) if attr.startswith("proc_")]
        for process in processes:
            try:
                process.kill()
            except Exception as e:
                logger.error(f"Error killing process: {e}")
    
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
