import os
import sqlite3
import json
import secrets
from Cryptodome.Cipher import AES
from app import app, get_db_connection

NETWORK_KEY = b'key_x_1234567890'

def test_full_system_logic():
    print("=== BAT DAU KIEM DINH LOGIC HE THONG WOKWI -> SERVER ===\n")

    node_id = "Xi_01"

    # 1. Tao Plaintext JSON (giong sketch.ino)
    data = {
        "id": node_id,
        "t": 28.5,
        "h": 60.0,
        "p": 1005.0,
        "hr": 75,
        "spo2": 97,
        "co2": 420,
        "co": 5.0,
        "nh3": 2.0,
        "lat": 21.0045,
        "lon": 105.8433,
        "alt": 10,
        "sats": 8,
        "gw": "Y_01",
        "seq": 50
    }
    plaintext = json.dumps(data).encode('utf-8')

    # 2. AES-128-CBC (giong sketch.ino)
    padded_len = len(plaintext)
    if padded_len % 16 != 0:
        padded_len = ((padded_len // 16) + 1) * 16
    padded_plaintext = plaintext.ljust(padded_len, b'\0')

    iv = secrets.token_bytes(16)
    cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(padded_plaintext)

    # 3. Dong goi: [16 byte IV] + [Ciphertext] -> hex
    final_hex_payload = (iv + ciphertext).hex()
    print(f"[Xi] Da tao goi tin ma hoa (Hex): {final_hex_payload[:50]}...\n")

    # 4. Dung Flask Test Client de kiem tra Server
    with app.test_client() as client:
        print("[Server] Dang tiep nhan va giai ma...")
        response = client.post('/receive-data', json={"payload": final_hex_payload})

        print(f"[Server] Ket qua phan hoi: {response.status_code}")
        print(f"[Server] Du lieu tra ve: {response.get_json()}")

        if response.status_code == 200:
            print("\n=> KET LUAN: Code Wokwi va Server da khop noi thanh cong!")
            conn = get_db_connection()
            log = conn.execute('SELECT * FROM telemetry WHERE device_id = ? ORDER BY id DESC LIMIT 1', (node_id,)).fetchone()
            conn.close()
            if log:
                print(f"[*] Xac nhan Database da luu: Nhiet do={log['temperature']}, Nhip tim={log['heart_rate']}")
        else:
            print("\n=> KET LUAN: Co loi trong logic giai ma.")

if __name__ == "__main__":
    test_full_system_logic()
