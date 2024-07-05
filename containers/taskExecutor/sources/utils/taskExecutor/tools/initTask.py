from typing import Union

from ..tasks import *


def initTask(taskName: str) -> Union[BaseTask, None]:
    task = None
    if taskName == 'NaiveFormula0':
        task = NaiveFormula0()
    elif taskName == 'NaiveFormula1':
        task = NaiveFormula1()
    elif taskName == 'NaiveFormula2':
        task = NaiveFormula2()
    elif taskName == 'NaiveFormula3':
        task = NaiveFormula3()
    elif taskName.startswith('ObjectDetectionYolov7'):
        task = ObjectDetectionYoloV7()

    return task
