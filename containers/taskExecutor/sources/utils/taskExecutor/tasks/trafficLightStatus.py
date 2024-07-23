import requests
from time import time

from .base import BaseTask


class TrafficLightStatus(BaseTask):
    def __init__(self):
        super().__init__(taskID=202, taskName='TrafficLightStatus')

        self.traffic_lights = [
            ('Junction 1', '100.118.67.2'),
            ('Junction 2', '100.101.191.76'),
            ('Junction 3', '100.74.59.69'),
            ('Junction 4', '100.68.188.100'),
        ]

    @staticmethod
    def get_light_status(host, port=8000):
        api_url = f'http://{host}:{port}/light_status'
        response = requests.get(api_url)
        return response.json()

    def exec(self, request_count):
        print('Received request # ', request_count)
        results = {}
        start_time = time()
        for junction, host in self.traffic_lights:
            results[junction] = self.get_light_status(host)
        computation_time = (time() - start_time) * 1000

        print('results: ', results)
        return {'results': results, 'computation_time': computation_time}
