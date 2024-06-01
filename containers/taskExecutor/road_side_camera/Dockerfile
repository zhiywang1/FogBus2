# Base
FROM ubuntu:jammy-20240427 as base

FROM base as python-builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install -y \
      software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.9 python3-pip
RUN ln -s /usr/bin/python3.9 /usr/bin/python
RUN sed 's|#!/usr/bin/python3|#!/usr/bin/python3.9|' /usr/bin/pip > /usr/bin/pip3 \
    && cp /usr/bin/pip3 /usr/bin/pip
RUN apt install -y python3.9-distutils
RUN apt install -y libgl1

#FROM python as builder
WORKDIR /yolov10
RUN apt install -y git
RUN git init \
      && git remote add origin https://github.com/THU-MIG/yolov10.git \
      && git fetch --depth 1 origin dadcda9c703cc3fbfd5ed6e505a2257738876ee2 \
      && git checkout FETCH_HEAD
RUN pip install --no-cache-dir -r requirements.txt
RUN mv /yolov10 /workplace

WORKDIR /workplace
RUN apt install -y wget
RUN wget https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10s.pt

COPY ./sources /workplace
RUN pip install --no-cache-dir -r requirements.txt
RUN apt clean && apt autoremove && apt autoclean

# Hostname
RUN echo "RoadsideCameraObjectDetection" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"

# Run NaiveFormula0
ENTRYPOINT ["python", "road_side_camera.py"]
