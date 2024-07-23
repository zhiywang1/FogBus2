# Base
FROM python:3.9-slim AS base

WORKDIR /workplace

RUN pip install -U pip
COPY ./sources/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./sources /workplace
# Hostname
RUN echo "SIEM-Agent" > /etc/hostname
# Run SIEM Agent
ENTRYPOINT ["python", "-u", "run.py"]
