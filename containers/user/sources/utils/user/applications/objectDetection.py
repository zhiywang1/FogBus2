import cv2
from time import time, sleep
from random import randint
from queue import Queue
from typing import Any, Tuple
from threading import Thread
from .base import ApplicationUserSide
from ...component.basic import BasicComponent


class ObjectDetection(ApplicationUserSide):

    def __init__(
            self,
            basicComponent: BasicComponent,
            window_height: int,
            video_path: str,
            task_count: int):
        super().__init__(
            appName='ObjectDetection',
            basicComponent=basicComponent)
        self.target_height = 480
        self.show_window = True if window_height is not None else False
        self.video_path = video_path
        self.window_height = window_height
        self.window_frame_queue: Queue[Tuple[str, Any]] = Queue()

        self.fps = 30
        self.sent_times = [0 for _ in range(self.fps)]
        self.task_count = task_count
        self.last_sent_frame = 0
        self.frames = Queue(self.task_count)

    def prepare(self):
        pass

    def _send_frame(self, frame_count: int):
        ret, frame = self.sensor.read()
        if not ret:
            self._set_sensor()
            return True
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb_resized = cv2.resize(frame_rgb, (self.target_height, self.target_height))
        input_data = {
            'image': frame_rgb_resized,
            'frame_count': frame_count,
        }
        self.sent_times[frame_count % self.fps] = time()
        self.frames.put((frame_count, frame))
        self.dataToSubmit.put(input_data)
        # print('Sent frame:', frame_count)
        return True

    def _set_sensor(self):
        if self.video_path is None:
            self.sensor = cv2.VideoCapture(0)
        else:
            self.sensor = cv2.VideoCapture(self.video_path)

    def _frame_sender(self):
        self.basicComponent.debugLogger.info('Frame sender started')
        self._set_sensor()
        frame_count = 0
        last_sent_time = time()
        while True:
            curr_time = time()
            time_diff = curr_time - last_sent_time
            if time_diff < 1 / self.fps:
                sleep(1 / self.fps - time_diff)
            ret = self._send_frame(frame_count)
            last_sent_time = curr_time
            if not ret:
                break
            self.last_sent_frame = frame_count
            frame_count += 1
        self.sensor.release()

    def _run(self):
        self.basicComponent.debugLogger.info(
            'Application is running: %s', self.appName)
        Thread(target=self._frame_sender).start()
        draw_times = []
        pre_time = time()
        while True:
            result = self.resultForActuator.get()
            frame_count = result['frame_count']
            self.responseTime.update((time() - self.sent_times[frame_count % self.fps]) * 1000)

            objects = result['objects']
            i, curr_time = 0, time()
            fps = 1 / (curr_time - pre_time)
            self.basicComponent.debugLogger.info(
                f'Frame Count: {frame_count}, Response time: {self.responseTime.median():.3f} ms, FPS: {fps:.2f}')
            draw_times.append(curr_time)

            for t in draw_times:
                if curr_time - t <= 1:
                    break
                i += 1
            draw_times = draw_times[i:]
            self.draw(frame_count, objects, len(draw_times))

    def draw(self, frame_count, objects, fps):
        # print('Received frame:', frame_count, objects)
        while True:
            count, frame = self.frames.get()
            if count == frame_count:
                break
            self.frames.put((count, frame))
            sleep(.1)
            # print(f'Frame checked: {count}, expecting: {frame_count} ')
        if not self.show_window:
            return
        # resize frame to window height and keep the aspect ratio
        width = frame.shape[1]
        height = frame.shape[0]
        resized_width = int(width * self.window_height / height)
        frame = cv2.resize(frame, (resized_width, self.window_height))
        self.put_labels(frame, objects, fps)
        self.window_frame_queue.put(('ObjectDetection', frame))

    def put_labels(self, frame, objects, fps):
        shape = frame.shape
        base = 640
        font_scale = 0.75 * self.window_height / base
        thickness = round(1 * self.window_height / base + 0.45)
        org = (round(10 * self.window_height / base), round(50 * self.window_height / base))
        for items in objects:
            cls, label, conf, bbox = items['cls'], items['label'], items['conf'], items['bbox']
            x1, y1, x2, y2 = bbox
            x1 = x1 * shape[1] / self.target_height
            y1 = y1 * shape[0] / self.target_height
            x2 = x2 * shape[1] / self.target_height
            y2 = y2 * shape[0] / self.target_height
            # add label and confidence value
            cv2.putText(
                frame,
                f'{label} {conf:.2f}',
                (int(x1), int(y1)),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                thickness)
            # add fps
            cv2.putText(
                frame,
                f'FPS: {fps}',
                org,
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                thickness)
            cv2.rectangle(
                frame,
                (int(x1), int(y1)), (int(x2), int(y2)),
                (255,
                 255,
                 255),
                thickness)
