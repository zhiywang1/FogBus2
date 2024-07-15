# Base
FROM python:3.9-slim AS base

FROM base AS pythonlibs

RUN python -m pip install --upgrade pip
COPY ./sources/requirements.txt /tmp/requirements.txt
RUN python -m pip install --prefix=/install  -r /tmp/requirements.txt


FROM base
WORKDIR /workplace
COPY --from=pythonlibs /install /usr/local
COPY ./sources/ /workplace

# Hostname
RUN echo "RemoteLogger" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"
# Run RemoteLogger
WORKDIR /workplace
ENTRYPOINT ["python", "-u", "remoteLogger.py"]
