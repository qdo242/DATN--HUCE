import os
import json

NETWORK_KEY = b"ABC123"

def xor_encrypt(data: bytes) -> bytes:
    key_len = len(NETWORK_KEY)
    return bytes(data[i] ^ NETWORK_KEY[i % key_len] for i in range(len(data)))

def xor_decrypt(data: bytes) -> bytes:
    return xor_encrypt(data)

def make_packet(device_id, temp, humid, co2, co, nh3, lat, lon, seq):
    data = {
        "id": device_id,
        "t": temp,
        "h": humid,
        "co2": co2,
        "co": co,
        "nh3": nh3,
        "lat": lat,
        "lon": lon,
        "seq": seq
    }
    plaintext = json.dumps(data).encode('utf-8')
    return xor_encrypt(plaintext)

if __name__ == "__main__":
    pt = b'{"id":"Xi_01","t":28.5}'
    ct = xor_encrypt(pt)
    print(f"Plaintext:  {pt}")
    print(f"Ciphertext: {ct.hex()}")
    dt = xor_decrypt(ct)
    print(f"Decrypted:  {dt}")
    assert pt == dt
    print("XOR OK: (X XOR K) XOR K = X")
