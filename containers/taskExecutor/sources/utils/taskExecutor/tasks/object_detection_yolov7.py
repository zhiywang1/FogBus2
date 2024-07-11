import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(__file__) + '/yolov7')
from yolov7 import Yolov7
from .base import BaseTask


class ObjectDetectionYoloV7(BaseTask):
    def __init__(self):
        super().__init__(taskID=201, taskName='ObjectDetectionYolov7')
        script_path = os.path.dirname(os.path.abspath(__file__))
        self.yolov7 = Yolov7(os.path.join(script_path, 'yolov7/yolov7-tiny.pt'))
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning)

    def exec(self,
             input_data):
        image = input_data['image']
        objects = self.yolov7.detect(image)
        result = {
            'objects': objects,
            'frame_count': input_data['frame_count']
        }
        print(f'Frame count: {input_data["frame_count"]}, objects count: {len(objects)}')
        return result
