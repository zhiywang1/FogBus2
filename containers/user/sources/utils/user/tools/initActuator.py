from typing import Union

from ..applications import ApplicationUserSide
from ..applications import NaiveFormulaParallelized
from ..applications import NaiveFormulaSerialized
from ..applications import ObjectDetection
from ..applications import TrafficLightStatus
from ...component.basic import BasicComponent


def initActuator(
        appName: str,
        basicComponent: BasicComponent,
        *args,
        **kwargs,
) -> Union[ApplicationUserSide, None]:
    actuator = None
    if appName == 'NaiveFormulaSerialized':
        actuator = NaiveFormulaSerialized(
            basicComponent=basicComponent)
    elif appName == 'NaiveFormulaParallelized':
        actuator = NaiveFormulaParallelized(
            basicComponent=basicComponent)
    elif appName == 'ObjectDetection':
        actuator = ObjectDetection(
            basicComponent=basicComponent,
            *args, **kwargs)
    elif appName == 'TrafficLightStatus':
        actuator = TrafficLightStatus(
            basicComponent=basicComponent,
            *args, **kwargs)
    return actuator
