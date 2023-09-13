from picamera2 import Picamera2
import time

picam2 = Picamera2()
time.sleep(1)
picam2.start_and_capture_file("image.jpg")