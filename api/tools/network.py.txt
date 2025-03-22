import time
import subprocess
import platform

rpi_ssid = "MDPGrp21"


def get_wifi_name():
    """Get the current Wi-Fi SSID (network name)."""
    try:
        system = platform.system()
        if system == "Windows":
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"]).decode("utf-8")
            for line in output.split("\n"):
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":")[1].strip()
        elif system == "Linux":
            output = subprocess.check_output(
                ["iwgetid", "-r"]).decode("utf-8").strip()
            return output
        elif system == "Darwin":  # macOS
            output = subprocess.check_output(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"]
            ).decode("utf-8")
            for line in output.split("\n"):
                if " SSID" in line:
                    return line.split(":")[1].strip()
    except Exception as e:
        return str(e)
    return "Unknown"


def network_monitor(logger):
    """Background thread to monitor network status continuously."""
    while True:
        wifi_name = get_wifi_name()
        if wifi_name.lower() != rpi_ssid.lower():
            logger.debug(f"Not connected to RPI Wi-fi: {rpi_ssid}")

        time.sleep(5)  # Adjust the polling interval as needed
