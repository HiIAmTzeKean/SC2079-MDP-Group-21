from picamera2 import Picamera2


picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)

counter = 0
while True:
    number = input()
    picam2.start()
    picam2.capture_file(f"{number}_no_{counter}.jpg")
    picam2.stop()
    counter += 1