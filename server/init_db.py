import sqlite3
import os

DB_NAME = 'iot_security.db'

def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Bang quan ly thiet bi
    cursor.execute('''
    CREATE TABLE devices (
        device_id TEXT PRIMARY KEY,
        node_key TEXT NOT NULL,
        gateway_key TEXT NOT NULL,
        last_seq INTEGER DEFAULT -1,
        status TEXT DEFAULT 'active',
        latitude REAL,
        longitude REAL,
        description TEXT
    )
    ''')
    
    # Bang du lieu Telemetry (Them nhieu truong cho cac loai cam bien khac nhau)
    cursor.execute('''
    CREATE TABLE telemetry (
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
        error_msg TEXT,
        FOREIGN KEY (device_id) REFERENCES devices (device_id)
    )
    ''')
    
    # Bang nhat ky tan cong
    cursor.execute('''
    CREATE TABLE attack_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        ip_address TEXT,
        attack_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        details TEXT
    )
    ''')
    
    # KHOI TAO 3 THIET BI (Khoa phai dung dung 16 ky tu)
    devices_data = [
        ('NODE_X_HEALTH', 'key_x_1234567890', 'gw_secret_000001', -1, 'active', 21.0045, 105.8433, 'Thiet bi deo theo doi suc khoe'),
        ('NODE_Y_ENV',    'key_y_0987654321', 'gw_secret_000001', -1, 'active', 21.0065, 105.8453, 'Tram quan trac moi truong'),
        ('GATEWAY_01',    'none',             'gw_secret_000001', -1, 'active', 21.0055, 105.8443, 'Tram trung chuyen du lieu')
    ]
    
    cursor.executemany("INSERT INTO devices VALUES (?,?,?,?,?,?,?,?)", devices_data)
    
    conn.commit()
    conn.close()
    print(f"Khoi tao he thong 3 thiet bi vao Database {DB_NAME} thanh cong.")

if __name__ == "__main__":
    init_db()
