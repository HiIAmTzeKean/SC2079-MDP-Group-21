from rpi.communication.stm32 import STMLink


stm_link = STMLink()
stm_link.connect()


# # right turn 
# stm_link.send_cmd("T",50,50,44) 
# stm_link.send_cmd("t",50,0,15) 
# stm_link.send_cmd("T",50,50,44)
# stm_link.send_cmd("t",25,0,4)

# half turn left
#stm_link.send_cmd("T",20,-95,45) 
#stm_link.send_cmd("T",20,95,44.5) 
#stm_link.send_cmd("T",100,0,2)

# half turn right
#stm_link.send_cmd("T",20,97,44.5)
#stm_link.send_cmd("T",20,-97,46)
#stm_link.send_cmd("T",25,35,0.1)
#stm_link.send_cmd("T",100,0,2)


# reverse half turn left
#stm_link.send_cmd("t",20,-100,45)
#stm_link.send_cmd("t",20,100,44.5)
#stm_link.send_cmd("t",100,0,2)

# reverse half turn right
#stm_link.send_cmd("t",20,97,45)
#stm_link.send_cmd("t",20,-97,46)
#stm_link.send_cmd("T",25,35,0.1)
#stm_link.send_cmd("T",100,0,2)

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



#stm_link.send_cmd("T",25,20,0.1)

#joel left
#stm_link.send_cmd("T",30,-60.5,91.5)
#stm_link.send_cmd("T",25,35,0.1)
#stm_link.send_cmd("t",100,0,5.5)

#right
#stm_link.send_cmd("T",30,58,91.5)
#stm_link.send_cmd("t",100,0,5)

#reverse left
#stm_link.send_cmd("T",100,0,4)
#stm_link.send_cmd("t",30,-58,91.5)
#stm_link.send_cmd("T",25,10,0.1)

#reverse right
stm_link.send_cmd("T",100,0,6.5)
stm_link.send_cmd("t",30,45,91.5)
