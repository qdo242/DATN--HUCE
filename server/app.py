import os
import sqlite3
from flask import Flask, request, jsonify
from Cryptodome.Cipher import AES
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(filename='server_debug.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s')

app = Flask(__name__)
DB_NAME = os.path.join(os.path.dirname(__file__), '..', 'iot_security.db')

NETWORK_KEY = b'key_x_1234567890'
executor = ThreadPoolExecutor(max_workers=4)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def verify_and_decrypt(raw_data):
    if len(raw_data) < 16 + 16:
        return None, "Packet too short"

    iv = raw_data[:16]
    ciphertext = raw_data[16:]

    try:
        cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
        plaintext = cipher.decrypt(ciphertext).rstrip(b'\0')
        data = json.loads(plaintext.decode('utf-8'))
        return data, None
    except Exception as e:
        return None, f"Decryption Failed: {str(e)}"

def check_seq(device_id, seq):
    conn = get_db_connection()
    row = conn.execute('SELECT last_seq FROM devices WHERE device_id = ?', (device_id,)).fetchone()
    if row is None:
        conn.close()
        return False, "Device not found"
    if seq is not None and seq <= row['last_seq']:
        conn.close()
        return False, "Replay attack detected (seq <= last_seq)"
    conn.close()
    return True, None

def update_seq(device_id, seq):
    for attempt in range(3):
        try:
            conn = get_db_connection()
            conn.execute('UPDATE devices SET last_seq = ? WHERE device_id = ?', (seq, device_id))
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if 'locked' in str(e) and attempt < 2:
                time.sleep(0.1)
                continue
            logging.error(f"DB update_seq failed: {e}")
            break

def log_telemetry(data, status):
    device_id = data.get('id', 'UNKNOWN')
    for attempt in range(3):
        try:
            conn = get_db_connection()
            lat, lon = data.get('lat'), data.get('lon')
            if lat is None or lon is None:
                device = conn.execute(
                    'SELECT latitude, longitude FROM devices WHERE device_id = ?',
                    (device_id,)
                ).fetchone()
                if device:
                    lat, lon = device['latitude'], device['longitude']
            conn.execute('''
                INSERT INTO telemetry
                    (device_id, temperature, humidity, pressure,
                     co2, co, nh3,
                     altitude, satellites,
                     latitude, longitude, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_id, data.get('t'), data.get('h'), data.get('p'),
                data.get('co2'), data.get('co'), data.get('nh3'),
                data.get('alt'), data.get('sats'),
                lat, lon, status
            ))
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if 'locked' in str(e) and attempt < 2:
                time.sleep(0.1)
                continue
            logging.error(f"DB write failed: {e}")
            break

def save_benchmark(device_id, decrypt_ms, seq_ms, log_ms, total_ms, status):
    for attempt in range(3):
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO benchmark (device_id, decrypt_ms, seq_ms, log_ms, total_ms, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (device_id, decrypt_ms, seq_ms, log_ms, total_ms, status))
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if 'locked' in str(e) and attempt < 2:
                time.sleep(0.1)
                continue
            break

@app.route('/benchmark', methods=['GET'])
def get_benchmark():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT * FROM benchmark ORDER BY id DESC LIMIT 100
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/receive-data', methods=['POST'])
def receive_data():
    t_start = time.time()
    json_input = request.get_json()
    if not json_input or 'payload' not in json_input:
        return jsonify({"status": "error", "message": "Missing payload"}), 400

    try:
        payload = json_input['payload']
        logging.debug(f"Received payload len={len(payload)} first50={payload[:50]}")
        raw_data = bytes.fromhex(payload)

        t1 = time.time()
        data, error = verify_and_decrypt(raw_data)
        t_decrypt = (time.time() - t1) * 1000

        if error:
            print(f"[!] Loi giai ma: {error}")
            logging.debug(f"Decrypt error: {error}")
            return jsonify({"status": "error", "reason": error}), 403

        t2 = time.time()
        ok, msg = check_seq(data.get('id'), data.get('seq'))
        t_seq = (time.time() - t2) * 1000

        if not ok:
            executor.submit(log_telemetry, data, f"Canh bao: {msg}")
            executor.submit(save_benchmark, data.get('id'), t_decrypt, t_seq, 0, 0, "FAIL")
            print(f"[!] {msg}")
            return jsonify({"status": "error", "reason": msg}), 403

        t3 = time.time()
        if data.get('seq') is not None:
            update_seq(data.get('id'), data.get('seq'))
        executor.submit(log_telemetry, data, "An toan")
        t_log = (time.time() - t3) * 1000

        t_total = (time.time() - t_start) * 1000
        print(f"[+] {data.get('id')}: decrypt={t_decrypt:.1f}ms seq={t_seq:.1f}ms log={t_log:.1f}ms total={t_total:.1f}ms")
        executor.submit(save_benchmark, data.get('id'), t_decrypt, t_seq, t_log, t_total, "OK")

        return jsonify({"status": "success", "device": data.get('id')}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    print("=== SERVER IOT XI->Y->SERVER DANG CHAY ===")
    app.run(host='0.0.0.0', port=5000, threaded=True)
