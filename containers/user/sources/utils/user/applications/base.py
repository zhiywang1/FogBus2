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
            appName: str):
        self.basicComponent = basicComponent
        self.appName = appName
        self.resultForActuator: Queue = Queue()
        self.dataToSubmit: Queue = Queue()
        self.responseTime = SequenceMedian(maxRecordNumber=10)
        self.responseTimeCount = 0
        self.startTime = time() * 1000

    def start(self):
        threading.Thread(target=self._run).start()

    @staticmethod
    def _run():
        raise NotImplementedError

    @abstractmethod
    def prepare(self):
        pass
