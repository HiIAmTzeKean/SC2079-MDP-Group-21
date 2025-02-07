from typing import Optional

import serial


BAUD_RATE = 115200
SERIAL_PORT = "COM3"

serialLink = serial.Serial(SERIAL_PORT, BAUD_RATE)
print("Connected to STM32")


def send(message: str) -> None:
    """Send a message to STM32, utf-8 encoded

    Args:
        message (str): message to send
    """
    serialLink.write(bytes(message, "utf-8"))
    print("Sent to STM32:", str(message).rstrip())


def wait_receive() -> Optional[str]:
    """Receive a message from STM32, utf-8 decoded

    Returns:
        Optional[str]: message received
    """
    while True:
        if serialLink.in_waiting > 0:
            return str(serialLink.read_all(), "utf-8")


def send_cmd(flag, speed, angle, val):
    """Send command and wait for acknowledge."""
    cmd = flag
    if flag not in ["S", "D", "M"]:
        cmd += f"{speed}|{round(angle, 2)}|{round(val, 2)}"

    cmd += "\n"
    send(cmd)


# t80|0|90\n

send_cmd("t", 50, -20, 180)
wait_receive()
