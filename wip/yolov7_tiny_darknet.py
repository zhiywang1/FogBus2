import os
import cv2
import darknet


def convert2relative(bbox):
    """
    Converts the bounding box coordinates to be relative to the image size
    """
    x, y, w, h = bbox
    _height, _width, __ = img.shape
    return x / _width, y / _height, w / _width, h / _height


def convert2original(image, bbox):
    """
    Converts the relative bounding box coordinates to original image size
    """
    x, y, w, h = bbox
    _height, _width, __ = image.shape
    return int(x * _width), int(y * _height), int(w * _width), int(h * _height)


def draw_boxes(image, bbox, color=(0, 255, 0)):
    """
    Draws bounding boxes on the image
    """
    x, y, w, h = convert2original(image, bbox)
    top_left = (x - w // 2, y - h // 2)
    bottom_right = (x + w // 2, y + h // 2)
    cv2.rectangle(image, top_left, bottom_right, color, 2)
    return image


if __name__ == "__main__":
    # Set the path to the shared library
    os.environ['DARKNET_PATH'] = './'

    try:
        # Load network and weights
        network, class_names, class_colors = darknet.load_network(
            "cfg/yolov7.cfg",
            "cfg/coco.data",
            "yolov7.weights",
            batch_size=1
        )

        # Load and preprocess image
        img = cv2.imread("data/dog.jpg")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (darknet.network_width(network), darknet.network_height(network)))
        darknet_image = darknet.make_image(darknet.network_width(network), darknet.network_height(network), 3)
        darknet.copy_image_from_bytes(darknet_image, img_resized.tobytes())

        # Perform detection
        detections = darknet.detect_image(network, class_names, darknet_image, thresh=0.25)

        # Draw boxes on the original image
        for label, confidence, bbox in detections:
            bbox = convert2relative(bbox)
            img = draw_boxes(img, bbox, color=(0, 255, 0))

        # Save the result image
        cv2.imwrite("predictions.jpg", img)

        # Cleanup
        darknet.free_image(darknet_image)

    except Exception as e:
        print(f"Error: {e}")
