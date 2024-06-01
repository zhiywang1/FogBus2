import os
import base64
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
from .base import BaseTask


class ObjectDetection(BaseTask):
    def __init__(self):
        super().__init__(taskID=108, taskName='RoadsideCameraObjectDetection')
        curr_script_path = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(curr_script_path, "yolov10s.pt")
        print(model_path)
        if not os.path.exists(model_path):
            raise Exception("please download the model:"
                            "wget https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10s.pt")
        self.model = YOLO(model_path)

    @staticmethod
    def np_arr_to_base64(
            np_arr):
        buffered = BytesIO()
        # Convert numpy array to PIL Image
        img = Image.fromarray(np_arr)
        # Create a BytesIO object
        # Save image to BytesIO object
        img.save(buffered, format="JPEG")
        # Get image data
        img_str = buffered.getvalue()
        # Encode image data to base64
        img_str_base64 = base64.b64encode(img_str)
        return img_str_base64

    def exec(self,
             input_data):
        image = input_data['image']
        if 'image_size' in input_data:
            image_size = input_data['image_size']
        else:
            image_size = 640
        if 'confidence' in input_data:
            confidence = input_data['confidence']
        else:
            confidence = 0.25

        res = self.model.predict(
            source=image,
            imgsz=image_size,
            conf=confidence)[0]
        full_labels = res.names
        boxes = res.boxes
        label_indexes = [int(i) for i in list(boxes.cls)]
        res_labels = {k: full_labels[k] for k in label_indexes if k in full_labels}
        object_counts = {full_labels[k]: label_indexes.count(k) for k in label_indexes if k in full_labels}
        predictor = self.model.predictor
        plotted_img = res.plot(
            line_width=predictor.args.line_width,
            boxes=predictor.args.show_boxes,
            conf=predictor.args.show_conf,
            labels=predictor.args.show_labels)

        result = {
            'plotted_image': self.np_arr_to_base64(plotted_img),
            'object_counts': object_counts,
            'res_labels': res_labels,
            'frame_count': input_data['frame_count']
        }
        return result
