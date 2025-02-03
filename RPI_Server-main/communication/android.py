import json
import logging
import os
import socket
from typing import Optional

import bluetooth
from communication.link import Link


logger = logging.getLogger(__name__)

class AndroidMessage:
    """
    Android message sent over Bluetooth connection.
    """

    def __init__(self, cat: str, value: str | dict[str,int]) -> None:
        self._cat = cat
        self._value = value

    @property
    def category(self) -> str:
        """
        Returns the message category.
        :return: String representation of the message category.
        """
        return self._cat

    @property
    def value(self) -> str:
        """
        Returns the message as a string.
        :return: String representation of the message.
        """
        if isinstance(self._value, dict):
            raise ValueError("Value is a dictionary, use jsonify instead.")
        return self._value

    @property
    def jsonify(self) -> str:
        """
        Returns the message as a JSON string.
        :return: JSON string representation of the message.
        """
        return json.dumps({"cat": self._cat, "value": self._value})


class AndroidDummy(Link):
    """
    Just to mimic android but I used PC to test it out
    """

    def __init__(self, host="0.0.0.0", port=1337):
        """
        Contructor for AndroidDummy.
        """
        super().__init__()
        self.host = host
        self.port = port
        self.server_sock = None
        self.client_sock = None

    def connect(self):
        """
        Connect to Android Dummy
        """
        # print("Connected to Android dummy.")
        logger.info("TCP Connection Attempt Start")
        try:
            # TCP Server Socket
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.bind((self.host, self.port))
            self.server_sock.listen(1)

            logger.info(f"Awaiting TCP connection on {self.host}:{self.port}")
            self.client_sock, client_info = self.server_sock.accept()
            logger.info(f"Connected to Android Dummy from: {client_info}")
        except Exception as e:
            logger.error(f"Error in TCP link connectio: {e}")
            if self.server_sock:
                self.server_sock.close()
            if self.client_sock:
                self.client_sock.close()

    def disconnect(self):
        """
        Disconnect from PC TCP Connection and Shutdown all socket
        """
        try:
            logger.debug("Disconnecting TCP Link")
            if self.server_sock:
                self.server_sock.shutdown(socket.SHUT_RDWR)
                self.server_sock.close()
            if self.client_sock:
                self.client_sock.shutdown(socket.SHUT_RDWR)
                self.client_sock.close()
            self.client_sock = None
            logger.info("Disconnected from Android Dummy")
        except Exception as e:
            logger.error(f"Failed to disconnect TCP link: {e}")

    def send(self, message: AndroidMessage):
        """Send message to PC"""
        try:
            self.client_sock.sendall(f"{message.jsonify()}".encode("utf-8"))
            logger.debug(f"Sent to PC: {message.jsonify()}")
        except OSError as e:
            logger.error(f"Error sending message to PC: {e}")
            raise e

    def recv(self):
        """Receive message from PC"""
        try:
            tmp = self.client_sock.recv(1024)
            logger.debug(tmp)
            message = tmp.strip().decode("utf-8")
            logger.debug(f"Received from PC: {message}")
            return message
        except OSError as e:
            logger.error(f"Error receiving message from PC: {e}")
            raise e


class AndroidLink(Link):
    """Class for communicating with Android tablet over Bluetooth connection.

    ## General Format
    Messages between the Android app and RPi will be in the following format:
    ```json
    {"cat": "xxx", "value": "xxx"}
    ```

    The `cat` (for category) field with the following possible values:
    - `info`: general messages
    - `error`: error messages, usually in response of an invalid action
    - `location`: the current location of the robot (in Path mode)
    - `image-rec`: image recognition results
    - `mode`: the current mode of the robot (`manual` or `path`)
    - `status`: status updates of the robot (`running` or `finished`)
    - `obstacle`: list of obstacles

    ## Android to RPi

    #### Set Obstacles
    The contents of `obstacles` together with the configured turning radius
    (`settings.py`) will be passed to the Algorithm API.
    
    ```json
    {
        "cat": "obstacles",
        "value": {
            "obstacles": [{"x": 5, "y": 10, "id": 1, "d": 2}],
            "mode": "0"
        }
    }
    ```
    RPi will store the received commands and path and make a call to the Algorithm API
    
    ### RPi to STM
    
    ####  Start
    Signals to the robot to start dispatching the commands (when obstacles are set).
    ```json
    {"cat": "control", "value": "start"}
    ```

    If there are no commands in the queue, the RPi will respond with an error:
    ```json
    {"cat": "error", "value": "Command queue is empty, did you set obstacles?"}
    ```

    ### RPi to Android

    #### Image Recognition
    
    ```json
    {"cat": "image-rec", "value": {"image_id": "A", "obstacle_id":  "1"}}
    ```

    #### Location Updates
    
    In Path mode, the robot will periodically notify Android with the updated location of the robot.
    ```json
    {"cat": "location", "value": {"x": 1, "y": 1, "d": 0}}
    ```
    where `x`, `y` is the location of the robot, and `d` is its direction.
    the direction for `d` being defined as
    ```
        NORTH = 0
        EAST = 2
        SOUTH = 4
        WEST = 6
        SKIP = 8
    ```
    """

    def __init__(self) -> None:
        """
        Initialize the Bluetooth connection.
        """
        super().__init__()
        self.client_sock = None
        self.server_sock = None

    def connect(self) -> None:
        """
        Connect to Andriod by Bluetooth
        """
        logger.info("Bluetooth connection started")
        try:
            # Set RPi to be discoverable in order for service to be advertisable
            os.system("sudo hciconfig hci0 piscan")

            # Initialize server socket
            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_sock.bind(("", bluetooth.PORT_ANY))
            self.server_sock.listen(1)

            # Parameters
            port = self.server_sock.getsockname()[1]
            uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

            # Advertise
            bluetooth.advertise_service(
                self.server_sock,
                "MDP-Group21-RPi",
                service_id=uuid,
                service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE],
            )

            logger.info(f"Awaiting Bluetooth connection on RFCOMM CHANNEL {port}")
            self.client_sock, client_info = self.server_sock.accept()
            logger.info(f"Accepted connection from: {client_info}")

        except Exception as e:
            logger.error(f"Error in Bluetooth link connection: {e}")
            self.server_sock.close()
            self.client_sock.close()

    def disconnect(self) -> None:
        """Disconnect from Android Bluetooth connection and shutdown all the sockets established"""
        try:
            logger.debug("Disconnecting Bluetooth link")
            self.server_sock.shutdown(socket.SHUT_RDWR)
            self.client_sock.shutdown(socket.SHUT_RDWR)
            self.client_sock.close()
            self.server_sock.close()
            self.client_sock = None
            self.server_sock = None
            logger.info("Disconnected Bluetooth link")
        except Exception as e:
            logger.error(f"Failed to disconnect Bluetooth link: {e}")

    def send(self, message: AndroidMessage) -> None:
        """Send message to Android"""
        try:
            self.client_sock.send(f"{message.jsonify}\n".encode("utf-8"))
            logger.debug(f"Sent to Android: {message.jsonify}")
        except OSError as e:
            logger.error(f"Error sending message to Android: {e}")
            raise e

    def recv(self) -> Optional[str]:
        """Receive message from Android"""
        try:
            tmp = self.client_sock.recv(1024)
            logger.debug(tmp)
            message = tmp.strip().decode("utf-8")
            logger.debug(f"Received from Android: {message}")
            return message
        except OSError as e:  # connection broken, try to reconnect
            logger.error(f"Error receiving message from Android: {e}")
            raise e
