import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(__file__), '..', 'iot_security.db')

def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE devices (
        device_id TEXT PRIMARY KEY,
        network_key TEXT NOT NULL,
        last_seq INTEGER DEFAULT -1,
        latitude REAL,
        longitude REAL,
        description TEXT
    )''')

    cursor.execute('''CREATE TABLE telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        pressure REAL,
        co2 REAL,
        co REAL,
        nh3 REAL,
        heart_rate INTEGER,
        spo2 REAL,
        altitude REAL,
        satellites INTEGER,
        latitude REAL,
        longitude REAL,
        status TEXT,
        FOREIGN KEY (device_id) REFERENCES devices (device_id)
    )''')

    cursor.execute('''CREATE TABLE benchmark (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        decrypt_ms REAL,
        seq_ms REAL,
        log_ms REAL,
        total_ms REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    common_key = "key_x_1234567890"
    devices_data = [
        ('Xi_01', common_key, -1, 21.84470, 104.09700, 'Node cam bien Xi_01 - Mù Cang Chải'),
        ('Xi_02', common_key, -1, 21.84550, 104.09820, 'Node cam bien Xi_02 - Mù Cang Chải'),
        ('Y_01',  common_key, -1, 21.84510, 104.09750, 'Gateway Y_01 - Mù Cang Chải')
    ]

    cursor.executemany(
        "INSERT INTO devices (device_id, network_key, last_seq, latitude, longitude, description) VALUES (?,?,?,?,?,?)",
        devices_data
    )

    conn.commit()
    conn.close()
    print("Da khoi tao database thanh cong.")
    print("3 thiet bi: Xi_01, Xi_02, Y_01")

if __name__ == "__main__":
    init_db()
