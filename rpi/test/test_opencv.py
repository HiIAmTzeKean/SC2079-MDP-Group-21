import cv2 as cv
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (640,480)
output = PiRGBArray(camera)
camera.capture(output,'bgr')
src = output.array
src_gray = cv.cvtColor(src,cv.COLOR_BGR2GRAY)
dst=cv.blur(src_gray,(5,5))
cv.imwrite('test.jpg',dst)
cv.waitKey(0)