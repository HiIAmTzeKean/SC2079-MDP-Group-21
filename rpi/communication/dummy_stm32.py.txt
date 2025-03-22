import logging
from typing import Optional

import serial
from .link import Link
from rpi.constant.consts import stm32_prefixes
from rpi.constant.settings import BAUD_RATE, SERIAL_PORT


logger = logging.getLogger(__name__)


class DummySTMLink(Link):
    """Dummy class for simulating communication with STM32 microcontroller."""

    def __init__(self) -> None:
        """Constructor for STMLinkDummy."""
        logger.info("Initialized STMLinkDummy")

    def connect(self) -> None:
        """Dummy connect method."""
        logger.info("Dummy connect to STM32")

    def disconnect(self) -> None:
        """Dummy disconnect method."""
        logger.info("Dummy disconnect from STM32")

    def send(self, message: str) -> None:
        """Dummy send method.

        :param message: message to send
        :type message: str
        """
        logger.debug(f"Dummy sent to STM32: {message}")

    def recv(self) -> Optional[str]:
        """Dummy receive method.

        :return: dummy message received from STM32
        :rtype: Optional[str]
        """
        message = "dummy_message"
        logger.debug(f"Dummy receive from STM32: {message}")
        return message

    def wait_receive(self) -> Optional[str]:
        """Dummy wait_receive method.

        :return: dummy message received from STM32
        :rtype: Optional[str]
        """
        message = "dummy_message_all"
        logger.debug(f"Dummy message received all: {message}")
        return message

    def send_cmd(
        self,
        flag: str,
        speed: int,
        angle: int,
        val: int,
    ) -> None:
        """Dummy send_cmd method.

        :param flag: command flag
        :param speed: speed value
        :param angle: angle value
        :param val: additional value
        """
        cmd = f"{flag}{speed}|{round(angle, 2)}|{round(val, 2)}"
        logger.debug(f"Dummy sent to STM32: {cmd}")