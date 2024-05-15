# Base
FROM cloudslab/fogbus2-naive_formula1:1.0
COPY ./sources /workplace

# Hostname
RUN echo "NaiveFormula1" > /etc/hostname

# Run NaiveFormula1
WORKDIR /workplace
ENTRYPOINT ["python", "taskExecutor.py"]
