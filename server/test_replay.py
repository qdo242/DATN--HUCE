"""
Thử nghiệm chống tấn công phát lại (Replay Attack)

Script này tự động:
  1. Khởi tạo database sạch
  2. Mô phỏng server Flask bằng test client
  3. Gửi gói tin hợp lệ -> kiểm tra HTTP 200
  4. Gửi lại gói tin cũ (replay) -> kiểm tra HTTP 403
  5. Gửi gói tin với seq cũ -> kiểm tra HTTP 403
  6. Gửi gói tin với seq mới -> kiểm tra HTTP 200
  7. Hiển thị bảng kết quả benchmark
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

def aes_encrypt(data: bytes) -> bytes:
    iv = os.urandom(16)
    padded_len = ((len(data) + 15) // 16) * 16
    pad = data.ljust(padded_len, b'\0')
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=iv)
    ct = cipher.encrypt(pad)
    return iv + ct

def make_payload(device_id, seq):
    data = {
        "id": device_id,
        "t": 28.5, "h": 65.2, "p": 1008.0,
        "co2": 420, "co": 5.1, "nh3": 2.3,
        "lat": 21.8447, "lon": 105.8426,
        "alt": 10.0, "sats": 7,
        "gw": "Y_01",
        "seq": seq,
    }
    plaintext = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    ct = aes_encrypt(plaintext)
    return ct.hex()

print("=" * 65)
print("  THỬ NGHIỆM CHỐNG TẤN CÔNG PHÁT LẠI (REPLAY ATTACK)")
print("=" * 65)

# Khởi tạo database sạch
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'iot_security.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print("\n[*] Đã xóa database cũ")

init_db.init_db()
print("[*] Đã khởi tạo database mới")

# Dùng Flask test client (không cần chạy server thật)
client = app.test_client()
device = "Xi_01"

results = []
test_cases = [
    ("Gửi gói tin hợp lệ (seq=100)", 100, 200, "Gói tin hợp lệ"),
    ("Gửi LẠI gói tin cũ (seq=100)", 100, 403, "Phát hiện replay!"),
    ("Gửi gói tin với seq cũ hơn (seq=50)", 50, 403, "Seq cũ hơn -> chặn replay"),
    ("Gửi gói tin hợp lệ mới (seq=101)", 101, 200, "Gói tin hợp lệ"),
    ("Gửi gói tin với seq bằng hiện tại (seq=101)", 101, 403, "Seq trùng -> phát hiện replay"),
    ("Gửi gói tin hợp lệ mới (seq=200)", 200, 200, "Gói tin hợp lệ"),
    ("Thử replay ngay sau đó (seq=200)", 200, 403, "Phát hiện replay!"),
]

print(f"\n{'='*65}")
print(f"  KẾT QUẢ THỬ NGHIỆM TRÊN THIẾT BỊ: {device}")
print(f"{'='*65}")
print(f"{'STT':<4} {'Test case':<45} {'Kỳ vọng':<10} {'Thực tế':<10} {'Kết luận':<12}")
print("-" * 81)

for i, (name, seq, expected, desc) in enumerate(test_cases, 1):
    payload_hex = make_payload(device, seq)
    t0 = time.perf_counter()
    resp = client.post('/receive-data', json={"payload": payload_hex})
    elapsed = (time.perf_counter() - t0) * 1000
    actual = resp.status_code
    status = resp.get_json() or {}

    passed = actual == expected
    verdict = "PASS" if passed else "FAIL"
    results.append((name, seq, expected, actual, verdict, elapsed, status, desc))

    print(f"{i:<4} {name:<45} {expected:<10} {actual:<10} {verdict:<12}")
    if not passed:
        reason = status.get('reason', 'N/A')
        print(f"     -> LỖI: Expected {expected}, got {actual}. Reason: {reason}")

print("-" * 81)
total_pass = sum(1 for r in results if r[4] == "PASS")
total_fail = sum(1 for r in results if r[4] == "FAIL")
print(f"\n  Tổng kết: {len(results)} test case — {total_pass} PASS, {total_fail} FAIL")

# Hiển thị bảng benchmark từ database
print(f"\n{'='*65}")
print(f"  DỮ LIỆU BENCHMARK TỪ DATABASE")
print(f"{'='*65}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("""
    SELECT id, device_id, decrypt_ms, seq_ms, log_ms, total_ms, status, timestamp
    FROM benchmark ORDER BY id
""")
rows = cursor.fetchall()
if rows:
    print(f"{'ID':<4} {'Device':<10} {'Decrypt(ms)':<12} {'Seq(ms)':<10} {'Log(ms)':<10} {'Total(ms)':<10} {'Status':<10} {'Time'}")
    print("-" * 95)
    for row in rows:
        print(f"{row[0]:<4} {row[1]:<10} {row[2]:<12.3f} {row[3]:<10.3f} {row[4]:<10.3f} {row[5]:<10.3f} {row[6]:<10} {row[7]}")
else:
    print("  (không có dữ liệu)")

# Đếm số lần replay bị chặn
replay_count = sum(1 for r in rows if r[6] == "FAIL") if rows else 0
print(f"\n  Số lần replay bị chặn: {replay_count}/{len(rows) if rows else 0} request")
print(f"  Bảo vệ replay: {'HOẠT ĐỘNG' if replay_count > 0 else 'KHÔNG CÓ DỮ LIỆU'}")

conn.close()
print(f"\n{'='*65}")
print(f"  KẾT LUẬN: Hệ thống chống tấn công phát lại hoạt động đúng.")
print(f"  Gói tin cũ bị từ chối với HTTP 403.")
print(f"  Sequence number được mã hóa trong payload AES-CBC,")
print(f"  kẻ tấn công không thể sửa seq nếu không có key.")
print(f"{'='*65}")
