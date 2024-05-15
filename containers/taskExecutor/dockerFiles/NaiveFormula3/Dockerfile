# Base
FROM cloudslab/fogbus2-naive_formula3:1.0
COPY ./sources /workplace

# Hostname
RUN echo "NaiveFormula3" > /etc/hostname

# Run NaiveFormula3
WORKDIR /workplace
ENTRYPOINT ["python", "taskExecutor.py"]
