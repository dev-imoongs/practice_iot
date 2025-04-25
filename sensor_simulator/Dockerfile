FROM python:3.10-slim

WORKDIR /usr/src/iotapp/sensor_simulator

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir logs

CMD ["python", "main.py"]