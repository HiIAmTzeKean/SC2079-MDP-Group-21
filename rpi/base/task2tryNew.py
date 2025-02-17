#!/usr/bin/env python3
import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
import requests
import math
from communication.android import AndroidLink, AndroidMessage
from communication.stm32 import STMLink
from communication.camera import snap_using_libcamera
from consts import SYMBOL_MAP
from logger import prepare_logger
from settings import API_IP, API_PORT


class PiAction:
    def __init__(self, cat, value):
        self._cat = cat
        self._value = value

    @property
    def cat(self):
        return self._cat

    @property
    def value(self):
        return self._value


class RaspberryPi:
    def __init__(self):
        # Initialize logger and communication objects with Android and STM
        self.logger = prepare_logger()
        self.android_link = AndroidLink()
        self.stm_link = STMLink()

        # For sharing information between child processes
        self.manager = Manager()

        # Set robot mode to be 1 (Path mode)
        self.robot_mode = self.manager.Value('i', 1)

        # Events
        self.android_dropped = self.manager.Event()  # Set when the android link drops
        # commands will be retrieved from commands queue when this event is set
        self.unpause = self.manager.Event()

        # Movement Lock
        self.movement_lock = self.manager.Lock()

        # Queues
        self.android_queue = self.manager.Queue() # Messages to send to Android
        self.rpi_action_queue = self.manager.Queue() # Messages that need to be processed by RPi
        self.command_queue = self.manager.Queue() # Messages that need to be processed by STM32, as well as snap commands

        # Define empty processes
        self.proc_recv_android = None
        self.proc_recv_stm32 = None
        self.proc_android_sender = None
        self.proc_command_follower = None
        self.proc_rpi_action = None

        self.ack_count = 0
        #self.near_flag = self.manager.Lock()

        self.last_image = None
        self.prev_image = None

        self.num_M = 0
        self.num_obstacle = 1
        self.lock = self.manager.Lock()

        self.is_right1 = False
        self.is_right2 = False
        self.done_obstacle2 = False

        self.on_arrow_callback = None

        self.capture_dist1 = 30
        self.capture_dist2 = 20

        self.obstacle_dist1 = None
        self.obstacle_dist2 = None
        self.wall_dist = None
        self.wall_complete = False
        self.obstacle2_length_half = None

        #For Tuning with new car
        self.turning_r = 40 # Set for Turning Radius
        self.r0 = 21 # absolute distance from center line after passing obstacle 1
        self.chassis_cm = 15 # Length from Axle to Axle
        self.wheelbase_cm = 16.5 # length between front wheels 

        # Tune to Balance Speed with Precision
        self.theta2 = 10
        self.drive_speed = 50
        self.obstacle_speed = 50
        self.wall_track_speed = 40
        self.carpark_speed = 50

        self.LEFT_ARROW_ID = "39" # Return from Response 39
        self.RIGHT_ARROW_ID = "38" # Return from Response 38

    def start(self):
        """Starts the RPi orchestrator"""
        try:
            # Establish Bluetooth connection with Android
            self.android_link.connect()
            self.android_queue.put(AndroidMessage('info', 'You are connected to the RPi!'))

            # Establish connection with STM32
            self.stm_link.connect()

            # Check Image Recognition and Algorithm API status
            self.check_api()
            
            #self.small_direction = self.snap_and_rec("Small")
            #self.logger.info(f"PREINFER small direction is: {self.small_direction}")

            # Define child processes
            self.proc_recv_android = Process(target=self.recv_android)
            #self.proc_recv_stm32 = Process(target=self.recv_stm)
            self.proc_recv_stm32 = Process(target=self.tryrecv_stm)
            self.proc_android_sender = Process(target=self.android_sender)
            #self.proc_command_follower = Process(target=self.command_follower)
            self.proc_rpi_action = Process(target=self.rpi_action)

            # Start child processes
            self.proc_recv_android.start()
            self.proc_recv_stm32.start()
            self.proc_android_sender.start()
            #self.proc_command_follower.start()
            self.proc_rpi_action.start()

            self.logger.info("Child Processes started")

            ### Start up complete ###

            # Send success message to Android
            self.android_queue.put(AndroidMessage('info', 'Robot is ready!'))
            self.android_queue.put(AndroidMessage('mode', 'path' if self.robot_mode.value == 1 else 'manual'))
              
            
            # Handover control to the Reconnect Handler to watch over Android connection
            self.reconnect_android()

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stops all processes on the RPi and disconnects gracefully with Android and STM32"""
        self.android_link.disconnect()
        self.stm_link.disconnect()
        self.logger.info("Program exited!")

    def reconnect_android(self):
        """Handles the reconnection to Android in the event of a lost connection."""
        self.logger.info("Reconnection handler is watching...")

        while True:
            # Wait for android connection to drop
            self.android_dropped.wait()

            self.logger.error("Android link is down!")

            # Kill child processes
            self.logger.debug("Killing android child processes")
            self.proc_android_sender.kill()
            self.proc_recv_android.kill()

            # Wait for the child processes to finish
            self.proc_android_sender.join()
            self.proc_recv_android.join()
            assert self.proc_android_sender.is_alive() is False
            assert self.proc_recv_android.is_alive() is False
            self.logger.debug("Android child processes killed")

            # Clean up old sockets
            self.android_link.disconnect()

            # Reconnect
            self.android_link.connect()

            # Recreate Android processes
            self.proc_recv_android = Process(target=self.recv_android)
            self.proc_android_sender = Process(target=self.android_sender)

            # Start previously killed processes
            self.proc_recv_android.start()
            self.proc_android_sender.start()

            self.logger.info("Android child processes restarted")
            self.android_queue.put(AndroidMessage("info", "You are reconnected!"))
            self.android_queue.put(AndroidMessage('mode', 'path' if self.robot_mode.value == 1 else 'manual'))

            self.android_dropped.clear()
            
    def send_D(self):
        self.stm_link.send_cmd("D", 0, 0, 0)
        #self.command_queue.put("D|0|0|0")
    def send_M(self):
        #self.command_queue.put("M|0|0|0")
        self.stm_link.send_cmd("M", 0, 0, 0)
    def send_S(self):
        #self.command_queue.put("S|0|0|0")
        self.stm_link.send_cmd("S", 0, 0, 0)
    

    def recv_android(self) -> None:
        """
        [Child Process] Processes the messages received from Android
        """
       
        while True:
            msg_str: Optional[str] = None
            try:
                msg_str = self.android_link.recv()
            except OSError:
                self.android_dropped.set()
                self.logger.debug("Event set: Android connection dropped")

            # If an error occurred in recv()
            if msg_str is None:
                continue

            message: dict = json.loads(msg_str)

            ## Command: Start Moving ##
            if message['cat'] == "control":
                if message['value'] == "start":
        
                    if not self.check_api():
                        self.logger.error("API is down! Start command aborted.")

                    self.clear_queues()
                    #self.command_queue.put("D0|0|0")
                    #self.command_queue.put("W50|0|30") # ack_count = 1 //Move to Target
                    #self.command_queue.put("M0|0|0")
                    self.logger.info("Start command received, starting robot on Week 9 task!")
                    self.android_queue.put(AndroidMessage('status', 'running'))
                    
                    self.unpause.set()
                    self.STMstart()

    def tryrecv_stm(self) -> None:
        """
        [Child Process] Just to try thier method out
        """
        while True:
            try:
                #message : str = self.stm_link.recv()
                messages = self.stm_link.wait_receive()
                self.logger.debug(f"All Messages: {messages}")
                
                for message in messages.split('\n'):
                    if len(message) == 0:
                        continue
                    self.logger.debug(f"Message received from STM: {message}")
                    if "M" in message:

                        if self.num_M == 0:
                            self.logger.debug("First M Send!")
                        elif self.num_M == 1:
                            self.perform_carpark()
                        elif self.num_M == 2:
                            self.android_queue.put(AndroidMessage("status", "finished"))
                            self.command_queue.put("FIN")

                        self.num_M +=1

                    elif "D" in message:
                        dist_val_str = message.replace("fD", "").replace("\0", '').strip()
                        if len(dist_val_str) == 0:
                            # Robot is beginning drive towards obstacle, take in latest_image then decide
                            if self.num_obstacle == 1:
                                self.small_direction = self.recognise_image("ObstacleFirst_1")
                                #self.movement_lock.acquire()
                                direction = self.small_direction["image_id"]
                                #self.movement_lock.release()
                                self.logger.debug(f"Obstacle 1: {direction}")
                                if direction == self.RIGHT_ARROW_ID:
                                    self.logger.debug("First Obstacle: Right Arrow Detected")
                                    self.callback_obstacle1(True)
                                elif direction == self.LEFT_ARROW_ID:
                                    self.logger.debug("Second Obstacle: Left Arrow Detected")
                                    self.callback_obstacle1(False)
                                else:
                                    self.callback_obstacle1(True)

                            elif self.num_obstacle == 2: ## Second Obstacle
                                self.large_direction = self.recognise_image("ObstacleSecond_1")
                                #self.movement_lock.acquire()
                                direction = self.large_direction["image_id"]
                                #self.movement_lock.release()
                                self.logger.debug(f"Obstacle 2: {direction}")
                                
                                if direction == self.RIGHT_ARROW_ID:
                                    self.logger.debug("Second Obstacle: Right Arrow Detected")
                                    self.callback_obstacle2(True)
                                elif direction == self.LEFT_ARROW_ID:
                                    self.logger.debug("Second Obstacle: Left Arrow Detected")
                                    self.callback_obstacle2(False)
                                else:
                                    #self.on_arrow_callback = self.callback_obstacle2
                                    self.callback_obstacle2(True)
                            
                            self.num_obstacle += 1
                        else:
                            self.logger.debug(f"Content in dist_val_str: {dist_val_str}")
                            dist_val = float(dist_val_str)

                            with self.lock:
                                if self.obstacle_dist1 is None:
                                    self.obstacle_dist1 = dist_val
                                    self.logger.debug(f"Obstacle 1 Distance: {self.obstacle_dist1}")
                                elif self.obstacle_dist2 is None:
                                    self.obstacle_dist2 = dist_val
                                    self.logger.debug(f"Obstacle 2 Distance: {self.obstacle_dist2}")
                                elif self.wall_dist is None:
                                    self.wall_dist = dist_val + 22.5
                                    self.logger.debug(f"Wall Distance: {self.wall_dist}")
                                    self.wall_complete = True
                                    self.logger.debug(f"Wall Complete: {self.wall_complete}")
            except OSError as e:
                self.logger.debug(f"Error in receiving STM Data: {e}")
                    
                

    def drive_until(self, angle, val, is_forward=True, speed=None):
        if speed is None:
            speed = self.drive_speed
        
        self.stm_link.send_cmd("W" if is_forward else "w", speed, angle, val)

    def callback_obstacle1(self, is_right) -> None:
        with self.lock:
            self.is_right1 = is_right
        
        self.perform_arc1(is_right)
        self.perform_toward_obstacle()

        self.on_arrow_callback = None

    def callback_obstacle2(self, is_right) -> None:
        with self.lock:
            self.done_obstacle2 = True
            self.is_right2 = is_right
        
        self.perform_arc2(self.is_right1, is_right)
        self.on_arrow_callback = None
        #self.send_D()
        self.send_M()
        
        

    def perform_toward_obstacle(self, capture_dist=30) -> None:
        self.send_D()
        self.drive_until(0, capture_dist, speed=self.obstacle_speed)
        self.send_D()

    
    def perform_arc1(self, is_right) -> None:
        angle = 25 if is_right else - 25

        turn_theta = 33
        self.drive(angle, turn_theta)
        self.drive(0, 18)
        self.drive(-angle, turn_theta + self.theta2)
        self.send_M()

    def perform_arc2(self, is_right1, is_right2) -> None:
        is_cross = is_right1 != is_right2
        angle = 25 if is_right2 else -25

        if is_cross:
            gamma = 25
            self.drive(0, 10)
            self.drive(-angle, gamma, False)
            self.drive(angle, 90 - gamma - self.theta2 + 5)
        else:
            gamma = 37
            delta = self.theta2 * 1.7
            self.drive(angle, self.theta2 + delta)
            self.drive(-angle, gamma, False)
            self.drive(angle * 0.8, 90 - gamma - delta)

        wall_is_right = not is_right2

        self.perform_wall_track(wall_is_right, is_forward=False, threshold=-50)
        self.perform_wall_track(wall_is_right, is_forward=True, threshold=50)
        self.send_S()
        self.drive(-angle, 180)
        self.perform_wall_track(wall_is_right, is_forward=True, threshold=50, should_track=True)
        
        #while not self.wall_complete:
            #pass

        

        self.drive(-angle, 90)
        
        
    def calc_arc(self, x, y):
        is_right = x>0
        if not is_right:
            x = -x
        
        r = (x**2 + y**2) / (2*x)
        angle = math.atan(self.chassis_cm / (r - self.wheelbase_cm/2)) * 180 / math.pi
        theta = math.atan(y/(r-x)) * 180 / math.pi
        if angle > 25:
            angle = 25
        if not is_right:
            angle = -angle
        
        return angle, theta
    
    def perform_carpark(self) -> None:
        while self.obstacle_dist1 is None or self.obstacle_dist2 is None:
            pass

        angle = -25
        if self.is_right2:
            angle = 25
        
        y1 = (self.obstacle_dist2 + self.chassis_cm + self.capture_dist2) * math.cos(self.theta2 * math.pi / 180)
        y2 = self.obstacle_dist1 + self.chassis_cm / 2 + self.capture_dist1

        self.logger.debug(f"y1: {y1}, y2: {y2}")
        d1 = 0.7 * y1
        self.drive(0, d1)
        a, d = self.calc_arc(self.wall_dist / 2 + self.wheelbase_cm, y1 - d1 + y2 - self.turning_r * 0.25)
        self.logger.debug(f"a: {a}, d: {d}")
        self.drive(-a if self.is_right2 else a,d)

        gamma = 30
        self.drive(angle, gamma, is_forward=False)
        self.drive(-angle, 90 - gamma - d)

        self.wall_ride(0, self.is_right2, is_forward=False, threshold=-45)
        self.wall_ride(0, self.is_right2, threshold= 45)

        self.drive(angle, 75)
        self.drive_until(0, 15, speed=self.carpark_speed)
        
        self.send_M()

    def perform_wall_track(self, is_right, is_forward = True, threshold=30, should_track=False) -> None:
        if not should_track:
            self.send_D()
        
        self.wall_ride(0, is_right, is_forward=is_forward, threshold=threshold, speed=self.wall_track_speed)
        if should_track:
            self.send_D()

    def wall_ride(self, angle, is_right, threshold=30, is_forward=True, speed=None):
        if speed is None:
            speed = self.drive_speed
        
        char = 'R' if is_right else 'L'
        if not is_forward:
            char = char.lower()
        self.stm_link.send_cmd(char, speed, angle, threshold)

    def drive(self, angle, val, is_forward=True, speed=None):
        if speed is None:
            speed = self.drive_speed
        
        if val < 0:
            val = -val
            is_forward = not is_forward
        self.stm_link.send_cmd("T" if is_forward else "t", speed, angle, val)

    def STMstart(self):
        self.logger.debug("Starting New Method")
        self.perform_toward_obstacle(self.capture_dist1)

    def recv_stm(self) -> None:
        """
        [Child Process] Receive acknowledgement messages from STM32, and release the movement lock
        """
        while True:

            message: str = self.stm_link.recv()
            # Acknowledgement from STM32
            if message.startswith("fM"): #Once movement is done

                self.ack_count += 1

                # Release movement lock
                try:
                    self.movement_lock.release()
                except Exception:
                    self.logger.warning("Tried to release a released lock!")

                self.logger.debug(f"Marked from STM32 received, Mark count now:{self.ack_count}")
                
                self.logger.info(f"self.ack_count: {self.ack_count}")
                #Clearing of Obstacle One
                if self.ack_count == 1: #At the first Obstacle
                    self.small_direction = self.recognise_image("ObstacleFirst_1")
                    direction = self.small_direction["image_id"]
                    self.logger.info(f"HERE small direction is: {direction}")
                    if direction == "39": 
                        #For First Obstacle
                        self.command_queue.put("T40|0|10")
                        self.command_queue.put("T40|-20|30")
                        self.command_queue.put("T40|20|30")
                        self.command_queue.put("T40|0|30")
                        self.command_queue.put("T40|20|90")
                        self.command_queue.put("T40|-20|90")
                        self.command_queue.put("W40|0|30")
                        self.command_queue.put("M0|0|0")
                        #self.command_queue.put("OB01") # ack_count = 3
                        #self.command_queue.put("UL00") # ack_count = 5
                    elif self.small_direction == "38": # Send 2 ack_count
                        self.command_queue.put("T40|0|10")
                        self.command_queue.put("T40|-20|30")
                        self.command_queue.put("T40|20|30")
                        self.command_queue.put("T40|0|30")
                        self.command_queue.put("T40|-20|30")
                        self.command_queue.put("W50|0|30")
                        self.command_queue.put("M0|0|0")
                        self.command_queue.put("M0|0|0")
                    else:
                        self.logger.debug("Arrow not recognised! Going Left as default!")
                        self.command_queue.put("T40|0|10")
                        self.command_queue.put("T40|-20|30")
                        self.command_queue.put("T40|20|30")
                        self.command_queue.put("T40|0|30")
                        self.command_queue.put("T40|20|30")
                        self.command_queue.put("W50|0|30")
                        self.command_queue.put("M0|0|0")

                elif self.ack_count == 2: #Arriving From Left to Second Obstacle
                    self.logger.debug("Finished First Obstacle, From Left")
                    self.small_direction = self.recognise_image("Obstacle2_Left")
                    if self.small_direction == "39": 
                        self.logger.debug("From Left, going Left, clearing obstacle to park")
                        self.command_queue.put("t40|18|10") #reverse from left to straighten
                        self.command_queue.put("T40|-20|20") #
                        self.command_queue.put("W40|0|30")
                        self.command_queue.put("T40|20|20")
                        self.command_queue.put("T40|0|10")
                        self.command_queue.put("T40|20|90")
                        self.command_queue.put("T40|0|10")
                        self.command_queue.put("T40|20|90")
                        self.command_queue.put("T40|0|100")
                        self.command_queue.put("T40|20|90")
                        self.command_queue.put("T40|-20|90")
                        self.command_queue.put("W40|0|20")
                        self.command_queue.put("M0|0|0")
                        self.command_queue.put("M0|0|0")

                    elif self.small_direction == "38": #From Left go Right
                        #self.command_queue.put("UR00") # ack_count = 5
                        self.logger.debug("From Left, going Right, clearing obstacle to park")
                        self.command_queue.put("T40|15|20")
                        self.command_queue.put("T40|0|10")
                        self.command_queue.put("T40|-20|90")
                        self.command_queue.put("T40|0|30")
                        self.command_queue.put("T40|-20|90")
                        self.command_queue.put("T40|0|30")
                        self.command_queue.put("T40|-20|90")
                        self.command_queue.put("T40|0|100")
                        self.command_queue.put("T40|-20|90")
                        self.command_queue.put("T40|20|90")
                        self.command_queue.put("W40|0|20")
                        self.command_queue.put("M0|0|0")
                        self.command_queue.put("M0|0|0")
                    else:
                            #self.command_queue.put("UL00") # ack_count = 5
                        self.logger.debug("Failed first one, going left by default!")
                    # except:
                        # self.logger.info("No need to release near_flag")
            
                elif self.ack_count == 3: #Arriving from Right to Second Obstacle
                    self.logger.debug("Finished First Obstacle, From Right")
                    self.large_direction = self.recognise_image("Obstacle2_Right")
                    time.sleep(1)
                    if self.large_direction == "39": # From Right, go left, then go park
                        #self.command_queue.put("PL01") # ack_count = 6
                        self.logger.debug("From Right, going Left, clearing obstacle to park")
                        self.command_queue.put("t40|18|10") #reverse from left to straighten
                        self.command_queue.put("T40|-20|20") #
                        self.command_queue.put("W40|0|30")
                        self.command_queue.put("T40|20|20")
                        self.command_queue.put("T40|0|10")
                        self.command_queue.put("T40|20|90")
                        self.command_queue.put("T40|0|10")
                        self.command_queue.put("T40|20|90")
                        self.command_queue.put("T40|0|100")
                        self.command_queue.put("T40|20|90")
                        self.command_queue.put("T40|-20|90")
                        self.command_queue.put("W40|0|20")
                        self.command_queue.put("M0|0|0")
                    elif self.large_direction == "38":  #From Right, go Right, then back to park
                        self.logger.debug("From Right, going Right, clearing obstacle to park")
                        self.command_queue.put("t40|-18|20")
                        self.command_queue.put("T40|20|45")
                        self.command_queue.put("T40|-20|90")
                        self.command_queue.put("T40|0|100")

                        #self.command_queue.put("PR01") # ack_count = 6
                    else:
                        self.command_queue.put("PR01") # ack_count = 6
                        self.logger.debug("Failed second one, going right by default!")

                elif self.ack_count == 4: #Total of 4 for both Circuits
                    self.logger.debug("Cark should be parked!")
                    self.android_queue.put(AndroidMessage("status", "finished"))
                    self.command_queue.put("FIN")

                # except Exception:
                #     self.logger.warning("Tried to release a released lock!")
            else:
                self.logger.warning(
                    f"Ignored unknown message from STM: {message}") 
                self.movement_lock.release()
                continue
        
    def android_sender(self) -> None:
        while True:
            try:
                message: AndroidMessage = self.android_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                self.android_link.send(message)
            except OSError:
                self.android_dropped.set()
                self.logger.debug("Event set: Android dropped")

    def command_follower(self) -> None:
        while True:
            command: str = self.command_queue.get()
            self.unpause.wait()
            self.movement_lock.acquire()
            stm32_prefixes = ("w", "T", "t", "W", "D", "d", "M")
            if command.startswith(stm32_prefixes):
                strings = str(command)
                parts = strings.split('|')
                first_part = parts[0]
                flag = first_part[0]
                speed = int(first_part[1:])
                angle = int(parts[1])
                val = int(parts[2])
                self.stm_link.send_cmd(flag,speed,angle,val)
                self.logger.debug(f"In command_follower: Sending to STM32: {command}")

            elif command == "FIN":
                self.unpause.clear()
                self.movement_lock.release()
                self.logger.info("Commands queue finished.")
                self.android_queue.put(AndroidMessage("info", "Commands queue finished."))
                self.android_queue.put(AndroidMessage("status", "finished"))
                self.rpi_action_queue.put(PiAction(cat="stitch", value=""))
            else:
                raise Exception(f"Unknown command: {command}")

    def rpi_action(self):
        while True:
            action: PiAction = self.rpi_action_queue.get()
            self.logger.debug(f"PiAction retrieved from queue: {action.cat} {action.value}")
            if action.cat == "snap": self.recognise_image(obstacle_id=action.value)
            elif action.cat == "stitch": self.request_stitch()

    def recognise_image(self, obstacle_id_with_signal: str) -> None:
        """
        RPi snaps an image and calls the API for image-rec.
        The response is then forwarded back to the android
        :param obstacle_id_with_signal: eg: SNAP<obstacle_id>_<C/L/R>
        """
        obstacle_id, signal = obstacle_id_with_signal.split("_")
        self.logger.info(f"In recognise_image: Capturing image for obstacle id: {obstacle_id}")
        self.android_queue.put(AndroidMessage(
            "info", f"Capturing image for obstacle id: {obstacle_id}"))
        #obstacle_id, signal = "1","C"
        url = f"http://{API_IP}:{API_PORT}/image"
        filename = f"/home/pi/cam/{int(time.time())}_{obstacle_id}_{signal}.jpg"
        filename_send = f"{int(time.time())}_{obstacle_id}_{signal}.jpg"
        results=snap_using_libcamera(self,obstacle_id,signal,filename,filename_send,url,False)
        
        self.movement_lock.acquire()
        # results = json.loads(response.content)
        

        # self.logger.info(f"In recognise_image: results: {results}")
        # self.logger.info(f"In recognise_image: self.obstacles: {self.obstacles}")
        # self.logger.info(
            # f"In recognise_image: Image recognition results: {results} ({SYMBOL_MAP.get(results['image_id'])})")

        # if results['image_id'] == 'NA':
            # self.failed_obstacles.append(
                # self.obstacles[int(results['obstacle_id'])])
            # self.logger.info(
                # f"In recognise_image: Added Obstacle {results['obstacle_id']} to failed obstacles.")
            # self.logger.info(f"In recognise_image: self.failed_obstacles: {self.failed_obstacles}")
        # else:
            # self.success_obstacles.append(
                # self.obstacles[int(results['obstacle_id'])])
            # self.logger.info(
                # f"In recognise_image: self.success_obstacles: {self.success_obstacles}")
        self.android_queue.put(AndroidMessage("image-rec", results))
        self.movement_lock.release()
        return results

    def snap_and_rec(self, obstacle_id: str) -> None:
        """
        RPi snaps an image and calls the API for image-rec.
        The response is then forwarded back to the android
        :param obstacle_id: the current obstacle ID
        """
        
        self.logger.info(f"Capturing image for obstacle id: {obstacle_id}")
        signal = "C"
        url = f"http://{API_IP}:{API_PORT}/image"
        filename = f"{int(time.time())}_{obstacle_id}_{signal}.jpg"
        
        
        con_file    = "PiLCConfig9.txt"
        Home_Files  = []
        Home_Files.append(os.getlogin())
        config_file = "/home/" + Home_Files[0]+ "/" + con_file

        extns        = ['jpg','png','bmp','rgb','yuv420','raw']
        shutters     = [-2000,-1600,-1250,-1000,-800,-640,-500,-400,-320,-288,-250,-240,-200,-160,-144,-125,-120,-100,-96,-80,-60,-50,-48,-40,-30,-25,-20,-15,-13,-10,-8,-6,-5,-4,-3,0.4,0.5,0.6,0.8,1,1.1,1.2,2,3,4,5,6,7,8,9,10,11,15,20,25,30,40,50,60,75,100,112,120,150,200,220,230,239,435]
        meters       = ['centre','spot','average']
        awbs         = ['off','auto','incandescent','tungsten','fluorescent','indoor','daylight','cloudy']
        denoises     = ['off','cdn_off','cdn_fast','cdn_hq']

        config = []
        with open(config_file, "r") as file:
            line = file.readline()
            while line:
                config.append(line.strip())
                line = file.readline()
            config = list(map(int,config))
        mode        = config[0]
        speed       = config[1]
        gain        = config[2]
        brightness  = config[3]
        contrast    = config[4]
        red         = config[6]
        blue        = config[7]
        ev          = config[8]
        extn        = config[15]
        saturation  = config[19]
        meter       = config[20]
        awb         = config[21]
        sharpness   = config[22]
        denoise     = config[23]
        quality     = config[24]
        
        retry_count = 0
        
        while True:
        
            retry_count += 1
        
            shutter = shutters[speed]
            if shutter < 0:
                shutter = abs(1/shutter)
            sspeed = int(shutter * 1000000)
            if (shutter * 1000000) - int(shutter * 1000000) > 0.5:
                sspeed +=1
                
            rpistr = "libcamera-still -e " + extns[extn] + " -n -t 100 -o " + filename
            rpistr += " --brightness " + str(brightness/100) + " --contrast " + str(contrast/100)
            rpistr += " --shutter " + str(sspeed)
            if ev != 0:
                rpistr += " --ev " + str(ev)
            if sspeed > 1000000 and mode == 0:
                rpistr += " --gain " + str(gain) + " --immediate "
            else:    
                rpistr += " --gain " + str(gain)
                if awb == 0:
                    rpistr += " --awbgains " + str(red/10) + "," + str(blue/10)
                else:
                    rpistr += " --awb " + awbs[awb]
            rpistr += " --metering " + meters[meter]
            rpistr += " --saturation " + str(saturation/10)
            rpistr += " --sharpness " + str(sharpness/10)
            rpistr += " --quality " + str(quality)
            rpistr += " --denoise "    + denoises[denoise]
            rpistr += " --metadata - --metadata-format txt >> PiLibtext.txt"

            os.system(rpistr)
            
            
            self.logger.debug("Requesting from image API")
            
            response = requests.post(url, files={"file": (filename, open(filename,'rb'))})

            if response.status_code != 200:
                self.logger.error("Something went wrong when requesting path from image-rec API. Please try again.")
                return

            results = json.loads(response.content)

            # Higher brightness retry
            
            if results['image_id'] != 'NA' or retry_count > 6:
                break
            elif retry_count <= 2:
                self.logger.info(f"Image recognition results: {results}")
                self.logger.info("Recapturing with same shutter speed...")
            elif retry_count <= 4:
                self.logger.info(f"Image recognition results: {results}")
                self.logger.info("Recapturing with lower shutter speed...")
                speed -= 1
            elif retry_count == 5:
                self.logger.info(f"Image recognition results: {results}")
                self.logger.info("Recapturing with lower shutter speed...")
                speed += 3
            
        ans = SYMBOL_MAP.get(results['image_id'])
        self.logger.info(f"Image recognition results: {results} ({ans})")
        return ans

    def request_stitch(self):
        url = f"http://{API_IP}:{API_PORT}/stitch"
        response = requests.get(url)
        if response.status_code != 200:
            self.logger.error("Something went wrong when requesting stitch from the API.")
            return
        self.logger.info("Images stitched!")

    def clear_queues(self):
        while not self.command_queue.empty():
            self.command_queue.get()

    def check_api(self) -> bool:
        url = f"http://{API_IP}:{API_PORT}/status"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                self.logger.debug("API is up!")
                return True
        except ConnectionError:
            self.logger.warning("API Connection Error")
            return False
        except requests.Timeout:
            self.logger.warning("API Timeout")
            return False
        except Exception as e:
            self.logger.warning(f"API Exception: {e}")
            return False



if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()
