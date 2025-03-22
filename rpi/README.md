# RPi Codebase

## Usage

Install python 3.9 in your RPi and the required libraries preferably using `apt-get`
package so that it is consistent with our environment. You can opt for a newer
version of python but this would be at your own risk.

Modules to take note of

- `communication` stores all the needed objects that are used in the base and task classes
- `constant` stores constants such as the forward speed or settings that we want to be relatively static
- `test` stores our test cases that we use to test the module or for developemental purposes
- `checklist` is the code that we use for our checklist

All other files in the root of `/rpi` contains the core classes that you need to
run the bot.

To get the robot moving simply run the following code below

```bash
# ensure that your are in /SC2079-MDP-GROUP
python3.9 run_t1.py
```

## Known issues

The bluetooth module may not terminate properly at times, simply run the following
code to kill the bluetooth script so that the RPi connects on channel 1.

```bash
# ensure that you are in `/rpi`
sudo bash restart_bt.sh
```

## Base RPi class

### Overview

The `base_rpi.py` file defines the `RaspberryPi` abstract base class, which serves as a foundation for managing communication and coordination between the Raspberry Pi, an Android device, and an STM32 microcontroller. This class provides essential methods and attributes for handling processes, queues, and events required for the robot's operation.

### Class and Methods

#### `RaspberryPi`

##### `__init__(self) -> None`

Initializes the Raspberry Pi with various communication links, managers, events, queues, and processes.

- **Attributes**:
  - `android_link`: Manages the connection with the Android device.
  - `stm_link`: Manages the connection with the STM32 microcontroller.
  - `manager`: Multiprocessing manager for handling shared resources.
  - `android_dropped`: Event to indicate that the connection with Android has been dropped.
  - `unpause`: Event to indicate that the robot has been unpaused.
  - `finish_all`: Event to indicate that all processes should finish.
  - `movement_lock`: Lock to control movement.
  - `android_queue`: Queue for messages to send to Android.
  - `rpi_action_queue`: Queue for messages that need to be processed by the Raspberry Pi.
  - `command_queue`: Queue for commands to be executed by the STM32 and snap from ALGO.
  - `path_queue`: Queue for X, Y, D coordinates of the robot passed from the command queue.
  - `proc_recv_android`: Process for receiving messages from Android.
  - `proc_recv_stm32`: Process for receiving messages from STM32.
  - `proc_android_controller`: Process for controlling messages for transmission/reception with Android.
  - `proc_command_follower`: Process for following commands given by the algorithm.
  - `proc_rpi_action`: Process for handling Raspberry Pi actions.
  - `second_obstacle_dist`: Shared value for the distance to the second obstacle.
  - `outstanding_stm_instructions`: Shared value for the number of outstanding instructions for STM32.
  - `obstacles`: Shared value for the number of obstacles left to detect by the robot.
  - `current_location`: Shared dictionary for the robot's current location.
  - `completed`: Boolean indicating if the task is completed.
  - `failed_attempt`: Boolean indicating if there was a failed attempt.

##### `start(self) -> None`

Abstract method to start the orchestrator. Must be implemented by subclasses.

##### `stop(self) -> None`

Stops all processes on the Raspberry Pi and disconnects from Android and STM32.

- **Functionality**:
  - Disconnects from Android and STM32.
  - Clears command and path queues.
  - Kills all processes.

##### `clear_proccess(self) -> None`

Clears all processes that start with 'proc_'.

- **Functionality**:
  - Retrieves all attributes that start with 'proc_'.
  - Attempts to kill each process and logs any errors encountered.

##### `clear_queues(self) -> None`

Clears both command and path queues.

- **Functionality**:
  - Empties the command queue.
  - Empties the path queue.

##### `check_api(self) -> bool`

Checks whether the image recognition API server is up and running.

- **Returns**:
  - `True` if the API is running.
  - `False` if the API is not running or if there is an error.

- **Functionality**:
  - Sends a GET request to the API status endpoint.
  - Logs and handles connection errors, timeouts, and other exceptions.

## Task 1

The `TaskOne` class is a Raspberry Pi orchestrator responsible for managing communication and coordination between an Android device, an STM32 microcontroller, and various Raspberry Pi processes. This orchestrator handles tasks such as receiving commands, processing actions, capturing images, and interacting with APIs.

