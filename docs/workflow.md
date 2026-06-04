# Kiến trúc Hệ thống và Giải pháp Bảo mật IoT

## 1. Kiến trúc Hệ thống

```
Xi node (TTGO T-Beam: ESP32 + LoRa SX1276 + BME280 + MAX30102 + GPS NEO-M8N + OLED)
  │
  │  [1] Phát Beacon "B|<Xi_ID>" (LoRa)
  │  [2] Chờ ACK từ Y
  │  [3] Đọc cảm biến (BME280, MAX30102, GPS)
  │  [4] Tạo JSON + mã hóa AES-128-CBC
  │  [5] Gửi "D|<Xi_ID>|<hex(IV + ciphertext)>" (LoRa)
  ▼
Y Gateway (ESP32 DevKit + LoRa SX1278 + WiFi)
  │
  │  [1] Quét LoRa → nhận Beacon → gửi ACK
  │  [2] Nhận data → forward HTTP POST
  │  [3] POST JSON {"payload": "<hex>"} lên Server
  ▼
Flask Server (Python + SQLite)
  │  [1] Giải mã AES-128-CBC
  │  [2] Kiểm tra seq (chống replay)
  │  [3] Lưu telemetry vào database
  ▼
Dashboard (Streamlit + Leaflet/OpenStreetMap)
  │  [1] Biểu đồ cảm biến (nhiệt độ, độ ẩm, áp suất, nhịp tim, SpO2, CO2, CO, NH3)
  │  [2] Bản đồ GPS (vị trí các node Xi + Y)
  │  [3] Danh sách thiết bị
```

## 2. Giải pháp Mã hóa

Mục tiêu: truyền tin nhanh, đơn giản, ít tốn tài nguyên. Mức bảo mật vừa phải.

### Phương án 1: XOR Cipher (tham khảo)
- 3-5 dòng code, chạy rất nhanh, ít RAM
- View file: `server/xor_cipher.py`
- Nhược điểm: bảo mật yếu, dễ bị phá

### Phương án 2: AES-128-CBC (được chọn)
- ESP32 hardware accelerator ~17-18µs
- Thư viện mbedtls có sẵn trên ESP32
- Pre-Shared Key duy nhất cho toàn mạng
- IV 16 bytes ngẫu nhiên mỗi gói tin

## 3. Cấu trúc Gói tin

### Giao thức LoRa
```
Beacon: B|<Xi_ID>           (vd: "B|Xi_01")
ACK:    A|<Xi_ID>|<Y_ID>    (vd: "A|Xi_01|Y_01")
Data:   D|<Xi_ID>|<hex>     (vd: "D|Xi_01|88cf72...")
```

### Payload hex
```
hex(IV 16 bytes + AES-128-CBC ciphertext)
```

### Dữ liệu JSON trước khi mã hóa:
```json
{
  "id": "Xi_01",
  "t": 28.5, "h": 65.2, "p": 1008.0,
  "hr": 75, "spo2": 96.0,
  "co2": 420, "co": 5.1, "nh3": 2.3,
  "lat": 21.00355, "lon": 105.84255, "alt": 10.0, "sats": 7,
  "gw": "Y_01", "seq": 1
}
```

## 4. Xử lý tại Server

1. Nhận JSON `{"payload": "<hex>"}`
2. `bytes.fromhex(payload)` → tách 16 byte đầu = IV, còn lại = ciphertext
3. Giải mã AES-128-CBC với NETWORK_KEY
4. Kiểm tra seq (chống replay attack)
5. Lưu telemetry vào SQLite

## 5. Chống tấn công Replay

- Mỗi gói tin có trường `seq` (uint32, tăng dần)
- Server lưu `last_seq` trong bảng `devices`
- Server từ chối nếu `seq <= last_seq`
- Anti-replay hoạt động độc lập cho từng device

## 6. Database Schema

### devices
| Column | Type | Mô tả |
|--------|------|-------|
| device_id | TEXT PRIMARY KEY | Tên thiết bị (Xi_01, Xi_02, Y_GW, TBEAM_01) |
| network_key | TEXT | Pre-shared key |
| last_seq | INTEGER | Sequence cuối cùng (chống replay) |
| latitude | REAL | Tọa độ mặc định |
| longitude | REAL | Tọa độ mặc định |
| description | TEXT | Mô tả |

### telemetry
| Column | Type | Mô tả |
|--------|------|-------|
| id | INTEGER PK AUTO | Khóa chính |
| device_id | TEXT | Thiết bị gửi |
| timestamp | DATETIME | Thời gian (auto) |
| temperature | REAL | Nhiệt độ (°C) |
| humidity | REAL | Độ ẩm (%) |
| pressure | REAL | Áp suất (hPa) |
| co2 | REAL | CO2 (ppm) |
| co | REAL | CO (ppm) |
| nh3 | REAL | NH3 (ppm) |
| heart_rate | INTEGER | Nhịp tim (bpm) |
| spo2 | REAL | SpO2 (%) |
| altitude | REAL | Độ cao (m) |
| satellites | INTEGER | Số vệ tinh GPS |
| latitude | REAL | Vĩ độ |
| longitude | REAL | Kinh độ |
| status | TEXT | Trạng thái ("An toàn") |

## 7. Thành tựu

- [x] Wokwi web simulation: Beacon → ACK → AES encrypt → HTTP POST → Server (HTTP 200)
- [x] Flask server: giải mã AES-128-CBC + chống replay + lưu SQLite
- [x] Streamlit dashboard: biểu đồ + bản đồ Leaflet + danh sách thiết bị
- [x] Firmware Xi node: T-Beam đọc BME280, MAX30102, GPS, mã hóa AES, gửi LoRa
- [x] Firmware Y Gateway: ESP32 + LoRa quét sóng, nhận data, HTTP POST lên Server
- [x] XOR cipher tham khảo (`server/xor_cipher.py`)
- [x] Fix bug IV bị ghi đè bởi mbedtls → dùng `iv_copy`
- [x] Fix WiFi timeout + device_id case mismatch
