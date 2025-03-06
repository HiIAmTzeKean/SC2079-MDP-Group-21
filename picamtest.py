from picamera2 import Picamera2
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()

# Ensure no extra zoom:
picam2.set_controls({"ScalerCrop": picam2.sensor_resolution}) 
# or sometimes the full area is given by (0, 0, width, height)

picam2.capture_file("picamspeed.jpg")
