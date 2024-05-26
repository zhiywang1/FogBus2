FROM python:3.9-alpine3.14
WORKDIR /workplace

RUN python -m pip install --upgrade pip
COPY ./sources/ /workplace

RUN apk add gcc python3-dev musl-dev linux-headers iptables
RUN python -m pip install \
    --no-cache-dir \
    -r requirements.txt



# Hostname
RUN echo "SIME-Agent" > /etc/hostname

#ENTRYPOINT ["python","-u", "run.py"]
