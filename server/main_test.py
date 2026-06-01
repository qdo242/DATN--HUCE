import requests
import sqlite3
import os
from simulator import simulate_node_to_server

SERVER_URL = "http://127.0.0.1:5000/receive-data"
DB_NAME = 'iot_security.db'

def reset_db_state():
    """Don dep trang thai thiet bi de bat dau bai test moi"""
    if os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        conn.execute("UPDATE devices SET last_seq = -1, status = 'active'")
        conn.execute("DELETE FROM attack_logs")
        conn.execute("DELETE FROM telemetry")
        conn.commit()
        conn.close()
        print("[*] Da thiet lap trang thai he thong sach.\n")

def run_comprehensive_test():
    reset_db_state()
    print("=== BAT DAU KIEM THU AN NINH CHUYEN SAU (AES-CBC) ===\n")

    # 1. Giao dich hop le
    print("[1] Gui ban tin hop le (IOT_NODE_01)...")
    packet = simulate_node_to_server(temp=25.0, humidity=60, seq=1)
    r = requests.post(SERVER_URL, json={"payload": packet.hex()})
    print(f"Phan hoi: {r.status_code} - {r.json()}\n")

    # 2. Tan cong vao IV
    print("[2] Tan cong vao IV (Sua doi vector khoi tao)...")
    tampered_iv = bytearray(packet)
    tampered_iv[5] = tampered_iv[5] ^ 0xFF
    r = requests.post(SERVER_URL, json={"payload": bytes(tampered_iv).hex()})
    print(f"Phan hoi: {r.status_code} - {r.json()}\n")

    # 3. Tan cong vao Ciphertext
    print("[3] Tan cong vao Ciphertext (Sua doi ban ma)...")
    tampered_ct = bytearray(packet)
    tampered_ct[20] = tampered_ct[20] ^ 0xFF
    r = requests.post(SERVER_URL, json={"payload": bytes(tampered_ct).hex()})
    print(f"Phan hoi: {r.status_code} - {r.json()}\n")

    # 4. Tan cong Replay
    print("[4] Tan cong phat lai (Replay Seq 1)...")
    r = requests.post(SERVER_URL, json={"payload": packet.hex()})
    print(f"Phan hoi: {r.status_code} - {r.json()}\n")

if __name__ == "__main__":
    run_comprehensive_test()
