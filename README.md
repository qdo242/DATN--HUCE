# Xây dựng giải pháp truyền tin bảo mật giữa các thiết bị IoT

**Đồ án tốt nghiệp** — Sinh viên thực hiện: **Đỗ Anh Quân** & **Tạ Huy Hoàng**

---

## Mục lục

- [Giới thiệu](#gioi-thieu)
- [Kiến trúc hệ thống](#kien-truc-he-thong)
- [Yêu cầu phần cứng](#yeu-cau-phan-cung)
- [Yêu cầu phần mềm](#yeu-cau-phan-mem)
- [Cài đặt và chạy](#cai-dat-va-chay)
- [Chạy mô phỏng Wokwi](#chay-mo-phong-wokwi)
- [Chạy trên phần cứng thật](#chay-tren-phan-cung-that)
- [Giao thức truyền tin](#giao-thuc-truyen-tin)
- [Bảo mật](#bao-mat)
- [Kiểm tra hệ thống](#kiem-tra-he-thong)
- [Cấu trúc thư mục](#cau-truc-thu-muc)
- [Các vấn đề thường gặp](#cac-van-de-thuong-gap)
- [Phân công công việc](#phan-cong-cong-viec)

---

## Giới thiệu

Hệ thống này giải quyết bài toán truyền tin bảo mật giữa các thiết bị IoT trong môi trường thực tế, nơi hạ tầng mạng không phải lúc nào cũng sẵn có. Các thiết bị cảm biến Xi được rải sẵn tại hiện trường, liên tục phát tín hiệu Beacon qua LoRa. Một người dùng mang theo thiết bị Y (Gateway) di chuyển qua vùng phủ sóng, bắt tay với các Xi để thu thập dữ liệu cảm biến và GPS, sau đó chuyển tiếp lên Server trung tâm qua WiFi/4G. Toàn bộ dữ liệu được mã hóa bằng AES-128-CBC trước khi truyền.

Luồng dữ liệu tổng quan:

```
Xi (ESP32 + cảm biến + LoRa) --> LoRa --> Y Gateway (ESP32 + LoRa + WiFi)
                                               |
                                               v
                                    Flask Server (Python + SQLite)
                                               |
                                               v
                                    Streamlit Dashboard (Web Map + Biểu đồ)
```

Các thiết bị Xi đo các tham số môi trường: nhiệt độ, độ ẩm, CO, CO2, NH3, kết hợp với tọa độ GPS và gửi về Server thông qua Gateway.

---

## Kiến trúc hệ thống

### Mô hình triển khai

```
Khu vực hiện trường (các Xi đã được rải sẵn)
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │  Xi_01  │   │  Xi_02  │   │  Xi_... │   (cảm biến + LoRa)
  │ (LoRa)  │   │ (LoRa)  │   │ (LoRa)  │
  └────┬────┘   └────┬────┘   └────┬────┘
       │             │             │
       └─────────────┼─────────────┘
                     │  Beacon / Data qua LoRa
                     ▼
              ┌──────────┐
              │ Y Gateway │  (Người dùng mang theo, di chuyển)
              │ (LoRa +   │
              │  WiFi/4G) │
              └────┬─────┘
                   │  HTTP POST (JSON)
                   ▼
           ┌──────────────┐
           │ Flask Server │  (Python + SQLite)
           │ - Giải mã    │
           │ - Chống replay│
           │ - Lưu SQLite  │
           └──────┬───────┘
                  │
                  ▼
           ┌──────────────┐
           │  Dashboard   │  (Streamlit + Leaflet)
           │ - Bản đồ GPS │
           │ - Biểu đồ    │
           │ - Thiết bị   │
           └──────────────┘
```

### Luồng giao tiếp chi tiết

1. **Beacon**: Thiết bị Xi phát Beacon `B|<Xi_ID>` qua LoRa theo chu kỳ.
2. **ACK**: Khi Y Gateway đến gần và nhận được Beacon, nó trả lời `A|<Xi_ID>|<Y_ID>`.
3. **Thu thập dữ liệu**: Xi đọc cảm biến (nhiệt độ, độ ẩm, CO, CO2, NH3) và GPS.
4. **Mã hóa**: Xi tạo JSON payload, mã hóa bằng AES-128-CBC với IV ngẫu nhiên 16 byte.
5. **Gửi dữ liệu**: Xi gửi `D|<Xi_ID>|<hex(IV + ciphertext)>` qua LoRa.
6. **Chuyển tiếp**: Y Gateway nhận dữ liệu, đóng gói `{"payload": "<hex>"}` và POST lên Server.
7. **Xử lý Server**: Server giải mã AES, kiểm tra seq (chống replay), lưu vào SQLite.
8. **Hiển thị**: Dashboard Streamlit hiển thị dữ liệu lên bản đồ Leaflet và biểu đồ.

---

## Yêu cầu phần cứng

### Danh sách thiết bị (khi chạy thật)

| Thiết bị | Số lượng | Vai trò | Ghi chú |
|----------|----------|---------|---------|
| TTGO T-Beam (ESP32 + LoRa SX1276 + GPS NEO-M8N + OLED) | 1 | Xi node | Đã có |
| ESP32 DevKit + LoRa SX1278 (433 MHz) | 1 | Y Gateway | Chưa có |
| BME280 | 1 | Cảm biến nhiệt độ, độ ẩm, áp suất | Đã có |
| MAX30102 | 1 | Cảm biến nhịp tim, SpO2 | Đã có |
| OLED SSD1306 (I2C 0x3C) | 1 | Hiển thị trạng thái | Đã có |

> **Lưu ý:** TTGO T-Beam đã tích hợp sẵn ESP32, LoRa SX1276, GPS NEO-M8N và OLED. Chưa có ESP32 thứ hai và module LoRa rời để làm Y Gateway. Khi chưa có phần cứng, sử dụng mô phỏng Wokwi.

### Sơ đồ chân T-Beam

| Module | Chân kết nối |
|--------|-------------|
| LoRa SPI | SCK=5, MISO=19, MOSI=27, CS=18, RST=23, DIO0=26 |
| GPS UART2 | RX=12, TX=15 |
| I2C bus | SDA=21, SCL=22 |
| OLED | I2C địa chỉ 0x3C |
| BME280 | I2C địa chỉ 0x76 |

---

## Yêu cầu phần mềm

- **Python** 3.10 trở lên
- **Git** (để clone repository)
- **Arduino IDE** (nếu nạp firmware cho phần cứng thật)
- **Node.js** (cho localtunnel, nếu cần expose server ra internet cho Wokwi)

### Thư viện Python

Liệt kê trong `requirements.txt`:
- flask
- pycryptodome
- streamlit
- folium
- streamlit-folium
- pandas

---

## Cài đặt và chạy

### Bước 1: Clone repository

```bash
git clone https://github.com/qdo242/DATN--DoAnhQuan.git
cd DATN--DoAnhQuan
```

### Bước 2: Cài đặt thư viện Python

```bash
pip install -r requirements.txt
```

Nếu dùng pip trên Windows và gặp lỗi quyền, thử:

```bash
pip install --user -r requirements.txt
```

### Bước 3: Khởi tạo database

```bash
python server/init_db.py
```

Lệnh này sẽ tạo file `iot_security.db` với hai bảng `devices` và `telemetry`, đồng thời thêm hai thiết bị mẫu: `Xi_01` và `Y_01`.

### Bước 4: Chạy Flask Server

Mở **Terminal thứ nhất**:

```bash
python server/app.py
```

Server sẽ chạy tại `http://127.0.0.1:5000`. Bạn sẽ thấy log:

```
 * Running on http://127.0.0.1:5000
```

### Bước 5: Chạy Dashboard

Mở **Terminal thứ hai**:

```bash
streamlit run server/dashboard.py
```

Dashboard sẽ chạy tại `http://localhost:8501`. Mở trình duyệt và truy cập địa chỉ này để xem bản đồ và biểu đồ.

### Bước 6: (Tùy chọn) Chạy localtunnel để expose server ra internet

Nếu muốn Wokwi kết nối đến server qua internet (vì Wokwi không truy cập được localhost), cần expose server ra public:

```bash
npm install -g localtunnel
lt --port 5000 --subdomain ten-cua-ban
```

Sau khi chạy, localtunnel sẽ cấp một URL như `https://ten-cua-ban.loca.lt`. Lấy URL này và cập nhật vào `SERVER_URL` trong file `wokwi/sketch.ino` trước khi chạy Wokwi.

---

## Chạy mô phỏng Wokwi

Do chưa có đủ phần cứng, toàn bộ hệ thống có thể được mô phỏng trên Wokwi (một trình giả lập ESP32 chạy trên web).

### Các bước thực hiện

1. Vào [https://wokwi.com](https://wokwi.com), đăng nhập (có thể dùng tài khoản Google hoặc GitHub).
2. Chọn **New Project** → chọn board **ESP32 DevKit V1**.
3. Copy 3 file sau từ repository vào Wokwi (mỗi file paste vào tab tương ứng):

   | File trong repo | File trên Wokwi | Mô tả |
   |----------------|-----------------|-------|
   | `wokwi/sketch.ino` | `sketch.ino` | Mã nguồn ESP32 mô phỏng |
   | `wokwi/diagram.json` | `diagram.json` | Sơ đồ kết nối linh kiện |
   | `wokwi/wokwi.toml` | `wokwi.toml` | Cấu hình dự án |

4. **Quan trọng:** Trong file `sketch.ino`, cập nhật hằng số `SERVER_URL` bằng URL localtunnel của bạn (nếu Wokwi cần kết nối internet). Nếu bạn chỉ chạy server local và Wokwi không cần POST thật, có thể giữ nguyên URL mặc định nhưng sẽ nhận HTTP -1.

   ```cpp
   const char* SERVER_URL = "https://ten-cua-ban.loca.lt/receive-data";
   ```

5. Nhấn nút **Start Simulation** (màu xanh, ở góc trên bên trái).

### Quan sát kết quả

Khi mô phỏng chạy, bạn sẽ thấy trên Serial Monitor (tab Serial):

1. **Khởi động**: ESP32 khởi động, kết nối WiFi (`Wokwi-GUEST`).
2. **OLED hiển thị**: Dòng chữ "Dang khoi dong...", sau đó "WiFi OK" kèm IP.
3. **Phase 1 - Beacon**: Xi phát `B|Xi_01`.
4. **Phase 2 - ACK**: Y nhận Beacon, trả `A|Xi_01|Y_01`.
5. **Phase 3 - Sensor**: Đọc cảm biến giả lập (random), hiển thị lên OLED.
6. **Phase 4 - Mã hóa**: JSON được mã hóa AES-128-CBC, tạo hex payload.
7. **Phase 5 - HTTP POST**: Gửi lên Server, nhận HTTP 200 nếu thành công.
8. **Kết thúc**: Sau 4 chu kỳ, mô phỏng dừng lại.

Trên OLED bạn sẽ thấy lần lượt các trạng thái: trạng thái WiFi, Beacon, ACK, giá trị cảm biến, và kết quả HTTP.

### Lưu ý khi mô phỏng

- **BME280**: Wokwi không hỗ trợ cảm biến BME280 qua I2C (Wokwi chỉ hỗ trợ SPI). Do đó tất cả giá trị cảm biến được mô phỏng bằng hàm `random()`.
- **MAX30102**: Không có trên Wokwi, mô phỏng bằng random.
- **GPS NEO-M8N**: Không có trên Wokwi, tọa độ mô phỏng tăng dần qua mỗi chu kỳ.
- **LoRa**: Không có module LoRa trên Wokwi, toàn bộ giao thức Beacon/ACK/Data được mô phỏng qua Serial (in ra màn hình).

---

## Chạy trên phần cứng thật

### Nạp firmware cho Xi node (TTGO T-Beam)

1. Cài đặt Arduino IDE.
2. Thêm board ESP32 vào Arduino IDE:
   - File → Preferences → Additional Boards Manager URLs: thêm `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → tìm "ESP32" → cài đặt.
3. Cài đặt các thư viện cần thiết (qua Library Manager):
   - `mbedtls` (có sẵn trong ESP32 core)
   - `TinyGPSPlus`
   - `LoRa` by Sandeep Mistry
   - `Adafruit BME280`
   - `Adafruit MAX30105`
   - `Adafruit SSD1306` + `Adafruit GFX`
   - `U8g2` (cho OLED T-Beam)
4. Mở file `hardware/xi_node/xi_node.ino` trong Arduino IDE.
5. Chọn board: Tools → Board → ESP32 → **TTGO T-Beam**.
6. Chọn cổng COM tương ứng.
7. Nhấn **Upload**.

### Nạp firmware cho Y Gateway

Khi có ESP32 thứ hai và module LoRa SX1278:

1. Mở file `hardware/y_gateway/y_gateway.ino`.
2. Cập nhật thông tin WiFi và địa chỉ Server.
3. Chọn board ESP32 DevKit và upload.

---

## Giao thức truyền tin

### Cấu trúc gói tin LoRa

Giao thức sử dụng văn bản thuần (plain text) trên LoRa, định dạng:

| Loại | Định dạng | Ví dụ | Mô tả |
|------|-----------|-------|-------|
| Beacon | `B|<Xi_ID>` | `B|Xi_01` | Xi phát để báo hiệu có mặt |
| ACK | `A|<Xi_ID>|<Y_ID>` | `A|Xi_01|Y_01` | Y xác nhận đã nhận Beacon |
| Data | `D|<Xi_ID>|<hex>` | `D|Xi_01|a1b2c3...` | Dữ liệu cảm biến đã mã hóa |

### Cấu trúc dữ liệu JSON (trước mã hóa)

```json
{
  "id": "Xi_01",
  "t": 28.5,
  "h": 65.2,
  "p": 1008.0,
  "hr": 75,
  "spo2": 96.0,
  "co2": 420,
  "co": 5.1,
  "nh3": 2.3,
  "lat": 21.00355,
  "lon": 105.84255,
  "alt": 10.0,
  "sats": 7,
  "gw": "Y_01",
  "seq": 1001
}
```

### Cấu trúc payload hex (sau mã hóa)

```
hex(IV 16 bytes + AES-128-CBC ciphertext)
```

Server thực hiện:
1. `bytes.fromhex(payload)` → 16 byte đầu là IV, phần còn lại là ciphertext.
2. Giải mã AES-128-CBC với NETWORK_KEY.
3. Parse JSON và kiểm tra seq.

### Payload HTTP từ Gateway lên Server

```json
{"payload": "a1b2c3d4e5f6..."}
```

---

## Bảo mật

### Mã hóa AES-128-CBC

- **Key**: Pre-Shared Key duy nhất cho toàn mạng: `key_x_1234567890` (16 byte).
- **IV**: 16 byte ngẫu nhiên cho mỗi gói tin, được gửi kèm trong payload hex.
- **Padding**: Zero-padding. ESP32: `memset(0)` trước khi mã hóa. Python server: `rstrip(b'\0')` sau khi giải mã.
- **Hiệu năng**: Sử dụng hardware accelerator trên ESP32 (mbedtls), thời gian mã hóa ~17 micro giây.

### Chống tấn công Replay

- Mỗi gói tin JSON chứa trường `seq` (uint32).
- Khi Xi khởi động, chọn ngẫu nhiên `seq = 1000 + random(9000)` để tránh bị lợi dụng khi reset nhiều lần.
- Server lưu `last_seq` cho từng thiết bị trong bảng `devices`.
- Server từ chối gói tin nếu `seq <= last_seq`.

### Giải thích lựa chọn bảo mật

> Yêu cầu của thầy: "Mạng IoT này mục đích chính là truyền tin, yêu cầu nhanh, đơn giản nhất, ít tốn tài nguyên nhất, mức độ bảo mật không quá cao."

AES-128-CBC được chọn vì:
1. Có hardware accelerator trên ESP32 (mbedtls), rất nhanh và ít tốn RAM.
2. Thư viện có sẵn trong ESP32 Arduino core, không cần cài thêm.
3. Đủ mạnh cho mức bảo mật vừa phải (128-bit key, khối 16 byte).
4. Dùng chung một Pre-Shared Key giúp đơn giản hóa quản lý.

---

## Kiểm tra hệ thống

### Kiểm tra nhanh bằng script

Repository có kèm script kiểm tra nhanh server:

```bash
python server/main_test.py
```

Script này gửi một gói tin mẫu lên server và kiểm tra phản hồi HTTP 200.

### Quy trình kiểm tra đầy đủ

1. Chạy server: `python server/app.py`
2. Chạy dashboard: `streamlit run server/dashboard.py`
3. Gửi dữ liệu mẫu (dùng script test hoặc curl):

```bash
curl -X POST http://127.0.0.1:5000/receive-data ^
  -H "Content-Type: application/json" ^
  -d "{\"payload\":\"<hex_64_ky_tu>\"}"
```

4. Kiểm tra dashboard tại `http://localhost:8501` — xem bản đồ có hiển thị điểm mới và biểu đồ cập nhật.

### Kiểm tra bằng Wokwi

Xem hướng dẫn ở phần [Chạy mô phỏng Wokwi](#chay-mo-phong-wokwi). Khi Wokwi chạy và server được expose qua localtunnel, bạn sẽ thấy HTTP 200 trên Serial Monitor và dữ liệu xuất hiện trên dashboard.

---

## Cấu trúc thư mục

```
DATN--DoAnhQuan/
│
├── hardware/                        # Firmware ESP32 cho phần cứng thật
│   ├── xi_node/
│   │   └── xi_node.ino              # Firmware Xi node (T-Beam: BME280, MAX30102, GPS, LoRa, AES)
│   └── y_gateway/
│       └── y_gateway.ino            # Firmware Y Gateway (ESP32 + LoRa + WiFi forwarder)
│
├── server/                          # Phía Server
│   ├── app.py                       # Flask server: nhận payload, AES giải mã, chống replay, SQLite
│   ├── init_db.py                   # Khởi tạo database và thêm thiết bị mẫu
│   ├── dashboard.py                 # Streamlit dashboard: bản đồ Leaflet, biểu đồ, danh sách thiết bị
│   ├── main_test.py                 # Script test nhanh (gửi 2 gói mẫu, kiểm tra HTTP 200)
│   └── xor_cipher.py                # Tham khảo: mã hóa XOR đơn giản
│
├── wokwi/                           # File mô phỏng Wokwi (copy-paste lên wokwi.com)
│   ├── sketch.ino                   # Code ESP32 mô phỏng (WiFi + OLED + AES + HTTP)
│   ├── diagram.json                 # Sơ đồ kết nối (ESP32 + OLED SSD1306)
│   ├── wokwi.toml                   # Cấu hình dự án Wokwi
│   ├── wokwi_to_copy.md             # Hướng dẫn copy-paste chi tiết
│   ├── sketch_minimal.ino           # Phiên bản tối giản để debug
│   └── libraries.txt                # Danh sách thư viện Wokwi cần thiết
│
├── docs/                            # Tài liệu dự án
│   ├── thesis.md                    # Đề tài đầy đủ (mô tả ngữ cảnh, nội dung công việc)
│   ├── workflow.md                  # Kiến trúc hệ thống, thiết kế chi tiết
│   ├── threat_model.md              # Mô hình mối đe dọa
│   ├── references.md                # Tài liệu tham khảo
│   ├── research_aes_gcm.md          # Nghiên cứu AES-GCM
│   ├── research_anti_replay.md      # Nghiên cứu chống replay
│   ├── research_hmac_auth.md        # Nghiên cứu HMAC authentication
│   └── research_performance.md      # Nghiên cứu hiệu năng
│
├── guides/                          # Hướng dẫn viết báo cáo
│   ├── writing_outline.md           # Bố cục bài viết (phân công Hoàng + Quân)
│   └── teky_install.md              # Hướng dẫn mua linh kiện tại Tế Ky
│
├── plan/                            # Kế hoạch thực hiện
│   └── perf_plan.md                 # Kế hoạch tối ưu hiệu năng
│
├── .opencode/
│   └── skills/
│       ├── iot-datn/SKILL.md        # Cấu hình context dự án cho opencode
│       └── iot-security/...         # Skill bảo mật IoT (có sẵn)
│
├── requirements.txt                 # Danh sách thư viện Python
├── opencode.json                    # Cấu hình opencode project
├── .gitignore                       # Git ignore rules
└── README.md                        # File này
```

---

## Các vấn đề thường gặp

### Lỗi khi chạy

| Vấn đề | Nguyên nhân | Cách khắc phục |
|--------|-------------|----------------|
| Wokwi VS Code extension boot loop | Extension không ổn định | Dùng Wokwi web thay vì VS Code extension |
| WiFi trên Wokwi không kết nối | Timeout ngắn, thiếu WiFi.mode | Code đã fix (timeout 80 lần, thêm WiFi.mode(WIFI_STA)) |
| HTTP -1 (connection refused) | Localtunnel chưa chạy hoặc URL sai | Chạy `lt --port 5000`, cập nhật SERVER_URL trong sketch.ino |
| HTTP 403 "Decryption Failed" | mbedtls ghi đè biến iv | Dùng iv_copy để lưu IV gốc (đã fix) |
| HTTP 403 "Device not found" | Sai case: XI_01 vs Xi_01 | Dùng đúng `Xi_01` (đã đồng bộ) |
| HTTP 403 "Replay attack" | seq không tăng | Server kiểm tra seq > last_seq (đã fix bằng random seq mỗi boot) |
| Oled không hiển thị nội dung | Thiếu Wire.begin trước oled.begin | Đã thêm Wire.begin(21, 22) (cần test lại trên Wokwi) |

### Lưu ý khi phát triển

- **Pre-Shared Key** phải giống nhau giữa ESP32 và Server. Mặc định: `key_x_1234567890`.
- **Localtunnel** sinh URL khác nhau mỗi lần chạy. Nhớ cập nhật `SERVER_URL` trong `sketch.ino` trước khi copy lên Wokwi.
- **Database** nếu muốn reset, xóa file `iot_security.db` và chạy lại `python server/init_db.py`.
- **Dashboard** nếu không thấy dữ liệu, kiểm tra server log và database.

---

## Phân công công việc

### Tạ Huy Hoàng — Phần cứng và giao thức LoRa

1. Lắp ráp phần cứng IoT: ESP32, LoRa SX1278, GPS, cảm biến.
2. Nghiên cứu LoRa và phương thức truyền tin.
3. Thử nghiệm gửi/nhận LoRa giữa Xi và Y.
4. Thiết kế gói tin Beacon và ACK.
5. Viết code Xi gửi Beacon, chờ ACK. Viết code Y quét Beacon.
6. Viết code Xi đọc cảm biến và GPS.
7. Viết code Xi gửi dữ liệu cho Y.
8. Viết code Y chuyển tiếp dữ liệu lên Server qua WiFi/4G.

### Đỗ Anh Quân — Mã hóa, Server và Dashboard

1. Nghiên cứu mã hóa dữ liệu IoT (AES-128-CBC).
2. Thiết kế kiến trúc hệ thống (Xi, Y, Server) và luồng dữ liệu.
3. Thiết kế cấu trúc gói tin từ Xi đến Server.
4. Viết code mã hóa (ESP32) và giải mã (Python).
5. Tích hợp mã hóa vào Gateway.
6. Xây dựng Flask Server nhận JSON từ Gateway.
7. Viết code Server tổng hợp và lưu SQLite.
8. Thiết lập Web Map (OpenStreetMap + Leaflet) hiển thị vị trí thiết bị.

---

## Giấy phép

Đồ án tốt nghiệp — Trường Đại học XXX (thông tin bổ sung sau).
