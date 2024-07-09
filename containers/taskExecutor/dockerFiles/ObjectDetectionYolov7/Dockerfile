# Base
FROM python:3.9-slim as base

WORKDIR /workplace
RUN apt update
RUN apt install -y gcc make
RUN apt install -y libgl1-mesa-glx
RUN apt install -y libglib2.0-0 libsm6 libxrender1 libxext6

RUN pip install -U pip
COPY ./sources/utils/taskExecutor/tasks/yolov7/requirements.txt /workplace/utils/taskExecutor/tasks/yolov7/requirements.txt
RUN pip install -r utils/taskExecutor/tasks/yolov7/requirements.txt
COPY ./sources/requirements.txt /workplace/requirements.txt
RUN pip install -r requirements.txt

COPY ./sources /workplace

# Hostname
RUN echo "ObjectDetectionYolov7" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"

RUN pip install memory_profiler
# Run ObjectDetectionYolov7
ENTRYPOINT ["python","-m", "memory_profiler", "taskExecutor.py"]
