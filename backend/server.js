// backend/server.js
const express = require("express");
const cors = require("cors");
const mqtt = require("mqtt");
const { Pool } = require("pg");

// === PostgreSQL 설정 ===
const db = new Pool({
  user: "mygasuser",
  host: "db",
  database: "gas_sensor",
  password: "mygaspassword",
  port: 5432,
});

// === MQTT 클라이언트 설정 ===
const mqttClient = mqtt.connect("mqtt://mqtt-broker:1883");

mqttClient.on("connect", () => {
  console.log("[MQTT] Connected");
  mqttClient.subscribe("sensors/gas", (err) => {
    if (err) console.error("[MQTT] Subscribe Error:", err);
    else console.log("[MQTT] Subscribed to sensors/gas");
  });
});

mqttClient.on("message", async (topic, message) => {
  try {
    const data = JSON.parse(message.toString());
    const { sensor_id, gas_type, value } = data;

    // DB에 INSERT
    await db.query(
      `INSERT INTO sensor_readings (sensor_id, gas_type, value)
       VALUES ($1, $2, $3)`,
      [sensor_id, gas_type, value]
    );

    console.log(`[DB] 저장됨: ${sensor_id} | ${gas_type} | ${value} ppm`);
  } catch (err) {
    console.error("[MQTT] 메시지 처리 실패:", err.message);
  }
});

// === Express 서버 ===
const app = express();
app.use(cors());
app.use(express.json());

// (예: 최근 센서 데이터 조회 API)
app.get("/api/recent", async (req, res) => {
  try {
    const setLimit = parseInt(req.query.value, 10) || 10;

    const result = await db.query(
      `
      SELECT * FROM sensor_readings
      ORDER BY measured_at DESC
      LIMIT $1
    `,
      [setLimit]
    );

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: "DB 오류" });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Express server running on port ${PORT}`);
});
