# Base
FROM python:3.9-alpine3.14 as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

## Dependencies
RUN apk add --no-cache \
    make automake gcc g++ subversion \
    linux-headers

RUN apk add --no-cache \
    gfortran openblas-dev lapack-dev \
    jpeg-dev zlib-dev

## Python libraries
RUN python -m pip install --no-cache-dir --upgrade pip
COPY ./sources/requirements.txt /install/requirements.txt
RUN apk add --no-cache \
    ninja

RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir autograd==1.3
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir certifi==2021.5.30
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir charset-normalizer==2.0.4
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir cma==2.7.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir cx-Oracle==8.2.1
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir cycler==0.10.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir docker==5.0.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir future==0.18.2
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir GPUtil==1.4.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir idna==3.2
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir iperf3==0.1.11
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir kiwisolver==1.3.1
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir mysql-connector-python==8.0.26
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir numpy==1.22.2
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir Pillow==9.0.1
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir protobuf==3.17.3
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir psutil==5.8.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir pymoo==0.4.2.2
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir pyparsing==2.4.7
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir python-dateutil==2.8.2
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir python-dotenv==0.19.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir pythonping==1.1.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir requests==2.26.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir scipy==1.6.3
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir six==1.16.0
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir urllib3==1.26.6
RUN python -m pip install \
    --prefix=/install \
    --no-cache-dir websocket-client==1.1.0
RUN apk add --no-cache \
    qhull-dev qhull

# Copy files
FROM base
COPY --from=builder /install /usr/local
COPY --from=builder /usr/lib/ /usr/lib/
COPY ./sources/ /workplace
RUN apk add --no-cache iperf3

# Hostname
RUN echo "Master" > /etc/hostname

# Run Master
WORKDIR /workplace
ENTRYPOINT ["python", "-u", "master.py"]
