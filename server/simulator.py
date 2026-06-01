import os
from Cryptodome.Cipher import AES
import json
import secrets

# KHOA DUNG CHUNG TOAN MANG (16 byte cho AES-128)
NETWORK_KEY = bytes([0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
                     0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C])

def simulate_node_to_server(temp, humidity, seq):
    # Tao Payload JSON
    data = {"id": "IOT_NODE_01", "t": temp, "h": humidity, "co2": 450, "lat": 21.0045, "lon": 105.8433, "seq": seq}
    plaintext = json.dumps(data).encode('utf-8')
    
    # Pad plaintext voi ky tu NULL de chieu dai chia het cho 16
    padded_len = len(plaintext)
    if padded_len % 16 != 0:
        padded_len = ((padded_len // 16) + 1) * 16
    padded_plaintext = plaintext.ljust(padded_len, b'\0')

    # Ma hoa AES-128-CBC
    iv = secrets.token_bytes(16)
    cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(padded_plaintext)
    
    # Dong goi: [16 byte IV] + [Ciphertext]
    final_packet = iv + ciphertext
    return final_packet

if __name__ == "__main__":
    p = simulate_node_to_server(28.5, 60, 1)
    print(f"Generated Secure Packet: {p.hex()}")
