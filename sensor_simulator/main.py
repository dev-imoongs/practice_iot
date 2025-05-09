from gas_simulator import GasDetector, GasSensor, CsvSaver, MqttPublisher
import time
import os

print("▶️ run_simulation() 시작1")

def run_simulation(duration: int = 10, interval: float = 1.0):
    print("▶️ run_simulation() 시작2")
    path = os.path.join(os.getcwd(), "logs")
    saver = CsvSaver(path)
    publisher = MqttPublisher()

    # 시뮬레이션 루프
    start_time = time.time()
    while time.time() - start_time < duration:
        sensor_data = detector.get_sensor_data()
        for sensor_id, gas_type, value, is_normal in sensor_data:
            saver.save(gas_type, value, is_normal)
            payload = {
                "sensor_id": sensor_id,
                "gas_type": gas_type,
                "value": value,
                "is_normal": is_normal
            }
            publisher.publish("sensors/gas", payload)
        time.sleep(interval)


if __name__ == "__main__":
    print("▶️ run_simulation() 시작3")
    co2_sensor = GasSensor("X1001","CO2", 50.0, 270.0)
    ch4_sensor = GasSensor("X1010","CH4", 80.0, 320.0)
    detector = GasDetector()
    detector.add_sensor(co2_sensor)
    detector.add_sensor(ch4_sensor)
    try:
        run_simulation(duration=300, interval=2)
    except Exception as e:
        print(f"Error occurred: {e}")

