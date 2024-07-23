import os
import sys
from time import time
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

        start_time = time()
        objects = self.yolov7.detect(image)
        computation_time = (time() - start_time) * 1000
        result = {
            'objects': objects,
            'frame_count': input_data['frame_count'],
            'computation_time': computation_time
        }
        print(f'Frame count: {input_data["frame_count"]}, objects count: {len(objects)}')
        return result
