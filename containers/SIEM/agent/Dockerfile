# Base
FROM python:3.10-slim AS base

WORKDIR /workplace
COPY ./sources/ /workplace

RUN pip install --upgrade pip
RUN pip install \
    --no-cache-dir \
    -r requirements.txt

COPY ./sources /workplace

# Hostname
RUN echo "SIEM-Agent" > /etc/hostname
# Run SIEM Agent
ENTRYPOINT ["python", "-u", "run.py"]
