import json
import secrets
from Cryptodome.Cipher import AES
from app import app, get_db_connection

NETWORK_KEY = b'key_x_1234567890'

def simulate_and_verify(node_id, data):
    print(f"[*] Dang kiem dinh Node: {node_id}...")

    # 1. Chuan bi Plaintext
    plaintext = json.dumps(data).encode('utf-8')

    # 2. Pad NULL bytes (giong memset 0 trong sketch.ino)
    padded_len = len(plaintext)
    if padded_len % 16 != 0:
        padded_len = ((padded_len // 16) + 1) * 16
    padded_plaintext = plaintext.ljust(padded_len, b'\0')

    # 3. Ma hoa AES-128-CBC
    iv = secrets.token_bytes(16)
    cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(padded_plaintext)

    # 4. Dong goi hex payload: [IV 16 byte] + [Ciphertext]
    final_payload = (iv + ciphertext).hex()

    # 5. Gui toi Flask Server (Internal Test)
    with app.test_client() as client:
        response = client.post('/receive-data', json={"payload": final_payload})
        return response.status_code, response.get_json()

if __name__ == "__main__":
    print("=== HE THONG TU KIEM DINH TRUOC KHI BAN GIAO ===\n")

    data_x = {"id":"Xi_01", "t":28.2, "h":60.0, "lat":21.0045, "seq":123}
    status_x, res_x = simulate_and_verify("Xi_01", data_x)
    print(f"Ket qua Node Xi_01: {status_x} - {res_x}\n")

    data_y = {"id":"Y_01", "t":30.5, "h":70.0, "lat":21.0065, "seq":456}
    status_y, res_y = simulate_and_verify("Y_01", data_y)
    print(f"Ket qua Node Y_01: {status_y} - {res_y}\n")

    if status_x == 200 and status_y == 200:
        print("=> CHUAN DOAN: He thong da san sang 100%. Hay mo Wokwi va chay ngay!")
