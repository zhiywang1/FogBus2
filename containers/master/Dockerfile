# Base
FROM python:3.9-slim AS base

FROM base AS pythonlibs

## Python libraries
RUN apt update
RUN apt install -y gcc # for cx-Oracle

RUN python -m pip install --upgrade pip
COPY ./sources/requirements.txt /tmp/requirements.txt
RUN python -m pip install --prefix=/install  -r /tmp/requirements.txt

# Copy files
FROM base AS oslibs
RUN apt update
RUN apt install -y iperf3

FROM base
WORKDIR /workplace
COPY --from=pythonlibs /install /usr/local
COPY --from=oslibs /usr/lib/ /usr/lib/
COPY ./sources/ /workplace

# Hostname
RUN echo "Master" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"
# Run Master
ENTRYPOINT ["python", "-u", "master.py"]
