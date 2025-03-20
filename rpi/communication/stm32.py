import logging
from typing import Optional

import serial
from .link import Link
from rpi.constant.consts import stm32_prefixes
from rpi.constant.settings import BAUD_RATE, SERIAL_PORT


logger = logging.getLogger(__name__)


class STMLink(Link):
    """Class for communicating with STM32 microcontroller over UART serial connection.

    ### RPi to STM32
    RPi sends the following commands to the STM32.

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

    # TODO deprecate this method since send cmd is the one used
    def send(self, message: str) -> None:
        """Send a message to STM32, utf-8 encoded

        :param message: message to send
        :type message: str
        """
        self.serial_link.write(f"{message}\n".encode("utf-8"))
        logger.debug(f"send stm: {message}")

    def recv(self) -> Optional[str]:
        """Receive a message from STM32, utf-8 decoded

        :return: message received from STM32
        :rtype: Optional[str]
        """
        message = self.serial_link.readline().strip().decode("utf-8")
        logger.debug(f"recv stm: {message}")
        return message

    def wait_receive(self) -> str:
        while self.serial_link.in_waiting <= 0:
            pass
        try:
            message = str(self.serial_link.read_all(), "utf-8")
            logger.debug(f"wait recv stm: {message}")
        except UnicodeDecodeError:
            return ""
        return message
    
    def send_cmd_raw(self, cmd: str) -> None:
        parts = cmd.split("|")
        self.send_cmd(parts[0][0], int(parts[0][1:]), float(parts[1]), float(parts[2]))

    def send_cmd(
        self,
        flag: str,
        speed: int,
        angle: float,
        val: float,
    ) -> None:
        cmd = flag
        if flag in stm32_prefixes:
            cmd += f"{speed}|{round(angle, 2)}|{round(val, 2)}" + "\n"
        self.serial_link.write(f"{cmd}\n".encode("utf-8"))
        logger.debug(f"send_cmd stm: {cmd}")
