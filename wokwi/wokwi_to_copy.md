# Đề tài: Xây dựng giải pháp truyền tin bảo mật giữa các thiết bị IoT

Wokwi simulation của toàn bộ luồng: Xi node → LoRa → Y Gateway → Server → Dashboard.

## Kiến trúc hệ thống

```
Xi node (TTGO T-Beam: ESP32 + LoRa + BME280 + MAX30102 + GPS + OLED)
  │
  ├─ Bật nguồn → gửi Beacon "B|<Xi_ID>"
  ├─ Chờ ACK từ Y Gateway
  ├─ Đọc cảm biến (BME280, MAX30102, GPS)
  ├─ Mã hóa JSON bằng AES-128-CBC
  └─ Gửi "D|<Xi_ID>|<hex_encrypted>" qua LoRa
       │
       ▼
Y Gateway (ESP32 + LoRa + WiFi)
       │
       ├─ Quét LoRa → nhận Beacon → gửi ACK
       ├─ Nhận data → forward HTTP POST lên Server
       │
       ▼
Flask Server (Python + SQLite)
       │
       ├─ Giải mã AES-128-CBC
       ├─ Chống replay attack (seq)
       └─ Lưu vào SQLite
       │
       ▼
Streamlit Dashboard (Python + Leaflet)
       ├─ Biểu đồ cảm biến
       ├─ Bản đồ GPS
       └─ Danh sách thiết bị
```

---

## Cách chạy (cần 3 terminal)

### Terminal 1: Flask Server
```bash
cd C:\Quan\ĐATN\DATN--DoAnhQuan
python server\init_db.py
python server\app.py
```

### Terminal 2: Localtunnel
```bash
lt --port 5000 --subdomain ten-cua-ban
```

### Terminal 3: Dashboard
```bash
python -m streamlit run server\dashboard.py
```

Mở `http://localhost:8501`.

---

## Cách chạy 2 node Wokwi song song

Nội dung 3 file (`sketch.ino`, `diagram.json`, `wokwi.toml`) nằm trong 2 thư mục:
- `wokwi/xi_01/` — **Xi_01** (21.84470, 104.09700, delay 3s)
- `wokwi/xi_02/` — **Xi_02** (21.84550, 104.09820, delay 4s)

**Bước 1:** Chạy server + localtunnel (xem ở trên). Copy localtunnel URL → thay `SERVER_URL` trong cả 2 file `sketch.ino`.

**Bước 2 (Tab 1):** https://wokwi.com → New Project → ESP32 → copy 3 file từ `wokwi/xi_01/` → Start Simulation.

**Bước 3 (Tab 2):** Tab mới → https://wokwi.com → New Project → ESP32 → copy 3 file từ `wokwi/xi_02/` → Start Simulation.

**Kết quả:** Cả 2 node gửi data song song → Dashboard hiển thị 2 marker trên map Mù Cang Chải.

> **Mẹo:** Nếu không muốn dùng Wokwi, chạy `python server/simulator.py` — nó mô phỏng cả Xi_01 + Xi_02 gửi POST trực tiếp lên server (không cần localtunnel).

## Cấu trúc file

Cả 2 project đều dùng chung cấu trúc:

### `diagram.json` (giống nhau cho cả Xi_01 và Xi_02)
```json
{
  "version": 1,
  "author": "Do Anh Quan & Ta Huy Hoang",
  "editor": "wokwi",
  "parts": [
    { "type": "board-esp32-devkit-v1", "id": "esp", "top": -100, "left": -300, "attrs": {} },
    { "type": "board-ssd1306", "id": "oled1", "top": -130, "left": 250, "attrs": {} }
  ],
  "connections": [
    ["esp:TX0", "$serialMonitor:RX", "red", []],
    ["esp:RX0", "$serialMonitor:TX", "blue", []],
    ["esp:21", "oled1:SDA", "green", []],
    ["esp:22", "oled1:SCL", "yellow", []],
    ["esp:3V3", "oled1:VCC", "red", []],
    ["esp:GND.1", "oled1:GND", "black", []]
  ],
  "dependencies": {}
}
```

### `wokwi.toml` (giống nhau)
```toml
[wokwi]
version = 1
firmware = 'sketch.ino'
diagram = 'diagram.json'
```

### `sketch.ino` (khác nhau giữa Xi_01 và Xi_02)

Xem nội dung đầy đủ trong file:
- `wokwi/xi_01/sketch.ino` — device_id `Xi_01`, tọa độ 21.84470, 104.09700
- `wokwi/xi_02/sketch.ino` — device_id `Xi_02`, tọa độ 21.84550, 104.09820

Sự khác biệt chính giữa 2 file:
| Tham số | Xi_01 | Xi_02 |
|---------|-------|-------|
| `XI_ID` | `"Xi_01"` | `"Xi_02"` |
| Tọa độ | 21.84470, 104.09700 | 21.84550, 104.09820 |
| Nhiệt độ gốc | 28.0°C | 26.5°C |
| Độ ẩm gốc | 60% | 65% |
| Delay/cycle | 3s | 4s |

Cả 2 đều dùng chung:
- AES key: `key_x_1234567890`
- Y_ID: `Y_01`
- Server URL: localtunnel URL của bạn

---

## Giải thích linh kiện trong Wokwi

| Linh kiện | Wokwi | Ghi chú |
|-----------|-------|---------|
| **ESP32 DevKit** | `board-esp32-devkit-v1` | Có sẵn WiFi + I2C + UART |
| **BME280** | *(mô phỏng)* | Wokwi không hỗ trợ I2C BME280 — chạy thật trên hardware |
| **OLED SSD1306** | `board-ssd1306` | Hiển thị trạng thái Xi/Y, cảm biến, HTTP result |

**Không có trên Wokwi** (sẽ chạy khi có hardware thật):
- MAX30102 (nhịp tim, SpO2) — mô phỏng bằng `random()`
- GPS NEO-M8N — mô phỏng tọa độ tăng dần
- LoRa SX1276/SX1278 — mô phỏng qua Serial/UART

---

## Các vấn đề đã gặp và cách fix

| Vấn đề | Nguyên nhân | Fix |
|--------|-------------|-----|
| Wokwi VS Code extension boot loop `rst:0x3` | Extension không ổn định | Dùng Wokwi web thay thế |
| WiFi không kết nối | Timeout ngắn + thiếu `WiFi.mode(WIFI_STA)` | Tăng timeout 80 lần + thêm `WiFi.mode` |
| HTTP -1 (kết nối thất bại) | Localtunnel chưa chạy, hoặc URL sai | Chạy `lt --port 5000`, cập nhật `SERVER_URL` |
| HTTP 403 "Decryption Failed" | mbedtls ghi đè biến `iv` sau khi encrypt | Dùng `iv_copy` để lưu IV gốc |
| HTTP 403 "Device not found" | Sai case: `XI_01` vs `Xi_01` | Đồng bộ device_id |

---

## Ghi chú quan trọng

- **Pre-Shared Key:** Cả ESP32 và Server dùng chung key `key_x_1234567890`
- **Chống replay:** Sequence number (`seq`) tăng dần, server kiểm tra `seq > last_seq`
- **AES padding:** Zero-padding (ESP32 dùng `memset 0`, server dùng `rstrip(b'\0')`)
- **IV ngẫu nhiên:** Mỗi gói tin có IV 16 bytes mới, gửi kèm trong hex payload
- **Localtunnel:** Mỗi lần chạy lại `lt` có thể ra URL khác — nhớ cập nhật lại `SERVER_URL`
