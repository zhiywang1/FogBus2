from time import time, sleep
from threading import Thread
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
            output = self.resultForActuator.get()
            result = output['results']
            computation_time = output['computation_time']
            print('Result:', result)
            response_time = time() * 1000 - sent_time
            self.responseTime.update(response_time)
            self.basicComponent.debugLogger.info(
                f'{request} #'
                f' Response time: {response_time:.3f} ms'
                f' Computation time: {computation_time:.3f} ms')
            request += 1
