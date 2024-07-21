# Base
FROM python:3.10-slim AS base

FROM base AS pythonlibs
RUN pip install -U pip
COPY ./sources/requirements.txt  /tmp/requirements.txt
RUN pip install --prefix=/install -r /tmp/requirements.txt

# Copy files
FROM base
WORKDIR /workplace
COPY --from=pythonlibs /install /usr/local
COPY ./sources/ /workplace

# Hostname
RUN echo "TrafficLightStatus" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"

# Run NaiveFormula3
ENTRYPOINT ["python", "-u", "taskExecutor.py"]
