# Base
FROM python:3.10-slim AS base

FROM base AS pythonlibs
RUN apt update
RUN apt install -y gcc make cmake
RUN apt install -y libgl1-mesa-glx
RUN apt install -y libglib2.0-0 libsm6 libxrender1 libxext6

RUN pip install -U pip
RUN apt install -y build-essential
RUN apt install -y libssl-dev
RUN pip install --prefix=/install opencv-python==4.9.0.80
COPY ./sources/requirements.txt  /tmp/requirements.txt
RUN pip install --prefix=/install -r /tmp/requirements.txt

# Copy files
FROM base AS oslibs
RUN apt update
RUN apt install -y libgl1-mesa-glx
RUN apt install -y libglib2.0-0 libsm6 libxrender1 libxext6

FROM base
WORKDIR /workplace
COPY --from=pythonlibs /install /usr/local
COPY --from=oslibs /usr/lib/ /usr/lib/
COPY ./sources/ /workplace

# Hostname
RUN echo "NaiveFormula3" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"

# Run NaiveFormula3
ENTRYPOINT ["python", "-u", "taskExecutor.py"]
