# Đề tài: Xây dựng giải pháp truyền tin bảo mật giữa các thiết bị IoT

Hệ thống IoT: Xi node (ESP32 + cảm biến) → LoRa → Y Gateway → WiFi → Server → Dashboard.

---

## 🚀 Hướng dẫn chạy (clone → chạy)

### Yêu cầu

- **Python 3.10+**
- **Git**
- **Arduino IDE** (nếu chạy hardware thật)

### Bước 1: Clone & cài đặt

```bash
git clone https://github.com/qdo242/DATN--DoAnhQuan.git
cd DATN--DoAnhQuan
pip install -r requirements.txt
```

### Bước 2: Khởi tạo Database

```bash
python server/init_db.py
```

### Bước 3: Chạy Server

```bash
python server/app.py
```

Server chạy tại `http://127.0.0.1:5000`.

### Bước 4: Chạy Dashboard (mở terminal mới)

```bash
streamlit run server/dashboard.py
```

Mở trình duyệt tại `http://localhost:8501`.

### Bước 5: Chạy mô phỏng Wokwi

1. Vào https://wokwi.com → **New Project** → **ESP32**
2. Copy **3 file** sau vào Wokwi:
   - `wokwi/sketch.ino`
   - `wokwi/diagram.json`
   - `wokwi/wokwi.toml`
3. Nhấn **Start Simulation**
4. Quan sát Serial Output: WiFi → Beacon → ACK → AES → HTTP POST 200

> Nếu cần expose server ra internet cho Wokwi: mở terminal thứ 4 chạy `lt --port 5000 --subdomain ten-cua-ban` (cài `npm install -g localtunnel`), lấy URL cập nhật vào `SERVER_URL` trong `wokwi/sketch.ino`.

---

## Kiến trúc hệ thống

```
Xi node (TTGO T-Beam: ESP32 + LoRa + GPS + BME280 + MAX30102 + OLED)
  │
  ├─ Beacon: "B|<Xi_ID>" (LoRa)
  ├─ Nhận ACK từ Y
  ├─ Đọc cảm biến
  ├─ Mã hóa AES-128-CBC
  └─ Gửi: "D|<Xi_ID>|<hex>"
       │
       ▼
Y Gateway (ESP32 + LoRa + WiFi)
       │
       ├─ Gửi ACK
       └─ HTTP POST → Server
       │
       ▼
Flask Server (Python + SQLite)
       │
       ├─ Giải mã AES-128-CBC
       ├─ Chống replay (seq)
       └─ Lưu telemetry
       │
       ▼
Streamlit Dashboard (Python + Leaflet.js)
       ├─ Biểu đồ cảm biến
       ├─ Bản đồ GPS
       └─ Danh sách thiết bị
```

## Giao thức mạng

| Gói tin | Định dạng | Mô tả |
|---------|-----------|-------|
| Beacon | `B|<Xi_ID>` | Xi gửi để báo có mặt |
| ACK | `A|<Xi_ID>|<Y_ID>` | Y xác nhận, sẵn sàng nhận data |
| Data | `D|<Xi_ID>|<hex>` | Dữ liệu cảm biến mã hóa AES-128-CBC |

## Bảo mật

| Lớp | Công nghệ |
|-----|-----------|
| Mã hóa | AES-128-CBC, IV 16 bytes ngẫu nhiên mỗi gói |
| Xác thực | Pre-Shared Key: `key_x_1234567890` |
| Chống replay | Sequence number, server kiểm tra `seq > last_seq` |
| Padding | Zero-padding (ESP32: `memset 0` ↔ Server: `rstrip(b'\0')`) |

## Cấu trúc thư mục

```
DATN--DoAnhQuan/
├── hardware/
│   ├── xi_node/xi_node.ino       # Firmware TTGO T-Beam
│   └── y_gateway/y_gateway.ino   # Firmware Y Gateway
├── server/
│   ├── app.py                    # Flask server
│   ├── init_db.py                # Khởi tạo SQLite
│   ├── dashboard.py              # Streamlit dashboard
│   ├── main_test.py              # Test nhanh
│   └── xor_cipher.py             # Tham khảo XOR cipher
├── wokwi/
│   ├── sketch.ino                # Code mô phỏng Wokwi
│   ├── diagram.json              # Sơ đồ mạch
│   ├── wokwi.toml                # Cấu hình
│   └── wokwi_to_copy.md          # Hướng dẫn copy-paste lên Wokwi
├── docs/                         # Tài liệu nghiên cứu
├── plan/                         # Kế hoạch thực hiện
├── guides/                       # Hướng dẫn cài đặt
├── requirements.txt              # Python dependencies
└── README.md
```

## Các vấn đề đã fix

| Vấn đề | Nguyên nhân | Fix |
|--------|-------------|-----|
| Wokwi VS Code extension boot loop | Extension không ổn định | Dùng Wokwi web |
| WiFi Wokwi không kết nối | Timeout ngắn | Tăng timeout 80x |
| HTTP -1 (connection refused) | Localtunnel chưa chạy | Chạy `lt --port 5000` |
| HTTP 403 "Decryption Failed" | mbedtls ghi đè iv | Dùng iv_copy |
| HTTP 403 "Device not found" | Sai case device_id | Đồng bộ `Xi_01` |
| HTTP 403 "Replay attack" | Chạy lại seq từ đầu | Random seq mỗi lần boot |

## Phần cứng (khi có hardware thật)

| Thiết bị | SL | Vai trò |
|----------|----|---------|
| TTGO T-Beam (ESP32 + LoRa SX1276 + GPS NEO-M8N + OLED) | 1 | Xi node |
| ESP32 DevKit + LoRa SX1278 | 1 | Y Gateway |
| BME280 | 1 | Nhiệt độ, độ ẩm, áp suất |
| MAX30102 | 1 | Nhịp tim, SpO2 |

## Phân công

- **Tạ Huy Hoàng:** Phần cứng (ESP32, LoRa, GPS, cảm biến), giao thức Beacon/ACK, chuyển tiếp Gateway→Server
- **Đỗ Anh Quân:** Mã hóa AES-128-CBC, Flask Server, SQLite, Dashboard + Leaflet Map
