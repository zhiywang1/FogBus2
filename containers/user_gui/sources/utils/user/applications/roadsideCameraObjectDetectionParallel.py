import json
import os
import re
import base64
import asyncio
import websockets
from http.server import SimpleHTTPRequestHandler, HTTPServer
from time import time
from threading import Thread
from queue import Queue
from PIL import Image
import io
from pprint import pformat
from .base import ApplicationUserSide
from ...component.basic import BasicComponent


class WebServer:
    def __init__(self,
                 host='0.0.0.0',
                 port=8080,
                 root_path='htmlParallel'):
        self.host = host
        self.port = port
        script_path = os.path.dirname(os.path.realpath(__file__))
        self.root_path = os.path.join(script_path, root_path)

    def run(self):
        http_thread = Thread(target=self.start_http_server)
        http_thread.daemon = True
        http_thread.start()

    def start_http_server(self):
        os.chdir(self.root_path)
        server_address = (self.host, self.port)
        httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
        print(f"HTTP server is running on http://{self.host}:{self.port}"
              f"\r\nHTTP root path: {self.root_path}")
        httpd.serve_forever()


class WSServer:
    def __init__(self,
                 frame_in: Queue,
                 frame_out: Queue,
                 host='0.0.0.0',
                 port=8765):
        self.host = host
        self.port = port
        self.frame_in = frame_in
        self.frame_out = frame_out
        self.last_data_sent_time = {}
        self.connected = False

    def run(self):
        websocket_server_thread = Thread(target=self.run_ws_server)
        websocket_server_thread.daemon = True
        websocket_server_thread.start()

    def run_result_handler(self,
                           websocket):
        asyncio.run(self.get_result_frame(websocket))

    async def get_result_frame(self,
                               websocket):
        while True:
            frame, frame_count = self.frame_out.get()
            await websocket.send(frame)

    def run_ws_server(self):
        asyncio.run(self.start_websocket_server())

    async def handler(self,
                      websocket,
                      path):
        if self.connected:
            # potentially race condition
            await websocket.close()
            return
        self.connected = True
        result_thread = Thread(target=self.run_result_handler, args=(websocket,))
        result_thread.daemon = True
        result_thread.start()
        async for message in websocket:
            self.convert_image(message)

    async def start_websocket_server(self):
        print(f"WebSocket server is running on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()

    def convert_image(self,
                      data_str):
        data = json.loads(data_str)
        data_url = data['dataURL']
        frame_count = data['frameCount']
        base64_data = re.sub('^data:image/jpeg;base64,', '', data_url)
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data))

        input_data = {
            'image_size': 640,
            'confidence': 0.25,
            'image': image,
            'frame_count': frame_count,
        }

        self.frame_in.put(input_data)
        self.last_data_sent_time[frame_count] = time()


class RoadsideCameraObjectDetectionParallel(ApplicationUserSide):

    def __init__(
            self,
            basicComponent: BasicComponent):
        super().__init__(
            appName='RoadsideCameraObjectDetectionParallel',
            basicComponent=basicComponent)

        self.web_server = WebServer()
        self.frame_out = Queue()
        self.ws_server = WSServer(self.dataToSubmit, self.frame_out)

    def prepare(self):
        pass

    def _run(self):

        self.web_server.run()
        self.ws_server.run()

        self.basicComponent.debugLogger.info(
            'Application is running: %s', self.appName)

        while True:
            result = self.resultForActuator.get()
            frame_count = result['frame_count']
            plotted_image = result['plotted_image']
            plotted_image = 'data:image/jpeg;base64,' + plotted_image.decode()
            self.ws_server.frame_out.put((plotted_image, frame_count))

            responseTime = (time() - self.ws_server.last_data_sent_time[frame_count]) * 1000
            del self.ws_server.last_data_sent_time[frame_count]

            self.responseTime.update(responseTime)
            self.responseTimeCount += 1

            if 'finalResult' in result:
                break
            self.basicComponent.debugLogger.info(
                'Response time: \r\n%s', self.responseTime)
