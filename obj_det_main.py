import argparse
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import MappedArray, Picamera2, Preview
from core.vehicle import Vehicle

normalSize = (640, 480)
lowresSize = (320, 240)
rectangles = []


class ObjDetModel:
    def __init__(self):
        model_path = '/home/pi/Freenove/Code/Server/object_detection/ssd_mobilenet.tflite'
        label_path = '/home/pi/Freenove/Code/Server/object_detection/coco_labels.txt'
        self.score_threshold = 0.5
        self.labels = self.read_labels(target_labels_file)
        self._initialize_interpreter(model_checkpoint_file)

    def _initialize_interpreter(self, model_checkpoint_file):
        self.interpreter = tflite.Interpreter(model_path=model_checkpoint_file, num_threads=4)
        self.interpreter.allocate_tensors()
        self.interpreter_details = {'input': self.interpreter.get_input_details(),
                                    'output': self.interpreter.get_output_details()}
        self.interpreter_details['height'] = self.interpreter_details['input'][0]['shape'][1]
        self.interpreter_details['width'] = self.interpreter_details['input'][0]['shape'][2]
        self.interpreter_details['dtype'] = self.interpreter_details['input'][0]['dtype']

    def read_labels(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        ret = {}
        for line in lines:
            pair = line.strip().split(maxsplit=1)
            ret[int(pair[0])] = pair[1].strip()
        return ret

    def preprocess_image(self, image):
        floating_model = (self.interpreter_details['dtype'] == np.float32)
        width = self.interpreter_details['width']
        height = self.interpreter_details['height']
        #rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        rgb = image
        initial_shapes = self.create_initial_shape_dict(rgb.shape)
        picture = cv2.resize(rgb, (width, height))
        input_data = np.expand_dims(picture, axis=0)
        if floating_model:
            input_data = (np.float32(input_data) - 127.5) / 127.5
        return input_data, initial_shapes

    def create_initial_shape_dict(self, shapes):
        initial_h, initial_w, channels = shapes
        return {'height': initial_h, 'width': initial_w, 'channels': channels}

    def predict(self, image):
        input_data, initial_shapes = self.preprocess_image(image)
        self.interpreter.set_tensor(self.interpreter_details['input'][0]['index'], input_data)
        self.interpreter.invoke()
        detected_boxes = self.interpreter.get_tensor(self.interpreter_details['output'][0]['index'])
        detected_classes = self.interpreter.get_tensor(self.interpreter_details['output'][1]['index'])
        detected_scores = self.interpreter.get_tensor(self.interpreter_details['output'][2]['index'])
        num_boxes = self.interpreter.get_tensor(self.interpreter_details['output'][3]['index'])
        rectangles = []
        for i in range(int(num_boxes)):
            top, left, bottom, right = detected_boxes[0][i]
            classId = int(detected_classes[0][i])
            score = detected_scores[0][i]
            if score > self.score_threshold:
                xmin = left * initial_shapes['width']
                ymin = bottom * initial_shapes['height']
                xmax = right * initial_shapes['width']
                ymax = top * initial_shapes['height']
                box  = [xmin, ymin, xmax, ymax]
                rectangles.append(box)
                rectangles[-1].append(self.labels[classId])
        return rectangles

    def draw_boxes(self, request):
        def draw_rect(rect) -> None:
            rect_start = (int(rect[0] * 2) - 5, int(rect[1] * 2) - 5)
            rect_end = (int(rect[2] * 2) + 5, int(rect[3] * 2) + 5)
            cv2.rectangle(m.array, rect_start, rect_end, (0, 255, 0, 0))
        def draw_label(rect) -> None:
            class_name = rect[4]
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(m.array, class_name, (int(rect[0] * 2) + 10, int(rect[1] * 2) + 10),
                        font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        with MappedArray(request, "main") as m:
            for rect in rectangles:
                draw_rect(rect)
                if len(rect) == 5:
                    draw_label(rect)


if __name__ == '__main__':
    model_path = '/home/pi/Freenove/Code/Server/object_detection/ssd_mobilenet.tflite'
    label_path = '/home/pi/Freenove/Code/Server/object_detection/coco_labels.txt'
    model = ObjDetModel(model_path, label_path)
    vehicle = Vehicle()
    while True:
        img = vehicle.get_vision()
        model.predict(img)
