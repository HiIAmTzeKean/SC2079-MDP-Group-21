import logging
from abc import ABC, abstractmethod
from typing import Optional, Union


logger = logging.getLogger(__name__)


class Link(ABC):
    """
    Abstract class to handle communications between Raspberry Pi and other components
    - send(message: str)
    - recv()
    """

    def __init__(self) -> None:
        """
        Constructor for Link.
        """
        self.logger = logger

    @abstractmethod
    def send(self, message: str) -> None:
        pass

    @abstractmethod
    def recv(self) -> Optional[str]:
        pass