### Features

- **Android Communication**: Manages the connection and communication with an Android device, including sending and receiving messages.
- **STM32 Communication**: Receives acknowledgment messages from the STM32 microcontroller and updates the robot's current location.
- **Image Recognition**: Captures images using the Raspberry Pi camera and sends them to an image recognition API.
- **Algorithm Requests**: Requests a series of commands and paths from an algorithm API and queues them for execution.
- **Stitching Images**: Sends a request to an image recognition API to stitch multiple images together.

### Processes Summary

The `TaskOne` class runs several child processes to manage different aspects of the robot's operation. Below is a summary of each process:

#### `recv_android`

- **Description**: Processes messages received from the Android device.
- **Functionality**:
  - Receives messages from the Android link.
  - Processes commands such as setting obstacles and starting the robot's movement.
  - Handles connection drops and logs errors.

#### `recv_stm`

- **Description**: Receives acknowledgment messages from the STM32 microcontroller and releases the movement lock.
- **Functionality**:
  - Waits for messages from the STM32 link.
  - Updates the robot's current location based on the received messages.
  - Releases the movement lock when a "finish" message is received.
  - Logs errors and warnings for unknown messages.

#### `android_controller`

- **Description**: Retrieves messages from the Android queue and sends them over the Android link.
- **Functionality**:
  - Continuously checks for messages in the Android queue.
  - Sends messages to the Android link.
  - Handles queue empty exceptions and connection drops.
  - Logs errors for any issues encountered.

#### `rpi_action`

- **Description**: Processes the actions that the Raspberry Pi needs to take.
- **Functionality**:
  - Retrieves actions from the RPi action queue.
  - Processes obstacle setting, image recognition, and image stitching actions.
  - Requests commands and paths from the algorithm API based on the actions.

#### `command_follower`

- **Description**: Follows commands received from the command queue and sends them to the STM32 microcontroller or processes them as image capture commands.
- **Functionality**:
  - Retrieves commands from the command queue.
  - Waits for the unpause event before executing commands.
  - Acquires the movement lock before sending commands to the STM32 or capturing images.
  - Handles "finish" commands by releasing the movement lock and stopping the processes.
  - Logs errors for unknown commands.

#### `reconnect_android`

- **Description**: Handles the reconnection to the Android device in the event of a lost connection.
- **Functionality**:
  - Waits for the Android connection to drop.
  - Kills and restarts the Android-related child processes.
  - Cleans up old sockets and reconnects the Android link.
  - Logs the reconnection process and sends reconnection messages to the Android device.

## Task 2

### Main file

`ANDRIOD_CONTROLLER = False` Controls the logic if android is to be used to start the
programme. Set to true if you need android.

For defining the commands, you do not need to touch anything else other than to
modify the 4 lists provided that determines the action to be taken. Below is an
example. Note that you can specify presets defined in consts.py or to define
an actual command as shown below.

Note: There is a command that you can issue `stall` which ensures all preceding
instructions are done before the next is executed. This is particularly useful
when there is a turn command (u-turn) and the STM at times move straight before
fully finishing a right turn. You can change the stall time

```python
action_list_second_left = [
    "frontuntil",
    "left",  # robot 15cm apart from wall, 20cm turn radius
    "R_ir",
    "u_turn_right",
    "stall",
    "r_ir",  # 15cm apart from wall on opposite side
    "R_ir",
    "right",
    f"T{FORWARD_SPEED_INDOOR}|0|20",
    f"r{FORWARD_SPEED_INDOOR}|0|50",
    "T30|0|20",
    "right",
    "r_ir",
    "left",
    f"W{FORWARD_SPEED_INDOOR}|0|15",
]
```

### Constants and Commands

Refer to `/constant/consts.py`.

- FORWARD_SPEED_INDOOR: Speed for forward movement indoors.
- TRACKING_SPEED_INDOOR: Speed for tracking movement indoors. Such as IR and Sonar.

To add more commands you can add directly to the dictionary or to define it
in such a way.

```python
manual_commands["u_turn_left"] = (manual_commands["left"], manual_commands["left"])
```
