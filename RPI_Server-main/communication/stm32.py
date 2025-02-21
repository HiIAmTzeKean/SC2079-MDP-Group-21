from enum import Enum
import logging
from typing import Optional

import serial
from communication.link import Link
from constant.settings import BAUD_RATE, SERIAL_PORT


logger = logging.getLogger(__name__)

class PathMode(Enum):
    """Enum class for Path mode commands"""
    FW = "FW0x"
    BW = "BW0x"
    FL = "FL00"
    FR = "FR00"
    BL = "BL00"
    BR = "BR00"

class ManualMode(Enum):
    """Enum class for Manual mode commands"""
    FW_I = "FW--" # Move forward indefinitely
    BW_I = "BW--" # Move backward indefinitely
    TL_I = "TL--" # Steer left indefinitely
    TR_I = "TR--" # Steer right indefinitely
    STOP = "STOP" # Stop all servos


class STMLink(Link):
    """Class for communicating with STM32 microcontroller over UART serial connection.

    ### RPi to STM32
    RPi sends the following commands to the STM32.

    #### Path mode commands
    High speed forward/backward, with turning radius of `3x1`
    - `FW0x`: Move forward `x` units
    - `BW0x`: Move backward `x` units
    - `FL00`: Move to the forward-left location
    - `FR00`: Move to the forward-right location
    - `BL00`: Move to the backward-left location
    - `BR00`: Move to the backward-right location

    #### Manual mode commands
    - `FW--`: Move forward indefinitely
    - `BW--`: Move backward indefinitely
    - `TL--`: Steer left indefinitely
    - `TR--`: Steer right indefinitely
    - `STOP`: Stop all servos

    ### STM32 to RPi
    After every command received on the STM32, an acknowledgement (string: `ACK`) must be sent back to the RPi.
    This signals to the RPi that the STM32 has completed the command, and is ready for the next command.
    """

    def __init__(self) -> None:
        """
        Constructor for STMLink.
        """
        super().__init__()
        self.serial_link: serial.Serial

        # try to connect to STM32
        try:
            self.connect()
        except Exception as e:
            logger.error(f"Failed to connect to STM32: {e}")
            raise e

    def connect(self) -> None:
        """Connect to STM32 using serial UART connection, given the serial port and the baud rate"""
        self.serial_link = serial.Serial(SERIAL_PORT, BAUD_RATE)
        logger.info("Connected to STM32")

    def disconnect(self) -> None:
        """Disconnect from STM32 by closing the serial link that was opened during connect()"""
        self.serial_link.close()
        del self.serial_link
        logger.info("Disconnected from STM32")

    def send(self, message: str) -> None:
        """Send a message to STM32, utf-8 encoded

        :param message: message to send
        :type message: str
        """
        self.serial_link.write(f"{message}\n".encode("utf-8"))
        logger.debug(f"Sent to STM32: {message}")

    def recv(self) -> Optional[str]:
        """Receive a message from STM32, utf-8 decoded

        :return: message received from STM32
        :rtype: Optional[str]
        """
        message = self.serial_link.readline().strip().decode("utf-8")
        logger.debug(f"Receive from STM: {message}")
        return message

    def wait_receive(self) -> Optional[str]:
        while self.serial_link.in_waiting < 0:
            pass
        message = str(self.serial_link.read_all(), "utf-8")
        logger.debug(f"Message Received All: {message}")
        return message

    def send_cmd(
        self,
        flag: str,
        speed: int,
        angle: int,
        val: int,
    ) -> None:
        cmd = flag
        if flag not in ["S", "D", "M"]:
            cmd += f"{speed}|{round(angle, 2)}|{round(val, 2)}" + "\n"
        self.send(cmd)
