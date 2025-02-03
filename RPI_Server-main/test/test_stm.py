from communication.stm32 import STMLink

stm_link = STMLink()
stm_link.connect()
stm_link.send_cmd("t",50,0,10)
stm_link.recv()
stm_link.send_cmd("T",50,0,10)
stm_link.recv()

assert True