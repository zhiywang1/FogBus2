# Base
FROM cloudslab/fogbus2-naive_formula0:1.0
COPY ./sources /workplace

# Hostname
RUN echo "NaiveFormula0" > /etc/hostname

# Run NaiveFormula0
WORKDIR /workplace
ENTRYPOINT ["python", "taskExecutor.py"]
