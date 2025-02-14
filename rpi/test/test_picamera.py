import time

from picamera import PiCamera


for run_num in range(6):
    
    filename = f"/home/rpi21/cam/test{run_num}.jpg"

    my_file = open(filename, "wb")
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.start_preview()
        camera.capture(filename)
        camera.stop_preview()
        
        
    time.sleep(4)