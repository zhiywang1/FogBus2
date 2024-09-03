import os
from time import time
from .base import ApplicationUserSide
from ...component.basic import BasicComponent


class DiabetesPrediction(ApplicationUserSide):

    def __init__(
            self,
            basicComponent: BasicComponent,
            window_height: int,
            video_path: str,
            task_count: int):
        super().__init__(
            appName='DiabetesPrediction',
            basicComponent=basicComponent)

    def prepare(self):
        pass

    @staticmethod
    def _load_csv(file_path: str):
        csv_data = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines[1:]:
                values = line.strip().split(',')
                float_values = [float(value) for value in values[:-1]]
                csv_data.append(float_values)
        return csv_data

    def _run(self):
        self.basicComponent.debugLogger.info(
            'Application is running: %s', self.appName)
        # load csv file
        curr_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(curr_path, 'diabetes_PIMA.csv')
        data = self._load_csv(file_path)
        with open(f'{file_path}.response_times.csv', 'w+') as file:
            file.write('test_num, voter0, voter1, voter2\n')
            for i in range(20):
                sent_time = time()
                self.dataToSubmit.put(data)
                response_times = {}
                results = {}
                for _ in range(3):
                    res = self.resultForActuator.get()
                    k = ''
                    for key in res.keys():
                        k = key
                        break
                    response_times[k] = (time() - sent_time) * 1000
                    results.update(res)
                from pprint import pprint
                pprint(response_times)

                file.write(f'{i}, '
                           f'{response_times["voter0"]}, '
                           f'{response_times["voter1"]}, '
                           f'{response_times["voter2"]}\n')
            file.close()
        self.basicComponent.debugLogger.info('Done')
