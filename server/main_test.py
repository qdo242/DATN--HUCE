import requests
import json
import secrets
import sqlite3
import os
from Cryptodome.Cipher import AES

SERVER_URL = "http://127.0.0.1:5000/receive-data"
DB_NAME = os.path.join(os.path.dirname(__file__), '..', 'iot_security.db')
NETWORK_KEY = b'key_x_1234567890'

def make_packet(device_id, temp, humid, seq, lat=21.00355, lon=105.84255):
    data = {
        "id": device_id,
        "t": temp,
        "h": humid,
        "co2": 420,
        "lat": lat,
        "lon": lon,
        "seq": seq
    }
    plaintext = json.dumps(data).encode('utf-8')
    padded_len = len(plaintext)
    if padded_len % 16 != 0:
        padded_len = ((padded_len // 16) + 1) * 16
    padded_plaintext = plaintext.ljust(padded_len, b'\0')

    iv = secrets.token_bytes(16)
    cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(padded_plaintext)

    return iv + ciphertext

def reset_db():
    if os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM telemetry")
        conn.commit()
        conn.close()
        print("[*] Da lam sach du lieu telemetry.\n")

if __name__ == "__main__":
    reset_db()
    print("=== GUI THU DU LIEU LEN SERVER ===\n")

    packet = make_packet("Xi_01", 25.0, 60.0, 1)
    r = requests.post(SERVER_URL, json={"payload": packet.hex()})
    print(f"Xi_01: {r.status_code} - {r.json()}")

    packet2 = make_packet("Xi_02", 30.0, 70.0, 1)
    r2 = requests.post(SERVER_URL, json={"payload": packet2.hex()})
    print(f"Xi_02: {r2.status_code} - {r2.json()}")

    print("\nDa gui xong. Hay mo Dashboard de kiem tra.")
