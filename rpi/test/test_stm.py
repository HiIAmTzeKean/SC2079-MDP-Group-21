from rpi.communication.stm32 import STMLink


stm_link = STMLink()
stm_link.connect()


# # right turn 
# stm_link.send_cmd("T",50,50,44) 
# stm_link.send_cmd("t",50,0,15) 
# stm_link.send_cmd("T",50,50,44)
# stm_link.send_cmd("t",25,0,4)

# # reverse right 
stm_link.send_cmd("T",50,0,5)
stm_link.send_cmd("t",50,48,44) 
stm_link.send_cmd("T",50,0,13) 
stm_link.send_cmd("t",50,48,44)

# left  
# stm_link.send_cmd("T",50,-50,44) 
# stm_link.send_cmd("t",50,0,19) 
# stm_link.send_cmd("T",50,-50,44)
# stm_link.send_cmd("T",25,10,0.1)
# stm_link.send_cmd("t",50,0,3)


# # reverse left 
# stm_link.send_cmd("T",25,0,5) 
# stm_link.send_cmd("t",30,-50,46) 
# stm_link.send_cmd("T",25,0,14) 
# stm_link.send_cmd("t",30,-50,46)
# stm_link.send_cmd("T",25,10,0.1)
