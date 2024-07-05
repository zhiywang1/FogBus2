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
        self.window_height = 640
        self.window_frame_queue: Queue[Tuple[str, Any]] = Queue(1)

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
            return ret
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb_resized = cv2.resize(frame_rgb, (self.target_height, self.target_height))
        input_data = {
            'image': frame_rgb_resized,
            'frame_count': frame_count,
        }
        self.sent_times[frame_count % self.fps] = time()
        self.frames.put((frame_count, frame))
        self.dataToSubmit.put(input_data)
        print('Sent frame:', frame_count)
        return True

    def _frame_sender(self):
        self.basicComponent.debugLogger.info('Frame sender started')
        if self.video_path is None:
            self.sensor = cv2.VideoCapture(0)
        else:
            self.sensor = cv2.VideoCapture(self.video_path)
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
        while True:
            result = self.resultForActuator.get()
            frame_count = result['frame_count']
            self.responseTime.update((time() - self.sent_times[frame_count % self.fps]) * 1000)
            self.basicComponent.debugLogger.info('Response time: %.3f ms', self.responseTime.median())
            objects = result['objects']
            i, curr_time = 0, time()
            draw_times.append(curr_time)

            for t in draw_times:
                if curr_time - t <= 1:
                    break
                i += 1
            draw_times = draw_times[i:]
            self.draw(frame_count, objects, len(draw_times))

    def draw(self, frame_count, objects, fps):
        print('Received frame:', frame_count, objects)
        while True:
            count, frame = self.frames.get()
            if count == frame_count:
                break
            self.frames.put((count, frame))

        original_shape = frame.shape

        for items in objects:
            cls, label, conf, bbox = items['cls'], items['label'], items['conf'], items['bbox']
            x1, y1, x2, y2 = bbox
            x1 = x1 * original_shape[1] / self.target_height
            y1 = y1 * original_shape[0] / self.target_height
            x2 = x2 * original_shape[1] / self.target_height
            y2 = y2 * original_shape[0] / self.target_height
            # add label and confidence value
            cv2.putText(
                frame,
                f'{label} {conf:.2f}',
                (int(x1), int(y1)),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (255, 255, 255),
                4)
            # add fps
            cv2.putText(
                frame,
                f'FPS: {fps}',
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (255, 255, 255),
                4)
            cv2.rectangle(
                frame,
                (int(x1), int(y1)), (int(x2), int(y2)),
                (255,
                 255,
                 255),
                4)

        self.window_frame_queue.put(('ObjectDetection', frame))
