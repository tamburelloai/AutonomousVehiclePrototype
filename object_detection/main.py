"""Main script to run the object detection routine."""
import argparse
import sys
import time
import numpy as np
import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import utils
import tflite_runtime.interpreter as tflite
# import the necessary packages
from picamera.array import PiRGBArray
from picamera2 import PiCamera
import time
import cv2


def run():
    # Load the TFLite model
    model_path = '/home/pi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server/object_detection/efficientdet_lite0.tflite'
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    
    # initialize the camera and grab a reference to the raw camera capture
    camera = Picamera2()
    #camera.start()
    time.sleep(1)
    print("Camera Initialized")
    
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))
    
    
    while True:
        ret, frame = cap.read()
        # Preprocess the input image
        input_image = cv2.resize(frame, (input_details[0]['shape'][2], input_details[0]['shape'][1]))
        input_image = np.expand_dims(input_image, axis=0)

        # Set the input tensor
        interpreter.set_tensor(input_details[0]['index'], input_image)

        # Run inference
        interpreter.invoke()

        # Get the output tensor
        output_data = interpreter.get_tensor(output_details[0]['index'])

        # Process the output data to identify objects and draw bounding boxes
        # You'll need to adapt this part to your specific model and label file

        # Display the results on the screen
        cv2.imshow('Object Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run()