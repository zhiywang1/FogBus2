from typing import Union

from ..tasks import *


def initTask(taskName: str) -> Union[BaseTask, None]:
    task = None
    if taskName == 'RoadsideCameraObjectDetection':
        task = ObjectDetection()

    return task
