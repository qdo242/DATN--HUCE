import requests
import json
import secrets
import time
from Cryptodome.Cipher import AES

NETWORK_KEY = b'key_x_1234567890'
SERVER_URL = "http://127.0.0.1:5000/receive-data"

def simulate_xi_to_y_to_server(device_id, start_lat, start_lon):
    print(f"\n{'='*50}")
    print(f"=== KHOI DONG THIET BI {device_id} ===")
    print(f"{'='*50}")

    curr_lat, curr_lon = start_lat, start_lon

    for seq in range(1, 6):
        print(f"\n--- Chu ky {seq} ---")

        # ---- GIAI DOAN 1: BEACON/ACK ----
        print(f"[{device_id}] Phat Beacon LoRa...")
        time.sleep(1)
        print(f"[GATEWAY Y] Nhan Beacon tu {device_id}, gui ACK")
        print(f"[{device_id}] Nhan ACK, bat dau truyen tin.")

        # ---- GIAI DOAN 2: DOC CAM BIEN ----
        temp = round(28.0 + (secrets.randbelow(100) / 10.0), 1)
        humi = round(60.0 + (secrets.randbelow(100) / 10.0), 1)
        co = round(5.0 + (secrets.randbelow(30) / 10.0), 1)
        co2 = 400 + secrets.randbelow(50)
        nh3 = round(2.0 + (secrets.randbelow(20) / 10.0), 1)

        curr_lat += 0.0001
        curr_lon += 0.0001

        data = {
            "id": device_id,
            "t": temp,
            "h": humi,
            "co": co,
            "co2": co2,
            "nh3": nh3,
            "lat": round(curr_lat, 5),
            "lon": round(curr_lon, 5),
            "seq": seq
        }
        print(f"[{device_id}] Du lieu: {data}")

        # ---- GIAI DOAN 3: MA HOA AES-128-CBC ----
        plaintext = json.dumps(data).encode('utf-8')
        padded_len = len(plaintext)
        if padded_len % 16 != 0:
            padded_len = ((padded_len // 16) + 1) * 16
        padded_plaintext = plaintext.ljust(padded_len, b'\0')

        iv = secrets.token_bytes(16)
        cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
        ciphertext = cipher.encrypt(padded_plaintext)

        # ---- GIAI DOAN 4: GUI QUA LoRa SANG GATEWAY ----
        print(f"[{device_id}] Gui du lieu ma hoa ({len(ciphertext)} bytes) qua LoRa...")
        time.sleep(0.5)
        print(f"[GATEWAY Y] Nhan du lieu ma hoa tu {device_id}")

        # ---- GIAI DOAN 5: GATEWAY CHUYEN TIEP LEN SERVER ----
        payload_hex = (iv + ciphertext).hex()
        print(f"[GATEWAY Y] Chuyen tiep len Server...")

        try:
            r = requests.post(SERVER_URL, json={"payload": payload_hex}, timeout=10)
            print(f"[SERVER] Phan hoi: {r.status_code} - {r.json()}")
            if r.status_code == 200:
                print(f"[GATEWAY Y] Gui ACK cho {device_id}")
        except Exception as e:
            print(f"[!] LOI: Khong ket noi duoc Server! ({e})")

        time.sleep(2)

if __name__ == "__main__":
    print("=== MO PHONG LUONG XI -> Y (GATEWAY) -> SERVER ===\n")
    simulate_xi_to_y_to_server("Xi_01", 21.00355, 105.84255)
    print("\n" + "="*50)
    simulate_xi_to_y_to_server("Xi_02", 21.00555, 105.84455)
    print("\n=== KET THUC ===")
