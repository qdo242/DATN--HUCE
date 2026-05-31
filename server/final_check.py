import json
import secrets
from Cryptodome.Cipher import AES
from Cryptodome.Hash import HMAC, SHA256
from app import app, get_db_connection

def simulate_and_verify(node_id, node_key, gw_key, data):
    print(f"[*] Dang kiem dinh Node: {node_id}...")
    
    # 1. Chuan bi Plaintext
    plaintext = json.dumps(data).encode('utf-8')
    
    # 2. Ma hoa AES-128-GCM (Giong mbedtls trong sketch.ino)
    nonce = secrets.token_bytes(12)
    cipher = AES.new(node_key.encode('utf-8'), AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    # 3. Gateway Layer (GW01 + Nonce + Cipher + Tag)
    packet = b"GW01" + nonce + ciphertext + tag
    
    # 4. HMAC-SHA256
    h = HMAC.new(gw_key.encode('utf-8'), digestmod=SHA256)
    h.update(packet)
    hmac_sig = h.digest()
    
    # 5. Hex Payload
    final_payload = (packet + hmac_sig).hex()

    # 6. Gui toi Flask Server (Internal Test)
    with app.test_client() as client:
        response = client.post('/receive-data', json={"payload": final_payload})
        return response.status_code, response.get_json()

if __name__ == "__main__":
    print("=== HE THONG TU KIEM DINH TRUOC KHI BAN GIAO ===\n")
    
    # Test Node X (Y te)
    data_x = {"id":"NODE_X_HEALTH", "temp":28.2, "bpm":78, "lat":21.0045, "seq":123}
    status_x, res_x = simulate_and_verify("NODE_X_HEALTH", "key_x_1234567890", "gw_secret_000001", data_x)
    print(f"Ket qua Node X: {status_x} - {res_x}\n")
    
    # Test Node Y (Moi truong)
    data_y = {"id":"NODE_Y_ENV", "temp":30.5, "press":1012.5, "lat":21.0065, "seq":456}
    status_y, res_y = simulate_and_verify("NODE_Y_ENV", "key_y_0987654321", "gw_secret_000001", data_y)
    print(f"Ket qua Node Y: {status_y} - {res_y}\n")
    
    if status_x == 200 and status_y == 200:
        print("=> CHUAN DOAN: He thong da san sang 100%. Ban hay mo Wokwi va chay ngay!")
