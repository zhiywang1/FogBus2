# Base
FROM python:3.10-slim AS base

COPY ./sources/requirements.txt /tmp/requirements.txt
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

WORKDIR /workplace
COPY ./sources/ /workplace
RUN rm .env > /dev/null 2>&1 &

# Hostname
RUN echo "SIME" > /etc/hostname
