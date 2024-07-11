import torch
import cv2
# from time import time
from yolov7_utils.torch_utils import select_device, TracedModel
from yolov7_utils.general import non_max_suppression
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


class Yolov7:
    def __init__(self, path=None):
        if path is None:
            import os
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yolov7-tiny.pt')
        self.weights_path = path
        self.device = select_device('cpu')
        self.model = self.load()
        self.names = self.model.names
        self.img_size = 480

        self.model = TracedModel(self.model, self.device, self.img_size)
        self.threshold = 0.20

    def load(self):
        ckpt = torch.load(self.weights_path, map_location=self.device)
        return ckpt['ema' if ckpt.get('ema') else 'model'].float().fuse().eval()

    def detect(self, image_rgb_resized):
        img = torch.from_numpy(image_rgb_resized).permute(2, 0, 1).to(self.device)
        img = img.float()
        img /= 255.0
        img = img.unsqueeze(0)
        # t1 = time()
        with torch.no_grad():
            pred = self.model(img)[0]
        # t2 = time()

        # d = (t2 - t1) * 1000
        # print(f'Done. ({d:.3f}ms)')
        pred = non_max_suppression(pred, self.threshold)

        objects = []
        for det in pred:
            if det is not None and len(det):
                for *xyxy, conf, cls in reversed(det):
                    objects.append({
                        'cls': int(cls),
                        'label': self.names[int(cls)],
                        'conf': float(conf),
                        'bbox': [float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])]
                    })
        return objects


if __name__ == '__main__':
    import os

    script_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_path, 'parrot.jpg')
    parrot_img = cv2.imread(img_path)
    parrot_img_rgb = cv2.cvtColor(parrot_img, cv2.COLOR_BGR2RGB)
    yolov7 = Yolov7()
    parrot_img_rgb_resized = cv2.resize(parrot_img_rgb, (480, 480))

    res = yolov7.detect(parrot_img_rgb_resized)
    from pprint import pprint

    pprint(res)
