#!/usr/bin/env python3
import json
import math
import os
import queue
import time
from multiprocessing import Manager, Process
from typing import Optional

import requests
from communication.android import AndroidLink, AndroidMessage
from communication.camera import snap_using_libcamera
from communication.stm32 import STMLink
from consts import SYMBOL_MAP
from logger import prepare_logger
from constant.settings import API_IP, API_PORT


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
        self.log = prepare_logger()
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
        self.proc_rpi_action = None

        self.num_M = 0
        self.num_obstacle = 1
        self.lock = self.manager.Lock()

        self.right1 = False
        self.right2 = False
        self.done_obstacle2 = False

        self.on_arrow_callback = None

        self.capture_dist1 = 30
        self.capture_dist2 = 20

        self.dist1 = None
        self.dist2 = None
        self.wall_dist = None
        self.wall_complete = False

        #For Tuning with new car
        self.turnRad = 40 # Set for Turning Radius
        self.chassis_cm = 15 # Length from Axle to Axle
        self.wheelbase_cm = 16.5 # length between front wheels 

        # Tune to Balance Speed with Precision
        self.theta2 = 10
        self.targetDrive_speed = 60
        self.obstacle_speed = 55
        self.track_wall_speed = 60
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
            self.check_server()
            

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

            self.log.info("Child Processes started")

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
        self.log.info("Program exited!")

    def reconnect_android(self):
        """Handles the reconnection to Android in the event of a lost connection."""
        self.log.info("Reconnection handler is watching...")

        while True:
            # Wait for android connection to drop
            self.android_dropped.wait()

            self.log.error("Android link is down!")

            # Kill child processes
            self.log.debug("Killing android child processes")
            self.proc_android_sender.kill()
            self.proc_recv_android.kill()

            # Wait for the child processes to finish
            self.proc_android_sender.join()
            self.proc_recv_android.join()
            assert self.proc_android_sender.is_alive() is False
            assert self.proc_recv_android.is_alive() is False
            self.log.debug("Android child processes killed")

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

            self.log.info("Android child processes restarted")
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
                self.log.debug("Event set: Android connection dropped")

            # If an error occurred in recv()
            if msg_str is None:
                continue

            message: dict = json.loads(msg_str)

            ## Command: Start Moving ##
            if message['cat'] == "control":
                if message['value'] == "start":
        
                    if not self.check_server():
                        self.log.error("API is down! Start command aborted.")

                    self.clear_queues()
                    #self.command_queue.put("D0|0|0")
                    #self.command_queue.put("W50|0|30") # ack_count = 1 //Move to Target
                    #self.command_queue.put("M0|0|0")
                    self.log.info("Start command received, starting robot on Week 9 task!")
                    self.android_queue.put(AndroidMessage('status', 'running'))
                    
                    self.unpause.set()
                    self.Task2_start()

    def tryrecv_stm(self) -> None:
        """
        [Child Process] Just to try thier method out
        """
        while True:
            try:
                #message : str = self.stm_link.recv()
                messages = self.stm_link.wait_receive()
                self.log.debug(f"All Messages: {messages}")
                
                for message in messages.split('\n'):
                    if len(message) == 0:
                        continue
                    self.log.debug(f"Message received from STM: {message}")
                    if "M" in message:

                        if self.num_M == 0:
                            self.log.debug("First M Send!")
                        elif self.num_M == 1:
                            self.back_ToPark()
                        elif self.num_M == 2:
                            self.android_queue.put(AndroidMessage("status", "finished"))
                            self.command_queue.put("FIN")

                        self.num_M +=1

                    elif "D" in message:
                        dist_val_str = message.replace("fD", "").replace("\0", '').strip()
                        if len(dist_val_str) == 0:
                            # Robot is beginning targetDrive towards obstacle, take in latest_image then decide
                            if self.num_obstacle == 1:
                                try:
                                    self.small_direction = self.recognise_image("ObstacleFirst_1")
                                    direction = self.small_direction["image_id"]
                                except Exception as e:
                                    direction = self.LEFT_ARROW_ID
                                self.log.debug(f"Obstacle 1: {direction}")
                                if direction == self.RIGHT_ARROW_ID:
                                    self.log.debug("First Obstacle: Right Arrow Detected")
                                    self.obst1_respond(True)
                                elif direction == self.LEFT_ARROW_ID:
                                    self.log.debug("Second Obstacle: Left Arrow Detected")
                                    self.obst1_respond(False)
                                else:
                                    self.obst1_respond(False)

                            elif self.num_obstacle == 2: ## Second Obstacle
                                try:
                                    self.large_direction = self.recognise_image("ObstacleSecond_1")
                                #self.movement_lock.acquire()
                                    direction = self.large_direction["image_id"]
                                except Exception as e:
                                    direction = self.LEFT_ARROW_ID
                                #self.movement_lock.release()
                                self.log.debug(f"Obstacle 2: {direction}")
                                
                                if direction == self.RIGHT_ARROW_ID:
                                    self.log.debug("Second Obstacle: Right Arrow Detected")
                                    self.obst2_respond(True)
                                elif direction == self.LEFT_ARROW_ID:
                                    self.log.debug("Second Obstacle: Left Arrow Detected")
                                    self.obst2_respond(False)
                                else:
                                    #self.on_arrow_callback = self.obst2_respond
                                    self.obst2_respond(True)
                            
                            self.num_obstacle += 1
                        else:
                            # Get distance travelled
                            self.log.debug(f"Content in dist_val_str: {dist_val_str}")
                            dist_val = float(dist_val_str)

                            with self.lock:
                                if self.dist1 is None:
                                    self.dist1 = dist_val
                                    self.log.debug(f"Obstacle 1 Distance: {self.dist1}")
                                elif self.dist2 is None:
                                    self.dist2 = dist_val
                                    self.log.debug(f"Obstacle 2 Distance: {self.dist2}")
                                elif self.wall_dist is None:
                                    #self.wall_dist = dist_val + 22.5
                                    self.wall_dist = dist_val + 32.5
                                    self.log.debug(f"Wall Distance: {self.wall_dist}")
                                    self.wall_complete = True
                                    self.log.debug(f"Wall Complete: {self.wall_complete}")
            except OSError as e:
                self.log.debug(f"Error in receiving STM Data: {e}")
                    
                

    def targetDrive_until(self, angle, val, is_forward=True, speed=None):
        if speed is None:
            speed = self.targetDrive_speed
        
        self.stm_link.send_cmd("W" if is_forward else "w", speed, angle, val)

    def obst1_respond(self, is_right) -> None:
        with self.lock:
            self.right1 = is_right
        
        self.clear_obs1(is_right)
        self.travel_to_obstacle()

        self.on_arrow_callback = None

    def obst2_respond(self, is_right) -> None:
        with self.lock:
            self.done_obstacle2 = True
            self.right2 = is_right
        
        self.clear_obs2(self.right1, is_right)
        self.on_arrow_callback = None
        self.send_M()
        
        

    def travel_to_obstacle(self, capture_dist=30) -> None:
        self.send_D()
        self.targetDrive_until(0, capture_dist, speed=self.obstacle_speed)
        self.send_D()

    
    def clear_obs1(self, is_right) -> None:
        angle = 25 if is_right else -25
        angle2 = 23 if is_right else -23
        turn_theta = 33
        self.targetDrive(angle2, turn_theta)
        self.targetDrive(0, 18)
        self.targetDrive(-angle, turn_theta + self.theta2-2)
        self.send_M()

    def clear_obs2(self, right1, right2) -> None:
        is_cross = right1 != right2
        angle = 25 if right2 else -25
        angle2 = 22 if right2 else -22

        if is_cross:
            gamma = 28
            #gamma = 35
            self.targetDrive(0, 10)
            self.targetDrive(-angle, gamma, False)
            self.targetDrive(angle, 90 - gamma - self.theta2)
        else:
            gamma = 25 
            delta = self.theta2 * 1.7
            self.targetDrive(angle, self.theta2 + delta)
            self.targetDrive(-angle, gamma, False)
            self.targetDrive(angle * 0.8, 90 - gamma - delta)

        wall_is_right = not right2

        self.track_wall(wall_is_right, is_forward=False, threshold=-50)
        self.track_wall(wall_is_right, is_forward=True, threshold=50)
        self.send_S()
        #self.targetDrive(-angle, 180)
        self.targetDrive(-angle2,180)
        self.track_wall(wall_is_right, is_forward=True, threshold=50, should_track=True)
        
        #while not self.wall_complete:
            #pass

        

        self.targetDrive(-angle, 90)
        
        
    def calc_turn_in(self, x, y):
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
    
    def back_ToPark(self) -> None:
        while self.dist1 is None or self.dist2 is None:
            pass

        angle = -25
        if self.right2:
            angle = 25
        
        y1 = (self.dist2 + self.chassis_cm + self.capture_dist2) * math.cos(self.theta2 * math.pi / 180)
        y2 = self.dist1 + self.chassis_cm / 2 + self.capture_dist1

        self.log.debug(f"y1: {y1}, y2: {y2}")
        #if y1 > 80:
            #d2 = 0.85*y1
        #else:
            #d2 = 0.95*y1
        d2 = 0.95*y1
        d1 = 0.8* y1
        #d2 = 0.95 * y1
        
        self.targetDrive(0, d2)
        a, d = self.calc_turn_in(self.wall_dist / 2 + self.wheelbase_cm, y1 - d1 + y2 - self.turnRad * 0.25)
        self.log.debug(f"a: {a}, d: {d}")
        #a -= 2
        #if a > 3:
         #   a -= 3
        #elif a < -3:
         #   a += 3
        self.targetDrive(-a if self.right2 else a,d)

        gamma = 30
        gamma2 = 37
        self.targetDrive(angle, gamma, is_forward=False)
        self.targetDrive(-angle, 90 - gamma2 - d)

        self.ride_wall(0, self.right2, is_forward=False, threshold=-45)
        self.ride_wall(0, self.right2, threshold= 45)

        self.targetDrive(angle, 80)
        
        self.targetDrive_until(0, 20, speed=self.carpark_speed)
        #self.targetDrive(0, 20)
        
        self.send_M()

    def track_wall(self, is_right, is_forward = True, threshold=30, should_track=False) -> None:
        if not should_track:
            self.send_D()
        
        self.ride_wall(0, is_right, is_forward=is_forward, threshold=threshold, speed=self.track_wall_speed)
        if should_track:
            self.send_D()

    def ride_wall(self, angle, is_right, threshold=30, is_forward=True, speed=None):
        if speed is None:
            speed = self.targetDrive_speed
        
        char = 'R' if is_right else 'L'
        if not is_forward:
            char = char.lower()
        self.stm_link.send_cmd(char, speed, angle, threshold)

    def targetDrive(self, angle, val, is_forward=True, speed=None):
        if speed is None:
            speed = self.targetDrive_speed
        
        if val < 0:
            val = -val
            is_forward = not is_forward
        self.stm_link.send_cmd("T" if is_forward else "t", speed, angle, val)

    def Task2_start(self):
        self.log.debug("Starting New Method")
        self.travel_to_obstacle(self.capture_dist1)

    
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
                self.log.debug("Event set: Android dropped")

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
                self.log.debug(f"In command_follower: Sending to STM32: {command}")

            elif command == "FIN":
                self.unpause.clear()
                self.movement_lock.release()
                self.log.info("Commands queue finished.")
                self.android_queue.put(AndroidMessage("info", "Commands queue finished."))
                self.android_queue.put(AndroidMessage("status", "finished"))
                self.rpi_action_queue.put(PiAction(cat="stitch", value=""))
            else:
                raise Exception(f"Unknown command: {command}")

    def rpi_action(self):
        while True:
            action: PiAction = self.rpi_action_queue.get()
            self.log.debug(f"PiAction retrieved from queue: {action.cat} {action.value}")
            if action.cat == "snap": self.recognise_image(obstacle_id=action.value)
            elif action.cat == "stitch": self.request_stitch()

    def recognise_image(self, obstacle_id_with_signal: str) -> None:
        """
        RPi snaps an image and calls the API for image-rec.
        The response is then forwarded back to the android
        :param obstacle_id_with_signal: eg: SNAP<obstacle_id>_<C/L/R>
        """
        obstacle_id, signal = obstacle_id_with_signal.split("_")
        self.log.info(f"In recognise_image: Capturing image for obstacle id: {obstacle_id}")
        self.android_queue.put(AndroidMessage(
            "info", f"Capturing image for obstacle id: {obstacle_id}"))
        #obstacle_id, signal = "1","C"
        url = f"http://{API_IP}:{API_PORT}/image"
        filename = f"/home/pi/cam/{int(time.time())}_{obstacle_id}_{signal}.jpg"
        filename_send = f"{int(time.time())}_{obstacle_id}_{signal}.jpg"
        results=snap_using_libcamera(self,obstacle_id,signal,filename,filename_send,url,False)
        
        self.movement_lock.acquire()
        # results = json.loads(response.content)
        

        # self.log.info(f"In recognise_image: results: {results}")
        # self.log.info(f"In recognise_image: self.obstacles: {self.obstacles}")
        # self.log.info(
            # f"In recognise_image: Image recognition results: {results} ({SYMBOL_MAP.get(results['image_id'])})")

        # if results['image_id'] == 'NA':
            # self.failed_obstacles.append(
                # self.obstacles[int(results['obstacle_id'])])
            # self.log.info(
                # f"In recognise_image: Added Obstacle {results['obstacle_id']} to failed obstacles.")
            # self.log.info(f"In recognise_image: self.failed_obstacles: {self.failed_obstacles}")
        # else:
            # self.success_obstacles.append(
                # self.obstacles[int(results['obstacle_id'])])
            # self.log.info(
                # f"In recognise_image: self.success_obstacles: {self.success_obstacles}")
        self.android_queue.put(AndroidMessage("image-rec", results))
        self.movement_lock.release()
        return results

    def request_stitch(self):
        url = f"http://{API_IP}:{API_PORT}/stitch"
        response = requests.get(url)
        if response.status_code != 200:
            self.log.error("Something went wrong when requesting stitch from the API.")
            return
        self.log.info("Images stitched!")

    def clear_queues(self):
        while not self.command_queue.empty():
            self.command_queue.get()

    def check_server(self) -> bool:
        url = f"http://{API_IP}:{API_PORT}/status"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                self.log.debug("API is up!")
                return True
        except ConnectionError:
            self.log.warning("API Connection Error")
            return False
        except requests.Timeout:
            self.log.warning("API Timeout")
            return False
        except Exception as e:
            self.log.warning(f"API Exception: {e}")
            return False



if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()
