import pickle
import os

from .base import BaseTask


class DiabetesVoter1(BaseTask):
    def __init__(self):
        super().__init__(taskID=202, taskName='DiabetesVoter1')
        path = os.path.dirname(os.path.realpath(__file__))
        self.scaler = pickle.load(open(os.path.join(path, 'diabetes', 'scaler.pkl'), 'rb'))
        self.model = pickle.load(open(os.path.join(path, 'diabetes', 'svc.pkl'), 'rb'))

    def exec(self,
             data):
        self.scaler.transform(data)
        prediction = self.model.predict(data)
        return {'voter1': prediction}
