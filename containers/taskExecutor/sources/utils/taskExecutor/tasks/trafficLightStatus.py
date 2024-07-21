from concurrent.futures import ThreadPoolExecutor
import requests

from .base import BaseTask


class TrafficLightStatus(BaseTask):
    def __init__(self):
        super().__init__(taskID=202, taskName='TrafficLightStatus')

        self.traffic_lights = [
            ('Junction 1', 'traffic-light-1.great-dace.ts.net'),
            ('Junction 2', 'traffic-light-2.great-dace.ts.net'),
            ('Junction 3', 'traffic-light-3.great-dace.ts.net'),
            ('Junction 4', 'traffic-light-4.great-dace.ts.net'),
        ]

    @staticmethod
    def get_light_status( host, port=8000):
        api_url = f'http://{host}:{port}/light_status'
        response = requests.get(api_url)
        return response.json()

    def exec(self, inputData):
        results = {}
        for junction, host in self.traffic_lights:
            results[junction] = self.get_light_status(host)
        return results
