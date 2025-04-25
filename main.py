from gas_simulator import GasDetector, GasSensor, CsvSaver
import time
import os

def run_simulation(duration: int = 10, interval: float = 1.0):
    # 구성

    
    saver = CsvSaver(path)

    # 시뮬레이션 루프
    start_time = time.time()
    while time.time() - start_time < duration:
        sensor_data = detector.get_sensor_data()
        for gas_type, value, is_normal in sensor_data:
            saver.save(gas_type, value, is_normal)
        time.sleep(interval)


if __name__ == "__main__":
    path = os.path.join(os.getcwd(),"logs")
    co2_sensor = GasSensor("CO2", 50.0, 400.0)
    ch4_sensor = GasSensor("CH4", 30.0, 250.0)
    detector = GasDetector()
    detector.add_sensor(co2_sensor)
    detector.add_sensor(ch4_sensor)
    run_simulation(duration=30, interval=1.0)  # 30초 동안 1초 간격으로 생성

