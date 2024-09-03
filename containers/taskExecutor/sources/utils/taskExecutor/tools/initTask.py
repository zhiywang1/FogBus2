from typing import Union

from ..tasks.base import BaseTask


def initTask(taskName: str) -> Union[BaseTask, None]:
    task = None
    if taskName == 'NaiveFormula0':
        from ..tasks.naiveFormula0 import NaiveFormula0
        task = NaiveFormula0()
    elif taskName == 'NaiveFormula1':
        from ..tasks.naiveFormula1 import NaiveFormula1
        task = NaiveFormula1()
    elif taskName == 'NaiveFormula2':
        from ..tasks.naiveFormula2 import NaiveFormula2
        task = NaiveFormula2()
    elif taskName == 'NaiveFormula3':
        from ..tasks.naiveFormula3 import NaiveFormula3
        task = NaiveFormula3()
    elif taskName == 'DiabetesVoter0':
        from ..tasks.diabetes_voter0 import DiabetesVoter0
        task = DiabetesVoter0()
    elif taskName == 'DiabetesVoter1':
        from ..tasks.diabetes_voter1 import DiabetesVoter1
        task = DiabetesVoter1()
    elif taskName == 'DiabetesVoter2':
        from ..tasks.diabetes_voter2 import DiabetesVoter2
        task = DiabetesVoter2()
    elif taskName.startswith('ObjectDetectionYolov7'):
        from ..tasks.object_detection_yolov7 import ObjectDetectionYoloV7
        task = ObjectDetectionYoloV7()
    elif taskName.startswith('TrafficLightStatus'):
        from ..tasks.trafficLightStatus import TrafficLightStatus
        task = TrafficLightStatus()
    return task
