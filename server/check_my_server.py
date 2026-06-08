import requests
import json
import secrets
from Cryptodome.Cipher import AES

# THONG TIN KHOP TUYET DOI
NODE_ID = "IOT_NODE_01"
# KHOA DUNG CHUNG TOAN MANG (16 byte = "key_x_1234567890")
NETWORK_KEY = b'key_x_1234567890'
URL = "http://127.0.0.1:5000/receive-data"

def run_test():
    print(f"[*] Dang kiem tra ket noi toi Server tai {URL}...")
    
    # 1. Tao du lieu cam bien
    data = {
        "id": NODE_ID,
        "t": 26.5,
        "lat": 21.0045,
        "lon": 105.8433,
        "seq": 500
    }
    plaintext = json.dumps(data).encode('utf-8')
    
    # Pad plaintext voi ky tu NULL de chieu dai chia het cho 16
    padded_len = len(plaintext)
    if padded_len % 16 != 0:
        padded_len = ((padded_len // 16) + 1) * 16
    padded_plaintext = plaintext.ljust(padded_len, b'\0')

    # 2. Ma hoa AES-128-CBC
    iv = secrets.token_bytes(16)
    cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(padded_plaintext)
    
    # 3. Dong goi: [16 byte IV] + [Ciphertext]
    packet = iv + ciphertext
    final_payload = packet.hex()

    # 4. Gui du lieu
    try:
        r = requests.post(URL, json={"payload": final_payload}, timeout=5)
        if r.status_code == 200:
            print("\n=> KET QUA: THANH CONG! Server da giai ma duoc du lieu.")
            print(f"Phan hoi tu Server: {r.json()}")
        else:
            print(f"\n=> KET QUA: THAT BAI (Code {r.status_code})")
            print(f"Ly do: {r.json().get('reason', 'Unknown error')}")
    except Exception as e:
        print(f"\n=> KET QUA: KHONG THE KET NOI TOI SERVER. ({e})")

if __name__ == "__main__":
    run_test()
