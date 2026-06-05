# Database Schema

File: `iot_security.db` (SQLite, auto-created by init_db.py)

## Table: `devices`
```sql
CREATE TABLE devices (
    device_id   TEXT PRIMARY KEY,
    network_key TEXT NOT NULL,
    last_seq    INTEGER DEFAULT -1,
    latitude    REAL,
    longitude   REAL,
    description TEXT
);
```

### Seed Data
| device_id | network_key | last_seq | latitude | longitude | description |
|-----------|-------------|----------|----------|-----------|-------------|
| Xi_01 | key_x_1234567890 | -1 | 21.00355 | 105.84255 | Node cam bien Xi_01 |
| Xi_02 | key_x_1234567890 | -1 | 21.00555 | 105.84455 | Node cam bien Xi_02 |
| Y_GW | key_x_1234567890 | -1 | 21.00455 | 105.84355 | Gateway di dong Y |

## Table: `telemetry`
```sql
CREATE TABLE telemetry (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id   TEXT,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity    REAL,
    co2         REAL,
    co          REAL,
    nh3         REAL,
    latitude    REAL,
    longitude   REAL,
    status      TEXT,
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);
```

## Key Queries
```sql
-- Latest telemetry per device
SELECT t.* FROM telemetry t
JOIN (SELECT device_id, MAX(timestamp) as max_ts FROM telemetry GROUP BY device_id) tm
ON t.device_id = tm.device_id AND t.timestamp = tm.max_ts;

-- Device map positions
SELECT t.device_id, t.latitude, t.longitude, d.description
FROM telemetry t
JOIN devices d ON t.device_id = d.device_id
GROUP BY t.device_id HAVING MAX(t.timestamp);

-- Security events
SELECT * FROM telemetry WHERE status != 'An toan' ORDER BY timestamp DESC;
```
