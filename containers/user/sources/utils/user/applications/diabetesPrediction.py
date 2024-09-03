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
            for line in lines:
                values = line.strip().split(',')
                float_values = [float(value) for value in values[:-1]]
                csv_data.append(float_values)
        return csv_data

    def _run(self):
        self.basicComponent.debugLogger.info(
            'Application is running: %s', self.appName)
        # load csv file
        data = self._load_csv('diabetes_PIMA.csv')
        self.dataToSubmit.put(data)
        results = {}
        from pprint import pprint
        for _ in range(3):
            res = self.resultForActuator.get()
            pprint(res)
            results.update(res)
