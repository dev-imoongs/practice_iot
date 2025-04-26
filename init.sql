CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    gas_type VARCHAR(50) NOT NULL,
    value REAL NOT NULL,
    is_normal BOOLEAN NOT NULL,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sensor_time ON sensor_readings (sensor_id, measured_at DESC);
