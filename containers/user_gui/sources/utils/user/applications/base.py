import threading
from abc import abstractmethod
from queue import Queue
from threading import Event
from time import time

from ...component.basic import BasicComponent
from ...types import SequenceMedian


class ApplicationUserSide:

    def __init__(
            self,
            basicComponent: BasicComponent,
            appName: str,
            videoPath: str = None,
            targetHeight: int = 640,
            pressSpaceToStart: bool = False):
        self.pressSpaceToStart = pressSpaceToStart
        self.basicComponent = basicComponent
        self.appName = appName
        self.sensor = None
        self.resultForActuator: Queue = Queue()
        self.dataToSubmit: Queue = Queue()
        self.targetHeight = targetHeight
        self.videoPath: str = videoPath
        self.responseTime = SequenceMedian(maxRecordNumber=10)
        self.responseTimeCount = 0
        self.windowFrameQueue = None
        self.interval = 1 / 60
        self.canStart: Event = Event()
        if not self.pressSpaceToStart:
            self.canStart.set()
        self.startTime = time() * 1000

    def start(self):
        threading.Thread(target=self._run).start()

    @staticmethod
    def _run():
        raise NotImplementedError

    @abstractmethod
    def prepare(self):
        pass
