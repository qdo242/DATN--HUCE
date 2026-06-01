import os
import sqlite3
import time
from flask import Flask, request, jsonify
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
import json

app = Flask(__name__)
DB_NAME = 'iot_security.db'

# KHOA DUNG CHUNG TOAN MANG (16 byte cho AES-128)
NETWORK_KEY = bytes([0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
                     0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C])

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def log_attack(device_id, ip, attack_type, details):
    conn = get_db_connection()
    conn.execute('INSERT INTO attack_logs (device_id, ip_address, attack_type, details) VALUES (?, ?, ?, ?)', 
                 (device_id, ip, attack_type, details))
    conn.commit()
    conn.close()

def verify_and_decrypt(raw_data, client_ip):
    start_time = time.time()
    
    # 1. Kiem tra do dai toi thieu: [16 byte IV] + [Ciphertext]
    if len(raw_data) < 16 + 16:
        return None, "Packet too short", None, 0
        
    iv = raw_data[:16]
    ciphertext = raw_data[16:]

    # 2. Giai ma AES-128-CBC
    try:
        cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
        # Giai ma va loai bo ky tu NULL padding
        plaintext = cipher.decrypt(ciphertext).rstrip(b'\0')
        decrypted_data = json.loads(plaintext.decode('utf-8'))
        node_id_found = decrypted_data.get('id', 'UNKNOWN')
    except Exception as e:
        log_attack("UNKNOWN", client_ip, "DECRYPTION_FAILED", str(e))
        return None, f"Decryption Failed: {str(e)}", "UNKNOWN", 0

    conn = get_db_connection()
    
    # Kiem tra xem ID trong Payload co hop le khong
    node = conn.execute('SELECT * FROM devices WHERE device_id = ? AND status = "active"', (node_id_found,)).fetchone()
    if not node:
        log_attack(node_id_found, client_ip, "INVALID_NODE", f"ID khong ton tai hoac bi khoa")
        conn.close()
        return None, "Node ID Invalid or Blacklisted", node_id_found, 0

    # Kiem tra Replay
    if decrypted_data.get('seq', 0) <= node['last_seq']:
        log_attack(node_id_found, client_ip, "REPLAY_ATTACK", f"Old Seq: {decrypted_data.get('seq')}")
        conn.close()
        return None, "Replay Attack Detected", node_id_found, 0
    
    # Cap nhat DB
    conn.execute('UPDATE devices SET last_seq = ? WHERE device_id = ?', (decrypted_data.get('seq'), node_id_found))
    conn.commit()
    conn.close()

    latency = time.time() - start_time
    return decrypted_data, None, node_id_found, latency

def log_telemetry(device_id, data, status, latency, error_msg=None):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO telemetry (device_id, temperature, humidity, pressure, heart_rate, spo2, latitude, longitude, latency, status, error_msg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (device_id, 
          data.get('temp'), data.get('humi'), data.get('press'),
          data.get('bpm'), data.get('spo2'), data.get('lat'), data.get('lon'),
          latency, status, error_msg))
    conn.commit()
    conn.close()

@app.route('/receive-data', methods=['POST'])
def receive_data():
    json_input = request.get_json()
    if not json_input or 'payload' not in json_input:
        return jsonify({"status": "error", "message": "Missing payload"}), 400
        
    try:
        raw_data = bytes.fromhex(json_input['payload'])
        data, error, dev_id, latency = verify_and_decrypt(raw_data, request.remote_addr)
        if error:
            log_telemetry(dev_id, {}, "Security Alert", latency, error)
            return jsonify({"status": "error", "reason": error}), 403
        
        log_telemetry(dev_id, data, "An toan", latency)
        print(f"[+] Decrypted from {dev_id}: {data}")
        return jsonify({"status": "success", "device": dev_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    print("=== SERVER SECURE READY ===")
    app.run(host='0.0.0.0', port=5000)
