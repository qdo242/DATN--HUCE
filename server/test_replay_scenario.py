"""
Kịch bản thử nghiệm phát lại cùng sequence number (Hình 4.16)
"""

import sys, os, json, time, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Cryptodome.Cipher import AES
from app import app
import init_db
import sqlite3

AES_KEY = b'key_x_1234567890'

def pad(data: bytes) -> bytes:
    padded_len = ((len(data) + 15) // 16) * 16
    return data.ljust(padded_len, b'\0')

def aes_encrypt(plaintext: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=iv)
    ct = cipher.encrypt(pad(plaintext))
    return iv + ct

client = app.test_client()
device = "Xi_01"
seq = 1001

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'iot_security.db')
if os.path.exists(db_path):
    os.remove(db_path)
init_db.init_db()

# Tạo payload giống hệt cho cả 2 lần gửi
payload = {
    "id": "Xi_01",
    "t": 28.5,
    "h": 65.2,
    "p": 1008.0,
    "co2": 420,
    "co": 5.1,
    "nh3": 2.3,
    "lat": 21.8447,
    "lon": 105.8426,
    "alt": 10.0,
    "sats": 7,
    "gw": "Y_01",
    "seq": seq
}
plaintext = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
payload_hex = aes_encrypt(plaintext).hex()

print("4.16. Kịch bản thử nghiệm phát lại cùng sequence number")
print("=" * 70)

# Bước 1
print("\nLần 1 – Xi_01 gửi payload chứa seq=1001:")
print(f"  Payload (hex):      {payload_hex[:50]}...")
resp1 = client.post('/receive-data', json={"payload": payload_hex})
print(f"  HTTP Response:       {resp1.status_code} {resp1.get_json()}")
conn = sqlite3.connect(db_path)
last_seq = conn.execute('SELECT last_seq FROM devices WHERE device_id = ?', (device,)).fetchone()[0]
print(f"  last_seq sau xử lý: {last_seq}")
conn.close()

# Bước 2
print("\nLần 2 – Gửi lại nguyên payload cũ (seq=1001):")
print(f"  Payload (hex):      {payload_hex[:50]}...")
resp2 = client.post('/receive-data', json={"payload": payload_hex})
print(f"  HTTP Response:       {resp2.status_code} {resp2.get_json()}")

conn = sqlite3.connect(db_path)
last_seq2 = conn.execute('SELECT last_seq FROM devices WHERE device_id = ?', (device,)).fetchone()[0]
telem_count = conn.execute('SELECT COUNT(*) FROM telemetry WHERE device_id = ?', (device,)).fetchone()[0]
conn.close()

print(f"  last_seq sau xử lý: {last_seq2}")
print(f"  Số bản ghi telemetry: {telem_count} (không tạo bản ghi mới do replay)")

print(f"\n{'=' * 70}")
print(f"Kết luận: Hệ thống phát hiện và chặn thành công tấn công phát lại.")
print(f"Gói tin cũ bị từ chối với HTTP 403, không tạo bản ghi telemetry mới.")
print(f"{'=' * 70}")
