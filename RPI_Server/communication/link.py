import logging
from abc import ABC, abstractmethod
from typing import Optional, Union

from android import AndroidMessage


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
    def send(self, message: Union[str, AndroidMessage]) -> None:
        pass

    @abstractmethod
    def recv(self) -> Optional[str]:
        pass
