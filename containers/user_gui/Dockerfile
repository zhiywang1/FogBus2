# Base
FROM python:3.9-alpine3.19 as base

FROM base as builder
WORKDIR /workplace
RUN apk update
RUN apk add --no-cache \
    gcc build-base linux-headers
COPY ./sources/requirements.txt /workplace/requirements.txt
RUN pip install --no-cache-dir -r  requirements.txt

FROM base
COPY  --from=builder /usr/local/lib/python3.9/ /usr/local/lib/python3.9/

WORKDIR /workplace
COPY ./sources /workplace
RUN apk update && apk add --no-cache openssl

# Hostname
RUN echo "User" > /etc/hostname
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"

# Run User
ENTRYPOINT ["python", "user_gui.py"]
