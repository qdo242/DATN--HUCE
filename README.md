# Đề tài: Xây dựng giải pháp truyền tin bảo mật giữa các thiết bị IoT

## 1. Kiến trúc hệ thống

```
Xi node (TTGO T-Beam: ESP32 + LoRa SX1276 + GPS NEO-M8N + BME280 + MAX30102 + OLED)
  │
  ├─ Bật nguồn → gửi Beacon "B|<Xi_ID>" qua LoRa
  ├─ Chờ ACK từ Y Gateway
  ├─ Đọc cảm biến (BME280, MAX30102, GPS, MQ)
  ├─ Mã hóa JSON bằng AES-128-CBC
  └─ Gửi "D|<Xi_ID>|<hex_encrypted>" qua LoRa
       │
       ▼
Y Gateway (ESP32 DevKit + LoRa SX1278 + WiFi/4G)
       │
       ├─ Quét LoRa → nhận Beacon → gửi ACK "A|<Xi_ID>|<Y_ID>"
       ├─ Nhận data → forward HTTP POST lên Server
       │
       ▼
Flask Server (Python + SQLite)
       │
       ├─ Giải mã AES-128-CBC
       ├─ Chống replay attack (sequence number)
       └─ Lưu vào database SQLite
       │
       ▼
Streamlit Dashboard (Python + Leaflet.js)
       ├─ Biểu đồ cảm biến (nhiệt độ, độ ẩm, áp suất, nhịp tim, SpO2, CO2, CO, NH3)
       ├─ Bản đồ GPS (OpenStreetMap + Leaflet)
       └─ Danh sách thiết bị
```

## 2. Mô tả bài toán

Hệ thống IoT gồm các nút cảm biến Xi (cố định) và Gateway Y (di động).

- **Mục tiêu:** Truyền tin nhanh, đơn giản, ít tốn tài nguyên, bảo mật ở mức vừa phải.
- **Yêu cầu:** Một Pre-Shared Key cho toàn mạng.
- **Kênh truyền:** Xi → LoRa → Y → WiFi/4G → Server.

## 3. Kiến trúc bảo mật

| Lớp | Công nghệ | Mô tả |
|-----|-----------|-------|
| Mã hóa | AES-128-CBC | Tận dụng hardware accelerator ESP32 (~17-18µs), IV 16 bytes ngẫu nhiên mỗi gói |
| Xác thực | Pre-Shared Key | Key `key_x_1234567890` dùng chung toàn mạng |
| Chống replay | Sequence number | Server kiểm tra `seq > last_seq`, từ chối gói cũ |
| Padding | Zero-padding | ESP32: `memset 0` → Server: `rstrip(b'\0')` |

## 4. Cấu trúc gói tin

```
Beacon:   B|<Xi_ID>
ACK:      A|<Xi_ID>|<Y_ID>
Data:     D|<Xi_ID>|<hex(IV 16 bytes + AES_CBC_ciphertext)>
```

## 5. Hướng dẫn chạy (3 terminal)

### Terminal 1: Flask Server

```bash
cd C:\Quan\ĐATN\DATN--DoAnhQuan
python server/init_db.py   # Tạo DB mới (xóa DB cũ nếu có)
python server/app.py       # Server lắng nghe tại http://127.0.0.1:5000
```

### Terminal 2: Localtunnel (cho Wokwi web)

```bash
lt --port 5000 --subdomain ten-cua-ban
```

Lấy URL (vd `https://ten-cua-ban.loca.lt`) → cập nhật vào `SERVER_URL` trong `wokwi/sketch.ino`.

### Terminal 3: Dashboard

```bash
python -m streamlit run server/dashboard.py
```

Mở trình duyệt tại `http://localhost:8501`.

## 6. Hướng dẫn chạy Wokwi web

1. Vào https://wokwi.com → **New Project** → **ESP32**
2. Copy 3 file trong `wokwi/wokwi_to_copy.md` lên Wokwi
3. Nhấn **Start Simulation**
4. Xem output serial: Beacon → ACK → AES encrypt → HTTP POST → Server

> Wokwi dùng 1 ESP32 đóng 2 vai trò Xi + Y, output serial thể hiện toàn bộ giao thức.

## 7. Hướng dẫn chạy hardware thật

### Thiết bị

| Thiết bị | Số lượng | Vai trò |
|----------|----------|---------|
| TTGO T-Beam (ESP32 + LoRa SX1276 + GPS NEO-M8N + OLED) | 1 | Xi node |
| ESP32 DevKit + LoRa SX1278 | 1 | Y Gateway |

### Cài đặt

1. Cài Arduino IDE
2. Thêm board ESP32: File → Preferences → Additional Board Manager URLs: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. Cài thư viện: **LoRa by Sandeep Mistry**, **Adafruit BME280**, **Adafruit MAX30105**, **TinyGPSPlus**, **U8g2**, **mbedtls** (built-in)
4. Mở `hardware/xi_node/xi_node.ino` → cấu hình WiFi → upload lên T-Beam
5. Mở `hardware/y_gateway/y_gateway.ino` → cấu hình WiFi + Server URL → upload lên ESP32 DevKit

## 8. Cấu trúc thư mục

```
DATN--DoAnhQuan/
├── hardware/
│   ├── xi_node/          # Firmware TTGO T-Beam Xi node
│   └── y_gateway/        # Firmware ESP32 Y Gateway
├── server/
│   ├── app.py            # Flask server (nhận + giải mã + lưu DB)
│   ├── init_db.py        # Khởi tạo SQLite database
│   ├── dashboard.py      # Streamlit dashboard + Leaflet map
│   ├── main_test.py      # Test nhanh (gửi 2 gói tin mẫu)
│   └── xor_cipher.py     # Tham khảo: XOR cipher
├── wokwi/
│   ├── sketch.ino        # Code mô phỏng Wokwi
│   ├── diagram.json      # Sơ đồ mạch Wokwi
│   ├── wokwi.toml        # Cấu hình Wokwi
│   └── wokwi_to_copy.md  # Hướng dẫn copy-paste lên Wokwi web
├── docs/                 # Tài liệu nghiên cứu
├── plan/                 # Kế hoạch thực hiện
├── guides/               # Hướng dẫn cài đặt
├── iot_security.db       # SQLite database
└── README.md
```

## 9. Các vấn đề đã fix

| Vấn đề | Nguyên nhân | Fix |
|--------|-------------|-----|
| Wokwi VS Code extension boot loop `rst:0x3` | Extension không ổn định | Chuyển sang Wokwi web |
| WiFi Wokwi không kết nối | Timeout ngắn + thiếu `WiFi.mode(WIFI_STA)` | Tăng timeout 80× + thêm `WiFi.mode` |
| HTTP -1 (connection refused) | Localtunnel chưa chạy | Chạy `lt --port 5000` trước |
| HTTP 403 "Decryption Failed" | mbedtls ghi đè biến `iv` sau encrypt | Dùng `iv_copy` lưu IV gốc |
| HTTP 403 "Device not found" | Sai case: `XI_01` vs `Xi_01` | Đồng bộ device_id |
| Dashboard crash "no such column: altitude" | DB cũ thiếu cột mới | Chạy lại `init_db.py` |

## 10. Phân công nhiệm vụ

- **Tạ Huy Hoàng:** Lắp ráp phần cứng (ESP32, LoRa, GPS, cảm biến), quy trình Beacon/ACK, chuyển tiếp Gateway→Server
- **Đỗ Anh Quân:** Mã hóa (XOR + AES-128-CBC), kiến trúc hệ thống, Flask Server, Database, Dashboard + Leaflet Map
