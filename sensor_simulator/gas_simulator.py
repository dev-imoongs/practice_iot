import os
import random
from datetime import datetime
import csv
from typing import List, Tuple
import paho.mqtt.client as mqtt
import json


class GasSensor:
    def __init__(self, sensor_id: str, gas_type: str, min_val: float, max_val: float):
        self.sensor_id = sensor_id
        self.gas_type = gas_type  # ex: CO2, CH4
        self.min_val = min_val
        self.max_val = max_val

    def generate_value(self) -> float:
        return round(random.uniform(self.min_val, self.max_val), 2)


class GasDetector:
    def __init__(self):
        self.sensors: List[GasSensor] = []

    def add_sensor(self, sensor: GasSensor):
        self.sensors.append(sensor)

    def get_sensor_data(self) -> List[Tuple[str, str, float, bool]]:
        result = []
        for sensor in self.sensors:
            value = sensor.generate_value()
            # 단순한 이상 감지 로직 (100~200 사이면 정상)
            is_normal = 100 < value < 200
            result.append((sensor.sensor_id, sensor.gas_type, value, is_normal))
        return result

class CsvSaver:
    def __init__(self, base_dir='logs'):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.current_hour = None
        self.writer = None
        self.file = None

    def _get_filename(self):
        now = datetime.now()
        return os.path.join(self.base_dir, f"gas_{now.strftime('%Y-%m-%d_%H')}.csv")

    def _check_and_rotate_file(self):
        hour = datetime.now().hour
        if self.current_hour != hour or self.file is None:
            if self.file:
                self.file.close()

            self.current_hour = hour
            filename = self._get_filename()

            file_exists = os.path.exists(filename)

            self.file = open(filename, mode='a', newline='')
            self.writer = csv.writer(self.file)

            if not file_exists:
                self.writer.writerow(["timestamp", "gas_type", "gas_ppm", "is_normal"])

    def save(self, gas_type: str, value: float, is_normal: bool):
        self._check_and_rotate_file()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.writer.writerow([timestamp, gas_type, value, '정상' if is_normal else '이상'])
        print(f"[{timestamp}] {gas_type}: {value} ppm ({'정상' if is_normal else '이상'})")

    def close(self):
        if self.file:
            self.file.close()

class MqttPublisher:
    def __init__(self, broker_host='mqtt-broker', broker_port=1883):
        self.client = mqtt.Client()
        self.client.connect(broker_host, broker_port, 60)
        self.client.loop_start()

    def publish(self, topic: str, payload: dict):
        self.client.publish(topic, json.dumps(payload))