from rpi.constant.consts import manual_commands

# prep the basic directional commamds and the arcs (likely for obstacle 2)
# values to be adjusted again..
def exec_seq(stm_link, commands: list):
    """Send commands (single or multiple) to STM32."""
    for command in commands:
        if command in manual_commands:
            flag, speed, angle, val = manual_commands[command]
            stm_link.send_cmd(flag, speed, angle, val)
            response = stm_link.recv()
            print(f"Executed {command}: {response}")
        else:
            print(f"Invalid command: {command}")

def cmd_front(stm_link):
    exec_seq(stm_link, ["front"])

def cmd_left(stm_link):
    exec_seq(stm_link, ["left"])

def cmd_right(stm_link):
    exec_seq(stm_link, ["right"])

def cmd_back(stm_link):
    exec_seq(stm_link, ["back"])

def cmd_bright(stm_link):
    exec_seq(stm_link, ["bright"])

def cmd_bleft(stm_link):
    exec_seq(stm_link, ["bleft"])

def cmd_left_arc(stm_link):
    exec_seq(stm_link, ["left", "right120", "left60"])

def cmd_right_arc(stm_link):
    exec_seq(stm_link, ["right", "left120", "right60"])