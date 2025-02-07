import os
from communication.android import AndroidLink, AndroidMessage
import bluetooth

# android_link = AndroidLink()
# android_link.connect()
# android_link.send(AndroidMessage("info", "You are reconnected!"))
# android_link.disconnect()

# Set RPi to be discoverable in order for service to be advertisable
os.system("sudo hciconfig hci0 piscan")

# Initialize server socket
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

# Parameters
port = server_sock.getsockname()[1]
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# Advertise
bluetooth.advertise_service(
    server_sock,
    "MDP-Group21-RPi",
    service_id=uuid,
    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE],
)

client_sock, client_info = server_sock.accept()

