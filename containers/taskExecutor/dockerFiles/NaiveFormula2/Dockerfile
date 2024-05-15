# Base
FROM cloudslab/fogbus2-naive_formula2:1.0
COPY ./sources /workplace


# Hostname
RUN echo "NaiveFormula2" > /etc/hostname

# Run NaiveFormula2
WORKDIR /workplace
ENTRYPOINT ["python", "taskExecutor.py"]
