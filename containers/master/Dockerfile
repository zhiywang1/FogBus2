# Base
FROM python:3.9-alpine3.14 as base

FROM base as builder

## Dependencies
RUN apk add make automake gcc g++ subversion linux-headers
RUN apk add gfortran openblas-dev lapack-dev jpeg-dev zlib-dev ninja
RUN apk add qhull-dev qhull

## Python libraries
RUN python -m pip install --upgrade pip

RUN python -m pip install --prefix=/install pymoo==0.4.2.2
RUN python -m pip install --prefix=/install autograd==1.3
RUN python -m pip install --prefix=/install certifi==2021.5.30
RUN python -m pip install --prefix=/install cma==2.7.0
RUN python -m pip install --prefix=/install cx-Oracle==8.2.1
RUN python -m pip install --prefix=/install cycler==0.10.0
RUN python -m pip install --prefix=/install future==0.18.2
RUN python -m pip install --prefix=/install GPUtil==1.4.0
RUN python -m pip install --prefix=/install idna==3.2
RUN python -m pip install --prefix=/install iperf3==0.1.11
RUN python -m pip install --prefix=/install kiwisolver==1.3.1
RUN python -m pip install --prefix=/install mysql-connector-python==8.0.26
RUN python -m pip install --prefix=/install Pillow==9.0.1
RUN python -m pip install --prefix=/install protobuf==3.17.3
RUN python -m pip install --prefix=/install psutil==5.8.0
RUN python -m pip install --prefix=/install pyparsing==2.4.7
RUN python -m pip install --prefix=/install python-dateutil==2.8.2
RUN python -m pip install --prefix=/install python-dotenv==0.19.0
RUN python -m pip install --prefix=/install pythonping==1.1.0
RUN python -m pip install --prefix=/install requests==2.26.0
RUN python -m pip install --prefix=/install six==1.16.0
RUN python -m pip install --prefix=/install urllib3==1.26.6
RUN python -m pip install --prefix=/install websocket-client==1.1.0
RUN python -m pip install --prefix=/install docker==5.0.0
RUN python -m pip install --prefix=/install numpy==1.22.2
RUN python -m pip install --prefix=/install scipy==1.6.3
RUN python -m pip install --prefix=/install requests==2.26.0
RUN python -m pip install --prefix=/install chardet==4.0.0


# Copy files
FROM base
COPY --from=builder /install /usr/local
COPY --from=builder /usr/lib/ /usr/lib/
COPY ./sources/ /workplace
RUN apk add  iperf3

# Hostname
RUN echo "Master" > /etc/hostname

# Run Master
WORKDIR /workplace
ENTRYPOINT ["python", "-u", "master.py"]
