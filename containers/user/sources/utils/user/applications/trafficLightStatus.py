from time import time
from .base import ApplicationUserSide
from ...component.basic import BasicComponent


class TrafficLightStatus(ApplicationUserSide):

    def __init__(
            self,
            basicComponent: BasicComponent,
            window_height: int,
            video_path: str,
            task_count: int):
        super().__init__(
            appName='TrafficLightStatus',
            basicComponent=basicComponent)

    def prepare(self):
        pass

    def _run(self):
        self.basicComponent.debugLogger.info(
            'Application is running: %s', self.appName)
        while True:
            sent_time = time() * 1000
            self.dataToSubmit.put(None)
            result = self.resultForActuator.get()
            print('Result:', result)
            self.responseTime.update(time() * 1000 - sent_time)

            self.basicComponent.debugLogger.info(
                f'Response time: {self.responseTime.median():.3f} ms')
