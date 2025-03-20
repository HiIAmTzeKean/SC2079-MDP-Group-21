from rpi.communication.stm32 import STMLink



stm_link = STMLink()
stm_link.connect()

#stm_link.send_cmd("W",70,0,20)
#stm_link.send_cmd("T",50,-35,45)
#stm_link.send_cmd("T",50,35,45)
#stm_link.send_cmd("T",50,35,45)
#stm_link.send_cmd("T",50,-35,45)
stm_link.send_cmd("T",25,-10,0.1)
stm_link.send_cmd("W",70,0,25)
#left arc
#stm_link.send_cmd("T",50,-45,50)
#stm_link.send_cmd("T",50,45,100)
#stm_link.send_cmd("T",50,-45,50)

stm_link.send_cmd("T",50,45,50)
stm_link.send_cmd("T",50,-45,100)
stm_link.send_cmd("T",50,45,50)

stm_link.send_cmd("W",70,0,33)
stm_link.send_cmd("w",70,0,33)

#stm_link.send_cmd("T",50,45,40)
#stm_link.send_cmd("T",100,0,20)
#stm_link.send_cmd("T",50,-45,80.5)
#stm_link.send_cmd("T",100,0,10)
#stm_link.send_cmd("T",50,45,40)

# stm_link.send_cmd("T",25,10,0.1) 
# stm_link.send_cmd("T",50,60,44.5) # r

# stm_link.send_cmd("T",50,-60,89.5)
#stm_link.send_cmd("T",25,10,0.1)
#stm_link.send_cmd("T",40,-60,90.2) 
#stm_link.send_cmd("T",40,-60,90.2) 

#stm_link.send_cmd("T",25,10,0.1)
#stm_link.send_cmd("T",40,60,90.3)
#stm_link.send_cmd("T",40,60,90.3)
#stm_link.send_cmd("T",30,0,100)
#stm_link.send_cmd("w",60,0,100)
# # right turn 
#stm_link.send_cmd("T",30,50,46) 
#stm_link.send_cmd("t",25,0,20) 
#stm_link.send_cmd("T",30,50,45.7)
#stm_link.send_cmd("t",25,0,4)

# turn left
#stm_link.send_cmd("T",30,-50,46) 
#stm_link.send_cmd("t",25,0,23) 
#stm_link.send_cmd("T",30,-50,45.5)
#stm_link.send_cmd("T",25,10,0.1)
#stm_link.send_cmd("t",25,0,3)

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


# # reverse right 
# stm_link.send_cmd("T",25,0,6) 
# stm_link.send_cmd("t",30,48,46) 
# stm_link.send_cmd("T",25,0,14) 
# stm_link.send_cmd("t",30,48,45.5)


# reverse left
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
#stm_link.send_cmd("T",100,0,6.5)
#stm_link.send_cmd("t",30,45,91.5)
