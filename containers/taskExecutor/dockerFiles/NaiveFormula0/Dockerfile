# Base
FROM cloudslab/fogbus2-naive_formula0:1.0


# Hostname
RUN echo "NaiveFormula0" > /etc/hostname
WORKDIR /workplace

RUN apk update && apk add --no-cache openssl
RUN openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key \
               -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"
COPY ./sources /workplace

# Run NaiveFormula0
ENTRYPOINT ["python", "taskExecutor.py"]
