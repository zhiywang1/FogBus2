from typing import Tuple

from dotenv import dotenv_values

from .base import Config

environment = dotenv_values()

portRangeStr = environment['USER_PORT_RANGE']
portRange = portRangeStr.split('-')


class ConfigUser(Config):
    portRange: Tuple[int, int] = (int(portRange[0]), int(portRange[1]) + 1)
