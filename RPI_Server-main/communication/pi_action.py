from typing import Any

from ..constant.consts import Category


class PiAction:
    """
    Class that represents an action that the RPi needs to take.
    """

    def __init__(self, cat: Category, value: str | list) -> None:
        """
        :param cat: The category of the action. Can be 'info', 'mode', 'path', 'snap', 'obstacle', 'location', 'failed', 'success'
        :param value: The value of the action. Can be a string, a list of coordinates, or a list of obstacles.
        """
        self._cat = cat
        self._value = value

    @property
    def cat(self) -> str:
        return self._cat.value

    @property
    def value(self) -> str | list[Any]:
        return self._value
