# Base
FROM python:3.9-slim AS base

FROM base AS pythonlibs

## Python libraries
#RUN apt update
#RUN apt install -y gcc

RUN python -m pip install --upgrade pip
COPY ./sources/requirements.txt /tmp/requirements.txt
RUN python -m pip install --prefix=/install  -r /tmp/requirements.txt

#RUN apt-get update && \
#    apt-get install -y make automake gcc g++ subversion linux-headers-generic \
#                       gfortran libopenblas-dev liblapack-dev libjpeg-dev zlib1g-dev ninja-build \
#                       libqhull-dev qhull-bin libffi-dev iperf3

# Copy files
FROM base as oslibs
RUN apt update
RUN apt install -y iperf3

FROM base
WORKDIR /workplace
COPY --from=pythonlibs /install /usr/local
COPY --from=oslibs /usr/lib/ /usr/lib/
COPY ./sources/ /workplace

# Hostname
RUN echo "Actor" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"

# Run Actor
ENTRYPOINT ["python", "-u", "actor.py"]
