from queue import Queue
from typing import Any
from typing import Callable
from typing import Tuple
from time import sleep, time
import cv2

from ...component.basic import BasicComponent


class WindowManager:
    def __init__(
            self,
            basicComponent: BasicComponent,
            frameQueue: Queue[Tuple[str, Any]],
            prepareWindows: Callable):
        self.basicComponent = basicComponent
        self.prepareWindows = prepareWindows
        self.frameQueue = frameQueue
        self.prepareWindows()
        self.interval = 1 / 60

    def run(self):
        lastUpdatedTime = time()
        while True:
            windowName, frame = self.frameQueue.get()
            currentTime = time()
            timeDiff = currentTime - lastUpdatedTime
            if timeDiff < self.interval:
                sleep(self.interval - timeDiff)
            lastUpdatedTime = currentTime
            cv2.imshow(windowName, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
