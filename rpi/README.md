# RPi Codebase

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
fully finishing a right turn.

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

