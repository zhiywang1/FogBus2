# Base
FROM python:3.9-slim as base

RUN apt update
RUN apt install -y gcc make
RUN apt install -y libgl1-mesa-glx
RUN apt install -y libglib2.0-0 libsm6 libxrender1 libxext6

RUN pip install -U pip
COPY ./sources/utils/taskExecutor/tasks/yolov7/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY ./sources/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Hostname
WORKDIR /workplace
COPY ./sources /workplace
RUN echo "ObjectDetectionYolov7" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"

# Run ObjectDetectionYolov7
ENTRYPOINT ["python", "-u", "taskExecutor.py"]
