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
        request = 0
        while True:
            sent_time = time() * 1000
            self.dataToSubmit.put(request)
            self.basicComponent.debugLogger.info('Request sent #: %d', request)
            result = self.resultForActuator.get()
            print('Result:', result)
            self.responseTime.update(time() * 1000 - sent_time)
            self.basicComponent.debugLogger.info(
                f'{request} # Response time: {self.responseTime.median():.3f} ms')
            if result > 1000:
                import os
                os._exit(0)
            request += 1
