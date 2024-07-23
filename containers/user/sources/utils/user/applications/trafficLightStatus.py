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

    def _monitor_response_time(self):
        while True:
            curr_time = time() * 1000
            rs = self.responseTime.median()
            self.basicComponent.debugLogger.info(
                f'Smart Traffic Light TS: {curr_time} Monitored Response Time: {rs:.3f} ms')
            sleep(0.01)

    def _run(self):
        Thread(target=self._monitor_response_time).start()
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
            self.responseTime.update(time() * 1000 - sent_time)
            self.basicComponent.debugLogger.info(
                f'{request} #'
                f' Response time: {self.responseTime.median():.3f} ms'
                f' Computation time: {computation_time:.3f} ms')
            request += 1
