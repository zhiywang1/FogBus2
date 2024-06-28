FROM python:3.9-slim as base

FROM base as builder
WORKDIR /workplace
RUN apt update
RUN apt install -y gcc build-essential git wget
RUN git clone https://github.com/AlexeyAB/darknet \
    && cd darknet \
    && git checkout d02cc3a81689a1593dc5d0c8ed018d10338bebdd

WORKDIR /workplace/darknet
RUN wget https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.weights
RUN wget https://raw.githubusercontent.com/WongKinYiu/yolov7/main/cfg/training/yolov7.yaml

RUN make -j $(nproc) GPU=0 CUDNN=0 CUDNN_HALF=0 OPENCV=0 LIBSO=1

FROM base
COPY --from=builder /workplace/darknet /workplace/darknet
WORKDIR /workplace/darknet
RUN pip install -U pip
RUN pip install numpy==1.22.2
RUN pip install opencv-python==4.9.0.80
RUN apt update && apt install -y libgl1-mesa-glx libglib2.0-0
COPY yolov7_tiny_darknet.py .

ENTRYPOINT ["python", "yolov7_tiny_darknet.py"]