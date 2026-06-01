import sqlite3
import os

DB_NAME = 'iot_security.db'

def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE devices (
        device_id TEXT PRIMARY KEY,
        node_key TEXT NOT NULL,
        gateway_key TEXT NOT NULL,
        last_seq INTEGER DEFAULT -1,
        status TEXT DEFAULT 'active',
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
        heart_rate REAL,
        spo2 REAL,
        latitude REAL,
        longitude REAL,
        latency REAL,
        status TEXT,
        error_msg TEXT
    )''')
    
    cursor.execute('''CREATE TABLE attack_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        ip_address TEXT,
        attack_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        details TEXT
    )''')
    
    # DUNG KHOA 16 KY TU TRONG SUOT
    devices_data = [
        ('IOT_NODE_01', '1234567890123456', 'gateway_secret_k', -1, 'active', 21.0045, 105.8433, 'Cam bien 1'),
        ('IOT_NODE_02', '6543210987654321', 'gateway_secret_k', -1, 'active', 21.0065, 105.8453, 'Cam bien 2'),
        ('GW01',        'none_node_key_00', 'gateway_secret_k', -1, 'active', 21.0055, 105.8443, 'Gateway')
    ]
    
    cursor.executemany("INSERT INTO devices VALUES (?,?,?,?,?,?,?,?)", devices_data)
    conn.commit()
    conn.close()
    print("Database REBUILT successfully.")

if __name__ == "__main__":
    init_db()
