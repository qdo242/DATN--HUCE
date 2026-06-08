import requests
import sqlite3
import os
from Cryptodome.Cipher import AES
import json
import secrets

NETWORK_KEY = b'key_x_1234567890'
SERVER_URL = "http://127.0.0.1:5000/receive-data"

def simulate_wokwi_cpp_logic(node_id):
    """Mo phong chinh xac AES-128-CBC trong sketch.ino"""
    print(f"--- Dang kiem tra Node: {node_id} ---")

    # 1. Tao data giong ESP32
    data = {
        "id": node_id,
        "t": 25.5,
        "h": 60.0,
        "co2": 420,
        "co": 5.0,
        "nh3": 2.0,
        "lat": 21.0045,
        "lon": 105.8433,
        "seq": 999
    }
    plaintext = json.dumps(data).encode('utf-8')

    # 2. Pad NULL bytes (giong sketch.ino: memset 0)
    padded_len = len(plaintext)
    if padded_len % 16 != 0:
        padded_len = ((padded_len // 16) + 1) * 16
    padded_plaintext = plaintext.ljust(padded_len, b'\0')

    # 3. Ma hoa AES-128-CBC
    iv = secrets.token_bytes(16)
    cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(padded_plaintext)

    # 4. Dong goi hex: [IV 16 byte] + [Ciphertext]
    final_payload = (iv + ciphertext).hex()

    # 5. Gui len Server
    try:
        r = requests.post(SERVER_URL, json={"payload": final_payload})
        print(f"Ket qua: {r.status_code} - {r.json()}\n")
        return r.status_code == 200
    except Exception as e:
        print(f"Loi ket noi Server: {e}")
        return False

if __name__ == "__main__":
    print("=== BAT DAU KIEM DINH TU DONG CAU HINH WOKWI-SERVER ===\n")

    success = simulate_wokwi_cpp_logic("Xi_01")

    if success:
        print("=> CHUC MUNG: Cau hinh Wokwi va Server da khop noi hoan hao!")
    else:
        print("=> CANH BAO: Co loi trong viec khop noi cau hinh.")
