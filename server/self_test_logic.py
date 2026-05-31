import os
import sqlite3
import json
import secrets
from Cryptodome.Cipher import AES
from Cryptodome.Hash import HMAC, SHA256
from app import app, get_db_connection

def test_full_system_logic():
    print("=== BAT DAU KIEM DINH LOGIC HE THONG WOKWI -> SERVER ===\n")
    
    # 1. Chuan bi thong tin (Khop voi sketch.ino va init_db.py)
    node_id = "NODE_X_HEALTH"
    node_key = "key_x_1234567890" # 16 bytes
    gw_key = "gw_secret_000001"
    
    # 2. Mo phong ESP32 mbedtls: Tao Plaintext JSON
    data = {
        "id": node_id,
        "temp": 28.5,
        "bpm": 75,
        "lat": 21.0045,
        "lon": 105.8433,
        "seq": 50
    }
    plaintext = json.dumps(data).encode('utf-8')
    
    # 3. Mo phong ESP32 mbedtls: AES-128-GCM
    nonce = secrets.token_bytes(12)
    cipher = AES.new(node_key.encode('utf-8'), AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    # 4. Mo phong Gateway Layer: [GW_ID(4)] + [Nonce(12)] + [Cipher] + [Tag(16)]
    packet = b"GW01" + nonce + ciphertext + tag
    
    # 5. Mo phong Gateway Layer: HMAC-SHA256
    h = HMAC.new(gw_key.encode('utf-8'), digestmod=SHA256)
    h.update(packet)
    hmac_sig = h.digest()
    
    # 6. Gói tin cuoi cung dang Hex (Cach ESP32 gui len)
    final_hex_payload = (packet + hmac_sig).hex()
    print(f"[ESP32] Da tao goi tin ma hoa (Hex): {final_hex_payload[:50]}...\n")

    # 7. Dung Flask Test Client de kiem tra Server ma khong can mo port
    with app.test_client() as client:
        print("[Server] Dang tiep nhan va giai ma...")
        response = client.post('/receive-data', json={"payload": final_hex_payload})
        
        print(f"[Server] Ket qua phan hoi: {response.status_code}")
        print(f"[Server] Du lieu tra ve: {response.get_json()}")
        
        if response.status_code == 200:
            print("\n=> KET LUAN: Code Wokwi va Server da khớp nối thành công!")
            # Kiem tra xem du lieu da vao DB chua
            conn = get_db_connection()
            log = conn.execute('SELECT * FROM telemetry WHERE device_id = ? ORDER BY id DESC LIMIT 1', (node_id,)).fetchone()
            conn.close()
            if log:
                print(f"[*] Xac nhan Database da luu: Nhiet do={log['temperature']}, Nhip tim={log['heart_rate']}")
        else:
            print("\n=> KET LUAN: Co loi trong logic giai ma.")

if __name__ == "__main__":
    test_full_system_logic()
