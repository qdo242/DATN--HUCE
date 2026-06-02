import os
import sqlite3
from flask import Flask, request, jsonify
from Cryptodome.Cipher import AES
import json

app = Flask(__name__)
DB_NAME = os.path.join(os.path.dirname(__file__), '..', 'iot_security.db')

NETWORK_KEY = b'key_x_1234567890'

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

def log_telemetry(data, status):
    conn = get_db_connection()
    device_id = data.get('id', 'UNKNOWN')

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
            (device_id, temperature, humidity, co2, co, nh3, latitude, longitude, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        device_id,
        data.get('t'),
        data.get('h'),
        data.get('co2'),
        data.get('co'),
        data.get('nh3'),
        lat, lon, status
    ))
    conn.commit()
    conn.close()

@app.route('/receive-data', methods=['POST'])
def receive_data():
    json_input = request.get_json()
    if not json_input or 'payload' not in json_input:
        return jsonify({"status": "error", "message": "Missing payload"}), 400

    try:
        raw_data = bytes.fromhex(json_input['payload'])
        data, error = verify_and_decrypt(raw_data)

        if error:
            print(f"[!] Loi giai ma: {error}")
            return jsonify({"status": "error", "reason": error}), 403

        log_telemetry(data, "An toan")
        print(f"[+] Da giai ma tu {data.get('id')}: t={data.get('t')} h={data.get('h')} lat={data.get('lat')}")
        return jsonify({"status": "success", "device": data.get('id')}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    print("=== SERVER IOT XI->Y->SERVER DANG CHAY ===")
    app.run(host='0.0.0.0', port=5000)
