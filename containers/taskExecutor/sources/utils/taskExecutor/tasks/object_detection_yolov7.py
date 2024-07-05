import os
from .base import BaseTask
from yolov7 import Yolov7


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
        # print(result)
        return result
