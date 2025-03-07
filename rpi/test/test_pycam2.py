from picamera2 import Picamera2
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()
picam2.capture_file("picamspeed.jpg")
picam2.stop()

picam2.start()
picam2.capture_file("picamspeed2.jpg")
picam2.stop()