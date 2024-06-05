from typing import Union

from ..applications import ApplicationUserSide
from ..applications import RoadsideCameraObjectDetection
from ..applications import RoadsideCameraObjectDetectionParallel
from ...component.basic import BasicComponent


def initActuator(
        appName: str,
        basicComponent: BasicComponent
) -> Union[ApplicationUserSide, None]:
    actuator = None

    if appName == 'RoadsideCameraObjectDetection':
        actuator = RoadsideCameraObjectDetection(
            basicComponent=basicComponent)
    elif appName == 'RoadsideCameraObjectDetectionParallel':
        actuator = RoadsideCameraObjectDetectionParallel(
            basicComponent=basicComponent)
    return actuator
