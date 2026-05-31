import os
import sqlite3
import time
from flask import Flask, request, jsonify
from Cryptodome.Cipher import AES
from Cryptodome.Hash import HMAC, SHA256
import json
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DB_NAME = 'iot_security.db'

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
    
    if len(raw_data) < 4 + 12 + 16 + 32:
        return None, "Packet too short", None, 0
        
    gateway_id = raw_data[:4].decode('utf-8', errors='ignore')
    hmac_received = raw_data[-32:]
    data_to_verify = raw_data[:-32]
    encrypted_payload = raw_data[4:-32]

    conn = get_db_connection()
    # 1. Kiem tra tinh trang Gateway (Khop voi ID 'GW01' tu Wokwi)
    gateway = conn.execute('SELECT * FROM devices WHERE device_id = "GATEWAY_01"').fetchone()
    if not gateway:
        conn.close()
        return None, "Gateway not registered", None, 0

    # 2. Xac thuc HMAC Gateway
    h = HMAC.new(gateway['gateway_key'].encode('utf-8'), digestmod=SHA256)
    h.update(data_to_verify)
    try:
        h.verify(hmac_received)
    except ValueError:
        log_attack(gateway['device_id'], client_ip, "HMAC_MISMATCH", "Invalid Gateway Signature")
        conn.close()
        return None, "HMAC Verification Failed", gateway['device_id'], 0

    # 3. Giai ma AES-GCM (Tam giai ma phan dau de lay ID Node)
    nonce = encrypted_payload[:12]
    tag = encrypted_payload[-16:]
    ciphertext = encrypted_payload[12:-16]

    # Trong kien truc chuyen nghiep, Server se thu tung khoa Node hoac Node ID duoc gui kem ben ngoai.
    # O day, chung ta se tim Node active trong DB de lay khoa.
    nodes = conn.execute('SELECT * FROM devices WHERE device_id LIKE "NODE%" AND status = "active"').fetchall()
    
    decrypted_data = None
    node_id_found = None

    for node in nodes:
        try:
            cipher = AES.new(node['node_key'].encode('utf-8'), AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            decrypted_data = json.loads(plaintext.decode('utf-8'))
            node_id_found = node['device_id']
            
            # Kiem tra Replay
            if decrypted_data['seq'] <= node['last_seq']:
                log_attack(node_id_found, client_ip, "REPLAY_ATTACK", f"Seq {decrypted_data['seq']} is old")
                conn.close()
                return None, "Replay Attack Detected", node_id_found, 0
            
            # Cap nhat DB
            conn.execute('UPDATE devices SET last_seq = ? WHERE device_id = ?', (decrypted_data['seq'], node_id_found))
            conn.commit()
            break
        except:
            continue # Thu khoa tiep theo

    conn.close()
    if not decrypted_data:
        return None, "Decryption Failed (No matching key or corrupted)", "UNKNOWN", 0

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
    try:
        raw_data = bytes.fromhex(json_input['payload'])
        data, error, dev_id, latency = verify_and_decrypt(raw_data, request.remote_addr)
        if error:
            log_telemetry(dev_id, {}, "Security Alert", latency, error)
            return jsonify({"status": "error", "reason": error}), 403
        
        log_telemetry(dev_id, data, "An toan", latency)
        return jsonify({"status": "success", "device": dev_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
