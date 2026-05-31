import requests
import sqlite3
import os
from Cryptodome.Cipher import AES
from Cryptodome.Hash import HMAC, SHA256
import json
import secrets

SERVER_URL = "http://127.0.0.1:5000/receive-data"

def simulate_wokwi_cpp_logic(node_id, node_key, gw_key):
    """Mo phong chinh xac thuat toan C++ mbedtls trong sketch.ino"""
    print(f"--- Dang kiem tra Node: {node_id} ---")
    
    # 1. Tao data giong ESP32
    data = {
        "id": node_id,
        "temp": 25.5,
        "bpm": 80,
        "lat": 21.0045,
        "seq": 999
    }
    plaintext = json.dumps(data).encode('utf-8')
    
    # 2. Ma hoa AES-128-GCM
    nonce = secrets.token_bytes(12)
    cipher = AES.new(node_key.encode('utf-8'), AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    # 3. Dong goi Gateway Layer (GW01 + Nonce + Cipher + Tag)
    packet = b"GW01" + nonce + ciphertext + tag
    
    # 4. Ky HMAC-SHA256
    h = HMAC.new(gw_key.encode('utf-8'), digestmod=SHA256)
    h.update(packet)
    hmac_sig = h.digest()
    
    # 5. Gui len Server (Hex format)
    final_payload = (packet + hmac_sig).hex()
    
    try:
        r = requests.post(SERVER_URL, json={"payload": final_payload})
        print(f"Ket qua: {r.status_code} - {r.json()}\n")
        return r.status_code == 200
    except Exception as e:
        print(f"Loi ket noi Server: {e}")
        return False

if __name__ == "__main__":
    print("=== BAT DAU KIEM DINH TU DONG CAU HINH WOKWI-SERVER ===\n")
    
    # Kiem tra ca 2 loai Node
    success_x = simulate_wokwi_cpp_logic("NODE_X_HEALTH", "key_x_1234567890", "gw_secret_000001")
    success_y = simulate_wokwi_cpp_logic("NODE_Y_ENV",    "key_y_0987654321", "gw_secret_000001")
    
    if success_x and success_y:
        print("=> CHUC MUNG: Cau hinh Wokwi va Server da khớp nối hoàn hảo!")
    else:
        print("=> CANH BAO: Co loi trong viec khớp nối cau hinh.")
