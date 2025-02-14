from communication.stm32 import STMLink
from constant.command_utils import (
    send_command_sequence,
    cmd_front,
    cmd_left,
    cmd_right,
    cmd_back,
    cmd_bright,
    cmd_bleft,
    cmd_left_arc,
    cmd_right_arc
)

stm_link = STMLink()
stm_link.connect()
stm_link.send_cmd("t",50,0,10)
stm_link.recv()
stm_link.send_cmd("T",50,0,10)
stm_link.recv()

cmd_front(stm_link)
cmd_left(stm_link)
cmd_right(stm_link)
cmd_back(stm_link)
cmd_bright(stm_link)
cmd_bleft(stm_link)
cmd_left_arc(stm_link)
cmd_right_arc(stm_link)

#for manual input can have multiple commands
#exec_seq(stm_link, ["front"])

#Step 1 move near object #cmd_front(stm_link)
#Step 2 Turn left or right (need recognize the direction arrow)
#Turning Left
#cmd_left_arc(stm_Link)
#exec_seqCstm_Link, ["Left60"])
#Turning right
#cd_right arc(stm_link)
#exec_seq(stm_link, ["right60"])
#Step 3 Move until near object (detect direction arrow)

#Step 4 Turn left or right
#Left Arrow
#cmd_left(sta_link)
#Right Arrow
#cmd_right(stn_ link)
#Step 5
#after turning, have to use IR sensor to detect whether obstacle is cleared 

#Step 6
#Left Arrow, need go right
#exec_seq(stn_Link, ["right", "right"])
#Right Arrow, need go left
#exec_seq(stn_Link, ["left", "Left"])

#Step 7 clear the obstacle length, use IR sensor to determine? Need to discuss 

#Step 8
#Left arrow #cnd_right
#Right arrow #cmd_left
test_stm.py
#Step 9 I think need to know how far we traversed, not sure how this can be implemented but need to path find back..
#Step 10 Park
assert True