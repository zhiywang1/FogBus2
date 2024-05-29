from typing import Union

from ..applications import ApplicationUserSide
from ..applications import NaiveFormulaParallelized
from ..applications import NaiveFormulaSerialized
from ...component.basic import BasicComponent


def initActuator(
        appName: str,
        basicComponent: BasicComponent
) -> Union[ApplicationUserSide, None]:
    actuator = None
    if appName == 'NaiveFormulaSerialized':
        actuator = NaiveFormulaSerialized(
            basicComponent=basicComponent)
    elif appName == 'NaiveFormulaParallelized':
        actuator = NaiveFormulaParallelized(
            basicComponent=basicComponent)
    return actuator
