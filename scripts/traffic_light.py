from time import time
from flask import Flask


class TrafficLight:

    def __init__(self, lights=('red', 'green', 'yellow'), light_durations=(60, 60, 5)):
        self.start_time = time()
        self.lights = lights
        self.light_durations = light_durations
        self.total_duration = sum(self.light_durations)

    def get_light_status(self):
        curr_time = time()
        elapsed_time = (curr_time - self.start_time) % self.total_duration
        for i in range(len(self.lights)):
            if elapsed_time >= self.light_durations[i]:
                elapsed_time -= self.light_durations[i]
                continue
            return self.lights[i], self.light_durations[i] - elapsed_time
        return '', -1


class TrafficLightAPIServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.traffic_light = TrafficLight()

        @self.app.route('/light_status', methods=['GET'])
        def get_light_status():
            light, remaining_time = self.traffic_light.get_light_status()
            return {'light': light, 'remaining_time': remaining_time}

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    server = TrafficLightAPIServer()
    server.run(port=8000)
