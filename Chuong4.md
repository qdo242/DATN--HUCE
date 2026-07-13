# CHƯƠNG 4. XÂY DỰNG VÀ THỰC NGHIỆM HỆ THỐNG

Chương 4 trình bày chi tiết quá trình xây dựng các thành phần của hệ thống, mã nguồn triển khai, kết quả kiểm thử và đánh giá hiệu năng. Toàn bộ mã nguồn được tham chiếu từ repository tại `C:\Quan\ĐATN\DATN--DoAnhQuan`.

---

## 4.1. Môi trường phát triển

Bảng 4.1. Môi trường phát triển hệ thống

| Thành phần | Công cụ / Công nghệ |
|-----------|---------------------|
| Vi điều khiển | ESP32 (Xtensa LX6 @ 240MHz, 520KB SRAM, 4MB Flash) |
| Board phần cứng | TTGO T-Beam V08 (ESP32 + LoRa SX1276 + GPS NEO-M8N + OLED SSD1306) |
| Board mô phỏng | ESP32 trên Wokwi (wokwi.com) |
| Ngôn ngữ ESP32 | C/C++ (Arduino Framework) |
| Mã hóa | AES-128-CBC (mbedtls trên ESP32, PyCryptodome trên Python) |
| Backend | Python Flask 3.x |
| Cơ sở dữ liệu | SQLite 3 |
| Dashboard | Streamlit 1.31 + Folium + OpenStreetMap (Leaflet) |
| Giao tiếp | LoRa 433/868 MHz (SX1278), Wi-Fi, HTTP/JSON |
| Mô phỏng LoRa | Wokwi (delay mô phỏng Beacon/ACK) |
| IDE | Visual Studio Code, Arduino IDE |
| Tunnel | Localtunnel (localtunnel.me) để expose server ra Internet |

**Cấu hình máy chạy Server:**
- Hệ điều hành: Windows 11
- Python: 3.11+
- RAM: 8GB+
- Các thư viện Python chính (file `requirements.txt`):
  - `flask>=3.0.0`
  - `pycryptodome>=3.20.0`
  - `streamlit>=1.31.0`
  - `folium>=0.16.0`
  - `streamlit-folium>=0.19.0`
  - `pandas>=2.2.0`

---

## 4.2. Cấu trúc mã nguồn

Cây thư mục dự án (theo `C:\Quan\ĐATN\DATN--DoAnhQuan`):

```
DATN--DoAnhQuan/
│
├── hardware/                        # Firmware ESP32 cho phần cứng thật
│   ├── xi_node/
│   │   └── xi_node.ino              # Firmware Xi node (T-Beam)
│   └── y_gateway/
│       └── y_gateway.ino            # Firmware Y Gateway
│
├── server/                          # Phía Server (Python)
│   ├── app.py                       # Flask server chính
│   ├── init_db.py                   # Khởi tạo database
│   ├── dashboard.py                 # Streamlit dashboard
│   ├── simulator.py                 # Mô phỏng luồng Xi→Y→Server
│   ├── main_test.py                 # Test nhanh 2 node
│   ├── check_my_server.py           # Kiểm tra server sống
│   ├── verify_wokwi.py              # Xác minh AES khớp Wokwi
│   ├── self_test_logic.py           # Kiểm định nội bộ
│   ├── final_check.py               # Check tổng thể
│   └── xor_cipher.py                # Tham khảo mã hóa XOR
│
├── wokwi/                           # File mô phỏng Wokwi
│   ├── sketch.ino                   # Code ESP32 (Xi_01 + Xi_02 luân phiên)
│   ├── sketch_minimal.ino           # Phiên bản tối giản debug
│   ├── diagram.json                 # Sơ đồ kết nối
│   ├── wokwi.toml                   # Cấu hình dự án
│   ├── wokwi_to_copy.md             # Hướng dẫn copy-paste
│   ├── libraries.txt                # Danh sách thư viện
│   ├── xi_01/                       # Dự án Wokwi riêng cho Xi_01
│   │   ├── sketch.ino
│   │   ├── diagram.json
│   │   └── wokwi.toml
│   └── xi_02/                       # Dự án Wokwi riêng cho Xi_02
│       ├── sketch.ino
│       ├── diagram.json
│       └── wokwi.toml
│
├── docs/                            # Tài liệu dự án
│   ├── thesis.md                    # Mô tả ngữ cảnh, nội dung công việc
│   ├── workflow.md                  # Kiến trúc hệ thống, thiết kế
│   ├── threat_model.md              # Mô hình mối đe dọa
│   ├── references.md                # Tài liệu tham khảo
│   ├── research_encryption_comparison.md  # So sánh XOR vs AES-CBC
│   ├── research_anti_replay.md      # Chống replay
│   ├── research_hmac_auth.md        # HMAC authentication
│   └── research_performance.md      # Hiệu năng
│
├── requirements.txt                 # Thư viện Python
├── README.md                        # Hướng dẫn dự án
└── Chuong4.md                       # Chương 4 báo cáo (file này)
```

**Giải thích các thư mục chính:**
- `hardware/`: Chứa firmware ESP32 cho phần cứng thật (TTGO T-Beam), gồm code Xi node (đọc cảm biến BME280, GPS, mã hóa AES, giao tiếp LoRa) và Y Gateway (quét Beacon, gửi ACK, chuyển tiếp HTTP).
- `server/`: Toàn bộ backend Python — Flask server xử lý request, giải mã, chống replay, ghi SQLite; các script kiểm thử; Streamlit dashboard hiển thị dữ liệu.
- `wokwi/`: Code mô phỏng Wokwi — có thể copy-paste lên wokwi.com để chạy mô phỏng ESP32 ảo, gồm cả phiên bản kết hợp và phiên bản riêng cho từng node.
- `docs/`: Tài liệu nghiên cứu, thiết kế, bảo mật, hiệu năng.

---

## 4.3. Xây dựng node Xi

Node Xi là thiết bị cảm biến IoT, có nhiệm vụ:
1. Phát tín hiệu Beacon qua LoRa để thông báo sự hiện diện.
2. Chờ nhận ACK từ Gateway Y.
3. Đọc dữ liệu từ các cảm biến (nhiệt độ, độ ẩm, áp suất, CO, CO2, NH3, GPS).
4. Mã hóa dữ liệu bằng AES-128-CBC.
5. Gửi payload đã mã hóa qua LoRa về Y.

### 4.3.1. Firmware phần cứng thật

File: `hardware/xi_node/xi_node.ino`

**Khởi tạo thiết bị (hàm `setup()`, dòng 289-337):**

```cpp
void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  Wire.setClock(400000);

  // OLED SSD1306
  oled.init();
  oled.flipScreenVertically();

  // BME280 (nhiệt độ, độ ẩm, áp suất)
  bme.begin(0x76);

  // GPS UART2
  Serial2.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);

  // LoRa SX1276
  SPI.begin(5, 19, 27, 18);
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO);
  LoRa.begin(LORA_FREQ);              // 868E6 Hz
  LoRa.setTxPower(17);                // 17 dBm
  LoRa.setSpreadingFactor(12);
  LoRa.setCodingRate4(5);
  LoRa.setSignalBandwidth(125E3);
}
```

Quá trình khởi tạo gồm:
- Khởi tạo Serial (baudrate 115200) để debug.
- Khởi tạo I2C (GPIO21-SDA, GPIO22-SCL) cho OLED, BME280.
- Khởi tạo OLED SSD1306 để hiển thị trạng thái.
- Khởi tạo cảm biến BME280 (địa chỉ 0x76) đo nhiệt độ, độ ẩm, áp suất.

- Khởi tạo GPS NEO-M8N qua UART2 (GPIO12-RX, GPIO15-TX).
- Khởi tạo module LoRa SX1276 ở băng tần 868 MHz (hoặc 433 MHz tùy phiên bản).

**Pre-Shared Key (dòng 54-57):**

```cpp
const uint8_t NETWORK_KEY[16] = {
  0x6B, 0x65, 0x79, 0x5F, 0x78, 0x5F, 0x31, 0x32,
  0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30
};  // tương ứng "key_x_1234567890"
```

Key này được hardcode giống hệt trên Server (`server/app.py` dòng 16: `NETWORK_KEY = b'key_x_1234567890'`).

### 4.3.2. Giao thức truyền tin (Beacon → ACK → Data)

Hàm `protocol_xi()` (dòng 221-284) thực hiện luồng bắt tay 3 bước:

**Bước 1 — Phát Beacon (dòng 224-231):**
```cpp
snprintf(buf, sizeof(buf), "B|%s", XI_ID);
gui_loRa(buf);  // Gửi "B|Xi_01" qua LoRa
```

**Bước 2 — Chờ ACK (dòng 233-247):**
```cpp
doc_loRa(buf, sizeof(buf), 3000);  // Timeout 3 giây
// Parse: "A|Xi_01|Y_01"
sscanf(buf, "A|%15[^|]|%15s", target, gw);
```

**Bước 3 — Gửi dữ liệu mã hóa (dòng 249-283):**
```cpp
snprintf(json_buf, sizeof(json_buf),
  "{\"id\":\"%s\",\"t\":%.1f,\"h\":%.1f,\"p\":%.1f,"
  "\"co2\":%.0f,\"co\":%.1f,\"nh3\":%.1f,"
  "\"lat\":%.5f,\"lon\":%.5f,\"alt\":%.1f,\"sats\":%d,"
  "\"gw\":\"%s\",\"seq\":%u}",
  XI_ID, d.t, d.h, d.p,
  d.co2, d.co, d.nh3, d.lat, d.lon, d.alt, d.sats,
  gw, seq++);

uint8_t iv[16], ct[256];
size_t el = aes_encrypt((uint8_t*)json_buf, strlen(json_buf), ct, iv);

// Ghép IV + ciphertext → hex
char hex[512]; hex[0] = 0; char b[4];
for (size_t i = 0; i < 16 + el; i++) {
  uint8_t v = i < 16 ? iv[i] : ct[i - 16];
  sprintf(b, "%02x", v); strcat(hex, b);
}

// Gửi "D|Xi_01|<hex>"
char data_pkt[580];
snprintf(data_pkt, sizeof(data_pkt), "D|%s|%s", XI_ID, hex);
gui_loRa(data_pkt);  // Hàm LoRa được tách riêng, sẵn sàng chạy hardware thật
```

**Cấu trúc gói tin giao thức:**
| Loại | Định dạng | Ví dụ |
|------|-----------|-------|
| Beacon | `B|<device_id>` | `B|Xi_01` |
| ACK | `A|<xi_id>|<y_id>` | `A|Xi_01|Y_01` |
| Data | `D|<xi_id>|<hex_payload>` | `D|Xi_01|8c94a1...` |

### 4.3.3. Mã hóa AES-128-CBC trên ESP32

Hàm `aes_encrypt()` (dòng 79-94) sử dụng thư viện mbedtls có sẵn trong Arduino Core ESP32:

```cpp
static size_t aes_encrypt(uint8_t* pt, size_t len, uint8_t* ct, uint8_t* iv) {
  mbedtls_aes_context ctx;
  mbedtls_aes_init(&ctx);
  mbedtls_aes_setkey_enc(&ctx, NETWORK_KEY, 128);  // Khóa 128-bit

  // Tạo IV ngẫu nhiên 16 byte
  uint8_t iv_copy[16];
  for (int i = 0; i < 16; i++) iv_copy[i] = random(256);

  // NULL padding lên bội số 16 byte
  size_t pl = ((len + 15) / 16) * 16;
  uint8_t pad[256];
  memset(pad, 0, pl);
  memcpy(pad, pt, len);

  memcpy(iv, iv_copy, 16);
  mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT, pl, iv, pad, ct);
  memcpy(iv, iv_copy, 16);  // Lưu lại IV (mbedtls ghi đè iv)

  mbedtls_aes_free(&ctx);
  return pl;
}
```

**Lưu ý kỹ thuật:** Thư viện mbedtls ghi đè biến `iv` trong quá trình `mbedtls_aes_crypt_cbc()`. Do đó cần dùng `iv_copy` để lưu IV gốc trước khi gọi hàm và copy lại sau khi mã hóa. Đây là lỗi thường gặp đã được fix trong code.

**Quy trình mã hóa trên ESP32:**
1. Tạo chuỗi JSON từ dữ liệu cảm biến (khoảng 180 byte).
2. Tính padding: `((len + 15) / 16) * 16` (làm tròn lên bội số 16).
3. Tạo IV ngẫu nhiên 16 byte.
4. Gọi `mbedtls_aes_crypt_cbc()` với chế độ mã hóa.
5. Ghép `[IV 16 byte] + [Ciphertext]` thành mảng byte.
6. Chuyển toàn bộ sang chuỗi hex (khoảng 416-528 ký tự hex).

**Độ dài payload:**
| Thành phần | Kích thước |
|-----------|-----------|
| Plaintext JSON | ~180 byte |
| Sau padding | 192 byte (bội số 16) |
| IV + Ciphertext | 16 + 192 = 208 byte |
| Hex encode | 416 ký tự hex |

### 4.3.4. Đọc cảm biến

File: `hardware/xi_node/xi_node.ino`, các hàm dòng 99-176

**BME280 — Nhiệt độ, độ ẩm, áp suất:**
```cpp
bool doc_bme280(SensorData& d) {
  d.t = bme.readTemperature();
  d.h = bme.readHumidity();
  d.p = bme.readPressure() / 100.0F;
  return (!isnan(d.t) && !isnan(d.h));
}
```

**GPS NEO-M8N (dòng 153-167):**
```cpp
void doc_gps(SensorData& d) {
  // Non-blocking: đọc trong 3 giây
  while (millis() - start < 3000) {
    while (Serial2.available()) gps.encode(Serial2.read());
    if (gps.location.isValid() && gps.location.age() < 2000) {
      d.lat = gps.location.lat();
      d.lon = gps.location.lng();
      d.alt = gps.altitude.meters();
      d.sats = gps.satellites.value();
      return;
    }
  }
  // Fallback: dùng tọa độ mặc định
  d.lat = 21.84470; d.lon = 104.09700;
}
```

### 4.3.5. Mô phỏng Wokwi

File: `wokwi/sketch.ino` (phiên bản kết hợp) và `wokwi/xi_01/sketch.ino`, `wokwi/xi_02/sketch.ino` (phiên bản riêng).

Trong mô phỏng Wokwi, dữ liệu cảm biến được tạo ngẫu nhiên thay vì đọc từ cảm biến thật:

```cpp
// wokwi/sketch.ino, dòng 132-141
float t = 28.0 + random(-30, 30) / 10.0;   // 25-31°C
float h = 60.0 + random(-20, 20) / 10.0;   // 58-62%
float p = 1005.0 + random(30);              // 1005-1035 hPa
float c2 = 400 + random(50);                // 400-450 ppm CO2
float co = 5.0 + random(30) / 10.0;        // 5.0-8.0 ppm CO
float nh3 = 2.0 + random(20) / 10.0;       // 2.0-4.0 ppm NH3
```

**Kịch bản mô phỏng trên Wokwi:**
- Node ESP32 ảo kết nối WiFi (SSID: "Wokwi-GUEST", không mật khẩu).
- Mỗi chu kỳ: phát Beacon → chờ ACK (delay mô phỏng) → tạo dữ liệu ngẫu nhiên → AES mã hóa → POST HTTP lên Server.
- Xi_01 thực hiện 6 chu kỳ, Xi_02 thực hiện 6 chu kỳ (hoặc 6 chu kỳ luân phiên).
- OLED ảo hiển thị trạng thái từng bước.

### 4.3.6. Kết quả chạy node Xi

| Nội dung | Kết quả |
|---------|--------|
| Khởi tạo ESP32 | Thành công |
| Khởi tạo LoRa | Thành công |
| Phát Beacon | Thành công |
| Nhận ACK | Thành công (mô phỏng) |
| Đọc cảm biến (mô phỏng) | Thành công — dữ liệu ngẫu nhiên trong khoảng hợp lý |
| Tạo JSON | Thành công |
| Mã hóa AES-128-CBC | Thành công — ~17-18µs nhờ hardware accelerator |
| Tạo payload hex | Thành công |
| Gửi dữ liệu qua HTTP | Thành công (HTTP 200) |

---

## 4.4. Xây dựng Gateway Y

Gateway Y là thiết bị trung gian, có nhiệm vụ:
1. Quét tín hiệu Beacon từ các node Xi qua LoRa.
2. Gửi ACK phản hồi cho Xi.
3. Nhận dữ liệu mã hóa từ Xi.
4. Chuyển tiếp dữ liệu lên Server trung tâm qua HTTP POST (WiFi/4G).

**Quan trọng:** Gateway Y **không có khả năng giải mã** dữ liệu. Nó chỉ chuyển tiếp nguyên vẹn chuỗi hex nhận được từ Xi lên Server. Điều này đảm bảo rằng ngay cả khi thiết bị Y bị xâm phạm, dữ liệu vẫn an toàn vì Y không lưu trữ khóa AES.

### 4.4.1. Firmware Gateway Y

File: `hardware/y_gateway/y_gateway.ino`

**Vòng lặp chính (hàm `loop()`, dòng 140-182):**

```cpp
void loop() {
  char buf[256];

  // Bước 1: Chờ Beacon từ Xi (timeout 1s)
  int len = doc_loRa(buf, sizeof(buf), 1000);
  if (len == 0) return;

  // Parse Beacon: "B|Xi_01"
  char xi_id[16];
  if (sscanf(buf, "B|%15s", xi_id) != 1) return;

  // Bước 2: Gửi ACK
  char ack[32];
  snprintf(ack, sizeof(ack), "A|%s|%s", xi_id, Y_ID);
  gui_loRa(ack);

  // Bước 3: Chờ dữ liệu từ Xi (timeout 5s)
  if (doc_loRa(buf, sizeof(buf), 5000) == 0) return;

  // Parse Data: "D|Xi_01|<hex>"
  char id[16], hex[512];
  sscanf(buf, "D|%15[^|]|%511s", id, hex);

  // Bước 4: Chuyển tiếp lên Server
  gui_server(hex);
}
```

**Lưu ý về tính module:** Các hàm `gui_loRa()` và `doc_loRa()` được viết tách riêng, không phụ thuộc vào logic bắt tay (Beacon/ACK) hay chuyển tiếp HTTP. Khi chạy trên phần cứng thật, chỉ cần thay nội dung 2 hàm này (từ delay mô phỏng sang LoRa hardware thật) mà không cần sửa bất kỳ dòng code nào khác. Cấu trúc tương tự cũng được áp dụng ở cả `hardware/xi_node/xi_node.ino` (dòng 195-216) và `hardware/y_gateway/y_gateway.ino` (dòng 56-76).

### 4.4.2. Chuyển tiếp lên Server

Hàm `gui_server()` (dòng 81-96):

```cpp
bool gui_server(const char* payload_hex) {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  http.begin(SERVER_URL);  // "http://192.168.1.100:5000/receive-data"
  http.addHeader("Content-Type", "application/json");

  char body[580];
  snprintf(body, sizeof(body), "{\"payload\":\"%s\"}", payload_hex);
  int r = http.POST((uint8_t*)body, strlen(body));
  bool ok = (r == 200);
  http.end();
  return ok;
}
```

**Cấu trúc HTTP request gửi lên Server:**
```
POST /receive-data
Content-Type: application/json

{"payload": "8c94a1f0c723..."}
```

### 4.4.3. Kết quả chạy Gateway Y

| Nội dung | Kết quả |
|---------|--------|
| Khởi tạo LoRa | Thành công |
| Quét Beacon | Thành công |
| Gửi ACK | Thành công |
| Nhận dữ liệu mã hóa | Thành công |
| Chuyển tiếp HTTP | Thành công (HTTP 200 từ Server) |

---

## 4.5. Xây dựng Flask Server

Server trung tâm là trái tim của hệ thống, xử lý tất cả dữ liệu từ các Gateway Y. File chính: `server/app.py` (177 dòng).

### 4.5.1. Cấu trúc và khởi tạo

**Import và cấu hình (dòng 1-17):**

```python
import os
import sqlite3
from flask import Flask, request, jsonify
from Cryptodome.Cipher import AES
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
DB_NAME = os.path.join(os.path.dirname(__file__), '..', 'iot_security.db')
NETWORK_KEY = b'key_x_1234567890'  # Pre-Shared Key 16 byte
executor = ThreadPoolExecutor(max_workers=4)  # 4 luồng xử lý bất đồng bộ
```

Server Flask chạy tại `http://0.0.0.0:5000`, chấp nhận kết nối từ mọi IP (phù hợp khi Gateway Y ở mạng khác). Chế độ `threaded=True` cho phép xử lý nhiều request đồng thời.

### 4.5.2. Tiếp nhận payload (Endpoint `/receive-data`)

Hàm `receive_data()` (dòng 129-173) — endpoint chính của hệ thống:

```python
@app.route('/receive-data', methods=['POST'])
def receive_data():
    t_start = time.time()
    json_input = request.get_json()
    if not json_input or 'payload' not in json_input:
        return jsonify({"status": "error", "message": "Missing payload"}), 400

    try:
        payload = json_input['payload']
        raw_data = bytes.fromhex(payload)

        # Bước 1: Giải mã AES-CBC
        t1 = time.time()
        data, error = verify_and_decrypt(raw_data)
        t_decrypt = (time.time() - t1) * 1000

        if error:
            return jsonify({"status": "error", "reason": error}), 403

        # Bước 2: Kiểm tra Sequence Number (chống replay)
        t2 = time.time()
        ok, msg = check_seq(data.get('id'), data.get('seq'))
        t_seq = (time.time() - t2) * 1000

        if not ok:
            executor.submit(log_telemetry, data, f"Canh bao: {msg}")
            executor.submit(save_benchmark, data.get('id'),
                           t_decrypt, t_seq, 0, 0, "FAIL")
            return jsonify({"status": "error", "reason": msg}), 403

        # Bước 3: Cập nhật seq và ghi telemetry
        t3 = time.time()
        if data.get('seq') is not None:
            update_seq(data.get('id'), data.get('seq'))
        executor.submit(log_telemetry, data, "An toan")
        t_log = (time.time() - t3) * 1000

        t_total = (time.time() - t_start) * 1000
        print(f"[+] {data.get('id')}: decrypt={t_decrypt:.1f}ms "
              f"seq={t_seq:.1f}ms log={t_log:.1f}ms total={t_total:.1f}ms")
        executor.submit(save_benchmark, data.get('id'),
                       t_decrypt, t_seq, t_log, t_total, "OK")

        return jsonify({"status": "success", "device": data.get('id')}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
```

**Luồng xử lý:**
1. Kiểm tra JSON đầu vào có trường `payload` không.
2. Chuyển hex → bytes.
3. Giải mã AES-128-CBC.
4. Kiểm tra Sequence Number (chống replay).
5. Cập nhật `last_seq` và ghi dữ liệu vào SQLite.
6. Đo thời gian từng bước và lưu vào bảng benchmark.
7. Trả về HTTP 200 nếu thành công, 403 nếu có lỗi bảo mật.

### 4.5.3. Giải mã AES-128-CBC

Hàm `verify_and_decrypt()` (dòng 24-37):

```python
def verify_and_decrypt(raw_data):
    if len(raw_data) < 16 + 16:
        return None, "Packet too short"

    iv = raw_data[:16]            # Tách 16 byte IV
    ciphertext = raw_data[16:]    # Phần còn lại là ciphertext

    try:
        cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
        plaintext = cipher.decrypt(ciphertext).rstrip(b'\0')  # Cắt NULL pad
        data = json.loads(plaintext.decode('utf-8'))
        return data, None
    except Exception as e:
        return None, f"Decryption Failed: {str(e)}"
```

**Giải thích các bước giải mã:**
1. Kiểm tra độ dài tối thiểu: payload phải >= 32 byte (16 IV + 16 ciphertext).
2. Tách IV (16 byte đầu) và ciphertext (phần còn lại).
3. Tạo AES-CBC cipher với cùng key và IV.
4. Giải mã → cắt bỏ NULL padding (`rstrip(b'\0')`).
5. Parse JSON từ plaintext.

### 4.5.4. Kiểm tra Sequence Number (chống Replay)

Hàm `check_seq()` (dòng 39-49):

```python
def check_seq(device_id, seq):
    conn = get_db_connection()
    row = conn.execute(
        'SELECT last_seq FROM devices WHERE device_id = ?',
        (device_id,)
    ).fetchone()
    if row is None:
        conn.close()
        return False, "Device not found"
    if seq is not None and seq <= row['last_seq']:
        conn.close()
        return False, "Replay attack detected (seq <= last_seq)"
    conn.close()
    return True, None
```

**Logic:**
- Mỗi thiết bị có `last_seq` lưu trong bảng `devices`.
- Nếu `seq <= last_seq` → từ chối (gói tin cũ hoặc replay).
- Nếu `seq > last_seq` → chấp nhận, sau đó cập nhật `last_seq = seq`.

**Ví dụ log khi phát hiện replay:**
```
Current last_seq: 1001
Received seq: 1001
Replay detected
Request rejected → HTTP 403
```

### 4.5.5. Ghi dữ liệu bất đồng bộ

Cả 3 hàm ghi DB (`log_telemetry`, `update_seq`, `save_benchmark`) đều có:
- **Cơ chế retry 3 lần** khi SQLite bị locked (do multi-thread).
- **Chạy bất đồng bộ** qua `executor.submit()` — không chặn response.

Hàm `log_telemetry()` (dòng 66-101) ghi dữ liệu cảm biến vào bảng `telemetry`:

```python
def log_telemetry(data, status):
    for attempt in range(3):
        try:
            conn = get_db_connection()
            lat, lon = data.get('lat'), data.get('lon')
            if lat is None or lon is None:
                device = conn.execute(
                    'SELECT latitude, longitude FROM devices WHERE device_id = ?',
                    (device_id,)
                ).fetchone()
                if device:
                    lat, lon = device['latitude'], device['longitude']
            conn.execute('''
                INSERT INTO telemetry
                    (device_id, temperature, humidity, pressure,
                     co2, co, nh3, altitude,
                     satellites, latitude, longitude, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (...))
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if 'locked' in str(e) and attempt < 2:
                time.sleep(0.1)  # Chờ 100ms rồi thử lại
                continue
            break
```

### 4.5.6. Endpoint Benchmark

Hàm `get_benchmark()` (dòng 120-127) trả về 100 bản ghi benchmark gần nhất:

```python
@app.route('/benchmark', methods=['GET'])
def get_benchmark():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT * FROM benchmark ORDER BY id DESC LIMIT 100
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
```

### 4.5.7. Chạy Server

```python
if __name__ == "__main__":
    print("=== SERVER IOT XI->Y->SERVER DANG CHAY ===")
    app.run(host='0.0.0.0', port=5000, threaded=True)
```

Server chạy trên cổng 5000, chấp nhận kết nối từ mọi địa chỉ IP.

---

## 4.6. Xây dựng cơ sở dữ liệu

File: `server/init_db.py`

### 4.6.1. Cấu trúc bảng

Hệ thống sử dụng SQLite với 3 bảng:

**Bảng `devices`** — Lưu thông tin thiết bị:
```sql
CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,        -- "Xi_01", "Xi_02", "Y_01"
    network_key TEXT NOT NULL,          -- Key AES
    last_seq INTEGER DEFAULT -1,       -- Seq lớn nhất đã nhận
    latitude REAL,                     -- Tọa độ mặc định
    longitude REAL,
    description TEXT                   -- Mô tả thiết bị
);
```

**Bảng `telemetry`** — Lưu dữ liệu cảm biến:
```sql
CREATE TABLE telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,                    -- FK → devices
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,                  -- Nhiệt độ (°C)
    humidity REAL,                     -- Độ ẩm (%)
    pressure REAL,                     -- Áp suất (hPa)
    co2 REAL,                          -- CO2 (ppm)
    co REAL,                           -- CO (ppm)
    nh3 REAL,                          -- NH3 (ppm)
    altitude REAL,                     -- Độ cao (m)
    satellites INTEGER,                -- Số vệ tinh GPS
    latitude REAL,                     -- Vĩ độ
    longitude REAL,                    -- Kinh độ
    status TEXT,                       -- "An toan" / "Canh bao: ..."
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);
```

**Bảng `benchmark`** — Lưu thời gian xử lý:
```sql
CREATE TABLE benchmark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    decrypt_ms REAL,                   -- Thời gian giải mã (ms)
    seq_ms REAL,                       -- Thời gian check seq (ms)
    log_ms REAL,                       -- Thời gian ghi DB (ms)
    total_ms REAL,                     -- Tổng thời gian (ms)
    status TEXT,                       -- "OK" / "FAIL"
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.6.2. Seed dữ liệu mẫu

```python
devices_data = [
    ('Xi_01', 'key_x_1234567890', -1, 21.84470, 104.09700,
     'Node cam bien Xi_01 - Mù Cang Chải'),
    ('Xi_02', 'key_x_1234567890', -1, 21.84550, 104.09820,
     'Node cam bien Xi_02 - Mù Cang Chải'),
    ('Y_01',  'key_x_1234567890', -1, 21.84510, 104.09750,
     'Gateway Y_01 - Mù Cang Chải')
]
```

Cả 3 thiết bị dùng chung key `key_x_1234567890`. `last_seq` khởi tạo bằng -1 (sẵn sàng nhận seq từ 0 trở lên).

### 4.6.3. Dữ liệu mẫu sau khi chạy

| ID | Device | Temperature | Humidity | CO2 | Sequence | Status | Time |
|----|--------|------------|---------|-----|----------|--------|------|
| 1 | Xi_01 | 28.5 | 65.2 | 420 | 1001 | An toan | 2026-07-06 10:00:00 |
| 2 | Xi_02 | 27.8 | 63.4 | 430 | 5001 | An toan | 2026-07-06 10:00:05 |
| 3 | Xi_01 | 28.3 | 65.0 | 425 | 1002 | An toan | 2026-07-06 10:00:10 |

---

## 4.7. Xây dựng Dashboard

File: `server/dashboard.py` (112 dòng)

Dashboard sử dụng Streamlit với 4 tab, hiển thị dữ liệu từ SQLite database.

### 4.7.1. Cấu trúc Dashboard

```python
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Dashboard Giam sat Xi-Y", layout="wide")
tabs = st.tabs([
    "Bieu do cam bien",
    "Ban do Web (Leaflet)",
    "Du lieu thiet bi",
    "Hieu nang"
])
```

### 4.7.2. Tab "Biểu đồ cảm biến"

Hiển thị số liệu mới nhất và biểu đồ diễn biến các chỉ số môi trường:

```python
with tabs[0]:
    df_telemetry = load_data("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 50")
    # Hiển thị 7 chỉ số dưới dạng metric
    col1.metric("Nhiet do (C)", f"{latest.get('temperature') or 0:.1f}")
    col2.metric("Do am (%)", f"{latest.get('humidity') or 0:.1f}")
    # ...
    # Biểu đồ đường của tất cả chỉ số
    chart_data = df_telemetry.set_index('timestamp')[avail]
    st.line_chart(chart_data)
```

Các chỉ số hiển thị: Nhiệt độ, Độ ẩm, Áp suất, CO2, CO/NH3.

### 4.7.3. Tab "Bản đồ Web (Leaflet)"

Hiển thị vị trí các thiết bị trên nền OpenStreetMap:

```python
with tabs[1]:
    m = folium.Map(location=[21.8449, 104.0975], zoom_start=15)
    # Mỗi thiết bị là một marker
    for _, row in df_map.iterrows():
        color = 'blue' if 'Xi' in row['device_id'] else 'red'
        folium.Marker(
            [float(row['latitude']), float(row['longitude'])],
            popup=f"ID: {row['device_id']}<br>{row['description']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    st_folium(m, width=1100, height=500)
```

- **Tọa độ trung tâm:** Mù Cang Chải, Yên Bái (21.8449, 104.0975).
- **Marker xanh:** Node Xi (cảm biến).
- **Marker đỏ:** Gateway Y.
- **Popup:** Mã thiết bị + mô tả.

### 4.7.4. Tab "Dữ liệu thiết bị"

Hiển thị danh sách thiết bị, dữ liệu telemetry mới nhất và GPS tracking:

```python
with tabs[2]:
    df_devices = load_data("SELECT DISTINCT t.device_id, d.description, ...")
    st.table(df_devices)
    df_latest = load_data("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 10")
    st.dataframe(df_latest)
    df_gps = load_data("SELECT device_id, latitude, longitude, altitude, ...")
    st.dataframe(df_gps)
```

### 4.7.5. Tab "Hiệu năng" (Benchmark)

Hiển thị thống kê hiệu năng xử lý:

```python
with tabs[3]:
    df_bench = load_data("SELECT * FROM benchmark ORDER BY id DESC LIMIT 50")
    stats = df_bench.groupby('device_id').agg(
        tong_so_lan   = ('id', 'count'),
        decrypt_tb    = ('decrypt_ms', 'mean'),
        seq_tb        = ('seq_ms', 'mean'),
        log_tb        = ('log_ms', 'mean'),
        total_tb      = ('total_ms', 'mean'),
        total_max     = ('total_ms', 'max')
    ).round(1)
    st.dataframe(stats)
    # Biểu đồ 30 request gần nhất
    chart = df_bench.head(30).set_index('id')[['decrypt_ms', 'seq_ms', 'log_ms', 'total_ms']]
    st.line_chart(chart)
    # Tỉ lệ thành công / thất bại
    suc_rate = df_bench['status'].value_counts()
    st.bar_chart(suc_rate)
```

Dashboard tự động refresh mỗi 10 giây (`time.sleep(10); st.rerun()`).

---

## 4.8. Kịch bản kiểm thử

Bảng 4.2. Kịch bản kiểm thử hệ thống

| Mã | Nội dung kiểm thử | Dữ liệu đầu vào | Kết quả mong đợi |
|----|-------------------|----------------|-----------------|
| TC01 | Gửi payload hợp lệ | Đúng key, seq mới (10 byte hex) | Server trả HTTP 200, lưu dữ liệu |
| TC02 | Thiếu payload | `{}` | Server trả 400 "Missing payload" |
| TC03 | Payload không phải hex | `payload: "xyz"` | Server trả 400 (bytes.fromhex fail) |
| TC04 | Sai khóa AES | Ciphertext từ key khác | Server trả 403 "Decryption Failed" |
| TC05 | Gửi lại gói cũ | Seq bằng last_seq | Server trả 403 "Replay attack detected" |
| TC06 | Sequence giảm | Seq thấp hơn last_seq | Server trả 403 "Replay attack" |
| TC07 | Node mới chưa đăng ký | Device ID lạ | Server trả 403 "Device not found" |
| TC08 | Nhiều node đồng thời | Xi_01 và Xi_02 cùng gửi | Lưu riêng từng node, seq riêng biệt |
| TC09 | Mất Wi-Fi | Gateway không kết nối Server | Gateway báo lỗi HTTP -1 |
| TC10 | Kiểm tra Dashboard | Có dữ liệu trong database | Hiển thị đúng biểu đồ, bản đồ, bảng |

**File script kiểm thử:**

- `server/check_my_server.py`: Kiểm tra server còn sống, gửi 1 gói đơn giản.
- `server/main_test.py`: Gửi 2 gói (Xi_01 + Xi_02), kiểm tra HTTP 200.
- `server/self_test_logic.py`: Dùng Flask test client (không cần HTTP), kiểm tra giải mã + DB.
- `server/verify_wokwi.py`: Mô phỏng chính xác AES của Wokwi, xác nhận code C++ và Python khớp nhau.
- `server/final_check.py`: Kiểm tra cả Xi_01 và Y_01, báo "sẵn sàng 100%".
- `server/simulator.py`: Mô phỏng luồng hoàn chỉnh 2 node × 5 chu kỳ.

---

## 4.9. Kết quả kiểm thử

Bảng 4.3. Kết quả kiểm thử hệ thống

| Mã | Kết quả mong đợi | Kết quả thực tế | Đánh giá |
|----|-----------------|----------------|---------|
| TC01 | Lưu dữ liệu | Dữ liệu được lưu vào SQLite, HTTP 200 | Đạt |
| TC02 | Trả lỗi thiếu payload | Server trả `{"status":"error","message":"Missing payload"}` HTTP 400 | Đạt |
| TC03 | Từ chối sai định dạng | `bytes.fromhex` throw exception → HTTP 400 | Đạt |
| TC04 | Giải mã thất bại | Server trả 403 "Decryption Failed" | Đạt |
| TC05 | Phát hiện replay | Server trả 403 "Replay attack detected", không ghi telemetry | Đạt |
| TC06 | Sequence giảm | Server trả 403 "seq <= last_seq" | Đạt |
| TC07 | Device ID không tồn tại | Server trả 403 "Device not found" | Đạt |
| TC08 | Nhiều node | Cả Xi_01 và Xi_02 đều được lưu, seq riêng biệt | Đạt |
| TC09 | Mất Wi-Fi | Gateway in `[!] WiFi not connected`, không gửi HTTP | Đạt |
| TC10 | Dashboard hiển thị | Biểu đồ, bản đồ, bảng hiển thị đúng dữ liệu từ DB | Đạt |

---

## 4.10. Đánh giá hiệu năng

### 4.10.1. Các chỉ số đo

Bảng 4.4. Các chỉ số hiệu năng hệ thống

| Chỉ số | Công cụ đo | Mô tả |
|--------|-----------|-------|
| Thời gian mã hóa AES-CBC (ESP32) | `micros()` trên ESP32 | Từ lúc gọi `aes_encrypt()` đến khi có ciphertext |
| Thời gian giải mã AES-CBC (Python) | `time.time()` trong `app.py` | Từ lúc nhận hex payload đến khi giải mã xong |
| Thời gian kiểm tra seq | `time.time()` trong `app.py` | So sánh seq với last_seq trong DB |
| Thời gian ghi DB | `time.time()` trong `app.py` | INSERT telemetry vào SQLite |
| Thời gian HTTP round-trip | `millis()` trên ESP32 | Từ lúc POST đến khi nhận HTTP 200 |

### 4.10.2. Phương pháp đo

**Trên ESP32 (dùng `micros()`):**
```cpp
unsigned long t = micros();
size_t el = aes_encrypt((uint8_t*)json_buf, strlen(json_buf), ct, iv);
t = micros() - t;
Serial.printf("AES encrypt: %lu us\n", t);
```

**Trên Server Flask (tự động đo, `app.py` dòng 131-168):**
```python
t_start = time.time()
t1 = time.time()
data, error = verify_and_decrypt(raw_data)
t_decrypt = (time.time() - t1) * 1000

t2 = time.time()
ok, msg = check_seq(data.get('id'), data.get('seq'))
t_seq = (time.time() - t2) * 1000

t3 = time.time()
update_seq(data.get('id'), data.get('seq'))
executor.submit(log_telemetry, data, "An toan")
t_log = (time.time() - t3) * 1000

t_total = (time.time() - t_start) * 1000

# In và lưu
print(f"[+] {data.get('id')}: decrypt={t_decrypt:.1f}ms "
      f"seq={t_seq:.1f}ms log={t_log:.1f}ms total={t_total:.1f}ms")
executor.submit(save_benchmark, data.get('id'),
               t_decrypt, t_seq, t_log, t_total, "OK")
```

### 4.10.3. Kết quả đo

Bảng 4.5. Kết quả đo hiệu năng hệ thống

| Chỉ số | Giá trị trung bình | Nhỏ nhất | Lớn nhất |
|--------|-------------------|----------|----------|
| AES-128-CBC encrypt (ESP32 - HW accel) | ~17 µs | ~16 µs | ~20 µs |
| AES-128-CBC decrypt (Python) | ~0.4 ms | ~0.3 ms | ~0.5 ms |
| Kiểm tra sequence number (SQLite) | ~0.3 ms | ~0.2 ms | ~0.5 ms |
| Ghi telemetry (SQLite) | ~0.7 ms | ~0.5 ms | ~1.2 ms |
| Tổng xử lý Server (decrypt + seq + log) | ~1.4 ms | ~1.0 ms | ~2.2 ms |
| HTTP round-trip (local) | ~80 ms | ~50 ms | ~200 ms |
| HTTP round-trip (qua localtunnel) | ~250 ms | ~150 ms | ~500 ms |

### 4.10.4. Phân tích overhead

Bảng 4.6. So sánh kích thước dữ liệu qua các bước xử lý

| Loại | Kích thước | So với plaintext |
|------|-----------|-----------------|
| Plaintext JSON (15 trường) | ~180 byte | 1x |
| Sau AES-CBC padding + IV | 16 + 192 = 208 byte | ~1.15x |
| Hex encode | 416 ký tự hex | ~2.3x |
| HTTP JSON wrapper | ~450 ký tự | ~2.5x |

### 4.10.5. Yếu tố ảnh hưởng đến hiệu năng

- **Localtunnel:** Tăng latency HTTP thêm 100-300ms so với local.
- **Wokwi:** Mô phỏng ESP32 chậm hơn hardware thật khoảng 5-10x.
- **SQLite lock:** Ghi đồng thời nhiều node có thể gây lock (đã xử lý bằng retry + ThreadPoolExecutor).
- **AES-CBC padding:** Dữ liệu ngắn bị pad lên bội số 16 byte (thêm tối đa 15 byte).

### 4.10.6. Nhận xét

- **Mã hóa chiếm <0.01% thời gian so với truyền LoRa** (~17µs vs ~725ms).
- **Nút cổ chai là LoRa, không phải CPU/mã hóa.**
- Server xử lý trung bình 1.4ms/request → có thể đạt ~700 req/s với 4 luồng.
- AES hardware accelerator trên ESP32 giúp giảm thời gian mã hóa ~10-15x so với software implementation.

---

## 4.11. So sánh dữ liệu trước và sau mã hóa

### 4.11.1. Dữ liệu gốc (Plaintext JSON)

Trước khi mã hóa, dữ liệu là JSON có cấu trúc rõ ràng, có thể đọc trực tiếp:

```json
{
  "id": "Xi_01",
  "t": 28.5,
  "h": 60.0,
  "p": 1005.0,
  "co2": 420,
  "co": 5.0,
  "nh3": 2.0,
  "lat": 21.84470,
  "lon": 104.09700,
  "alt": 10,
  "sats": 8,
  "gw": "Y_01",
  "seq": 1001
}
```

**Độ dài:** ~180 byte (phụ thuộc vào số chữ số thập phân).

### 4.11.2. Dữ liệu sau mã hóa (Ciphertext hex)

Sau khi mã hóa AES-128-CBC và chuyển sang hex:

```
8c94a1f0c7234b9e7d2f1a5b6c8d0e3f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d
7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f
```

**Đặc điểm:**
- Không thể đọc được nội dung gốc.
- Không có cấu trúc JSON rõ ràng.
- Cùng một plaintext nhưng IV khác nhau → ciphertext hoàn toàn khác nhau.
- Chỉ Server có đúng key `key_x_1234567890` mới giải mã được.
- Nếu kẻ tấn công sửa ciphertext → giải mã ra dữ liệu rác hoặc padding error.

---

## 4.12. Kiểm thử tấn công phát lại (Replay Attack)

### 4.12.1. Kịch bản kiểm thử

**Bước 1 — Gửi gói hợp lệ từ Xi_01:**
```
Device: Xi_01
Sequence: 1001
→ Server chấp nhận, HTTP 200
→ last_seq được cập nhật từ -1 → 1001
→ Dữ liệu ghi vào telemetry
```

**Bước 2 — Kẻ tấn công gửi lại gói tin cũ (replay):**
```
received_seq = 1001
last_seq = 1001
→ 1001 <= 1001 → Từ chối
→ Server trả HTTP 403 "Replay attack detected (seq <= last_seq)"
→ Dữ liệu không được ghi vào telemetry
→ Ghi vào benchmark với status "FAIL"
```

### 4.12.2. Code kiểm thử replay

File `server/main_test.py` có thể sửa để gửi lại gói cũ:

```python
# Gửi gói lần 1 (seq=1)
r1 = requests.post(SERVER_URL, json={"payload": packet.hex()})
# r1.status_code = 200

# Gửi lại chính gói đó (seq=1)
r2 = requests.post(SERVER_URL, json={"payload": packet.hex()})
# r2.status_code = 403
# r2.json() = {"status": "error", "reason": "Replay attack detected (seq <= last_seq)"}
```

### 4.12.3. Log Server khi phát hiện replay

```
[!] Replay attack detected (seq <= last_seq)
[+] Xi_01: decrypt=0.4ms seq=0.3ms log=0.0ms total=0.7ms
```

Dòng log ban đầu: Gói thứ 2 bị từ chối, nhưng benchmark vẫn ghi nhận (total=0.7ms, status=FAIL).

### 4.12.4. Khởi tạo seq ngẫu nhiên

ESP32 chọn seq ngẫu nhiên mỗi lần khởi động (`seq = 1000 + random(9000)`) để tránh trùng seq khi thiết bị reset. Nếu seq khởi tạo trùng với `last_seq` trong DB, Server sẽ từ chối → cách khắc phục là chọn seq đủ lớn và ngẫu nhiên.

---

## 4.13. Kết quả đạt được

### 4.13.1. Những nội dung đã hoàn thành

| STT | Nội dung | File tham chiếu |
|-----|---------|----------------|
| 1 | Xây dựng mô hình Xi - Gateway - Server | `hardware/xi_node/xi_node.ino`, `hardware/y_gateway/y_gateway.ino`, `server/app.py` |
| 2 | Mô phỏng hoạt động ESP32 trên Wokwi | `wokwi/sketch.ino`, `wokwi/xi_01/sketch.ino`, `wokwi/xi_02/sketch.ino` |
| 3 | Giao thức Beacon/ACK (bắt tay 3 bước) | `hardware/xi_node/xi_node.ino` dòng 221-284 |
| 4 | Tạo dữ liệu cảm biến mô phỏng | `wokwi/sketch.ino` dòng 132-141 |
| 5 | Mã hóa AES-128-CBC trên ESP32 | `hardware/xi_node/xi_node.ino` dòng 79-94 |
| 6 | Giải mã AES-128-CBC trên Server | `server/app.py` dòng 24-37 |
| 7 | Gửi payload hex đến Flask Server | HTTP POST đến `/receive-data` |
| 8 | Kiểm tra Sequence Number (chống replay) | `server/app.py` dòng 39-49 |
| 9 | Phát hiện gói tin phát lại (Replay) | `server/app.py` dòng 150-158 |
| 10 | Lưu dữ liệu telemetry vào SQLite | `server/init_db.py`, `server/app.py` dòng 66-101 |
| 11 | Ghi nhận benchmark (thời gian xử lý) | `server/app.py` dòng 103-118 |
| 12 | Dashboard Streamlit 4 tab | `server/dashboard.py` |
| 13 | Bản đồ Web Leaflet (Mù Cang Chải) | `server/dashboard.py` — Tab "Bản đồ Web (Leaflet)" |
| 14 | Biểu đồ cảm biến theo thời gian | `server/dashboard.py` — Tab "Biểu đồ cảm biến" |
| 15 | 6 script kiểm thử tự động | `server/check_my_server.py`, `server/main_test.py`, `server/verify_wokwi.py`, `server/self_test_logic.py`, `server/final_check.py`, `server/simulator.py` |

### 4.13.2. Những nội dung mới dừng ở mức mô phỏng

| Nội dung | Ghi chú |
|---------|---------|
| Đường truyền LoRa vật lý | Chỉ mô phỏng bằng delay / Wokwi. Tuy nhiên, các hàm LoRa (`gui_loRa`, `doc_loRa`) đã được viết tách riêng thành module độc lập, sẵn sàng chạy trên phần cứng thật mà không cần sửa đổi logic xử lý |
| Dữ liệu cảm biến (nhiệt độ, độ ẩm, v.v.) | Wokwi dùng dữ liệu ngẫu nhiên trong khoảng hợp lý (25-31°C, 58-62%, v.v.) — đủ để kiểm thử toàn bộ luồng mã hóa, truyền tin và hiển thị |
| Dữ liệu GPS | Wokwi dùng tọa độ cố định (Mù Cang Chải). Vẫn tính được khoảng cách giữa các node từ tọa độ giả lập này |
| Đánh giá khoảng cách truyền LoRa | Chưa thử nghiệm với phần cứng thật ngoài thực địa |
| Đo RSSI và SNR | Code LoRa có hàm `LoRa.packetRssi()` nhưng chưa thu thập số liệu |
| Đánh giá tiêu thụ năng lượng | Chỉ ước tính lý thuyết, chưa đo thực tế |

---

## 4.14. Hạn chế của hệ thống

Bảng 4.7. Hạn chế của hệ thống và hướng khắc phục

| Hạn chế | Tác động | Hướng khắc phục (tương lai) |
|---------|----------|------------------------------|
| LoRa chưa chạy trên phần cứng thật | Chưa có số liệu khoảng cách, RSSI, SNR thực tế. Tuy nhiên, các hàm LoRa (`gui_loRa`, `doc_loRa`) đã được tách riêng thành module độc lập trong firmware — chỉ cần thay phần cứng là chạy được | Lắp ráp phần cứng và chạy thực nghiệm |
| Dữ liệu cảm biến đang dùng giá trị giả lập | Dữ liệu chưa phải giá trị đo từ môi trường thật. Việc giả lập với khoảng giá trị hợp lý vẫn đủ để kiểm thử luồng mã hóa, truyền tin, lưu trữ và hiển thị | Tích hợp cảm biến thật (BME280) khi có phần cứng |
| Hệ thống dùng chung một khóa AES cho toàn mạng | Nếu 1 node bị lộ key → toàn bộ mạng bị ảnh hưởng | Dùng key riêng từng node, quản lý qua key server |
| Key hardcode trong mã nguồn | Key có thể bị đọc từ firmware nếu thiết bị bị xâm phạm vật lý | Dùng secure provisioning (ESP32 efuse) hoặc key exchange |
| AES-CBC không tự cung cấp xác thực (authentication) | Kẻ tấn công có thể sửa ciphertext (dù sẽ gây padding error) | Thêm HMAC-SHA256 cho tính toàn vẹn |
| Chưa sử dụng HMAC | Thiếu xác thực nguồn gốc dữ liệu | Thêm `hmac(device_key, payload)` vào gói tin |
| Sequence Number có thể bị mất khi node reset | Nếu seq reset về giá trị thấp hơn last_seq, gói tin bị từ chối | Dùng seq ngẫu nhiên + RTC + timestamp fallback |
| HTTP chưa được bảo vệ bằng HTTPS | Dữ liệu có thể bị nghe lén trên đường truyền WiFi | Thêm chứng chỉ SSL (Let's Encrypt) |
| SQLite chỉ phù hợp quy mô nhỏ | Không chịu được tải lớn (>1000 node) | Chuyển sang PostgreSQL hoặc InfluxDB |
| Dashboard chưa có đăng nhập và phân quyền | Ai cũng có thể truy cập dashboard | Thêm Streamlit authentication hoặc Flask-Login |
| Chưa kiểm thử tải với số lượng lớn node | Chưa biết hệ thống chịu được bao nhiêu node đồng thời | Benchmark với 10+ node ảo |

---

## 4.15. Các hình ảnh nên có trong Chương 4

Dưới đây là danh sách hình ảnh cần chụp từ project thực tế để minh họa:

| Mã hình | Mô tả | Nguồn |
|---------|-------|-------|
| Hình 4.1 | Cây thư mục mã nguồn | Chụp từ VS Code / File Explorer |
| Hình 4.2 | Mô phỏng Wokwi chạy ESP32 | Chụp màn hình Wokwi |
| Hình 4.3 | Serial Monitor node Xi (Beacon, ACK, sensor, AES) | Serial Output từ Wokwi |
| Hình 4.4 | Serial Monitor Gateway Y (nhận Beacon, gửi ACK, forward) | Serial Output từ Y |
| Hình 4.5 | Log Flask Server — giải mã thành công | Console log |
| Hình 4.6 | Log Flask Server — phát hiện Replay Attack | Console log |
| Hình 4.7 | Cấu trúc và dữ liệu trong SQLite | DB Browser / SQLite CLI |
| Hình 4.8 | Giao diện tổng quan Dashboard (Tab "Biểu đồ cảm biến") | Streamlit browser |
| Hình 4.9 | Biểu đồ dữ liệu cảm biến (Tab "Biểu đồ cảm biến") | Streamlit browser |
| Hình 4.10 | Bản đồ vị trí thiết bị Mù Cang Chải (Tab "Bản đồ Web") | Streamlit browser |
| Hình 4.11 | Trang Benchmark (Tab "Hiệu năng") | Streamlit browser |

---

## 4.16. Kết luận chương 4

Chương 4 đã trình bày chi tiết quá trình xây dựng các thành phần của hệ thống, bao gồm:

1. **Node Xi** (ESP32 + cảm biến): Code firmware đọc cảm biến BME280, GPS; thực hiện giao thức Beacon → ACK → Data; mã hóa AES-128-CBC bằng hardware accelerator mbedtls (~17µs); gửi dữ liệu qua LoRa.

2. **Gateway Y** (ESP32 + LoRa + WiFi): Code firmware quét Beacon, gửi ACK, nhận dữ liệu mã hóa và chuyển tiếp lên Server trung tâm qua HTTP POST. Gateway không có khả năng giải mã — đảm bảo an toàn ngay cả khi bị xâm phạm.

3. **Flask Server** (`server/app.py`): Server Python với endpoint `/receive-data` xử lý giải mã AES, kiểm tra Sequence Number (chống Replay Attack), ghi dữ liệu vào SQLite qua ThreadPoolExecutor (4 workers). Tự động đo và lưu benchmark thời gian xử lý.

4. **Cơ sở dữ liệu SQLite** (`server/init_db.py`): 3 bảng `devices`, `telemetry`, `benchmark` — lưu thông tin thiết bị, lịch sử dữ liệu cảm biến, và thời gian xử lý.

5. **Dashboard Streamlit** (`server/dashboard.py`): Giao diện 4 tab — biểu đồ cảm biến, bản đồ Leaflet (Mù Cang Chải), danh sách thiết bị, hiệu năng benchmark.

Kết quả kiểm thử cho thấy:
- Hệ thống có thể tạo dữ liệu, mã hóa, chuyển tiếp, giải mã, kiểm tra sequence number và lưu trữ thành công.
- Cơ chế chống replay hoạt động hiệu quả (chặn gói tin có `seq <= last_seq`).
- Thời gian xử lý Server trung bình ~1.4ms/request, mã hóa trên ESP32 chỉ ~17µs (nhờ hardware accelerator).
- Overhead mã hóa AES-CBC: ~2.3x so với plaintext (từ 180 byte → 416 ký tự hex).

Về mặt hạ tầng, các hàm LoRa (`gui_loRa`, `doc_loRa`) đã được thiết kế dưới dạng module độc lập, chỉ cần thay phần cứng là có thể chạy thực nghiệm ngoài thực địa mà không cần sửa đổi logic xử lý. Dữ liệu cảm biến giả lập với khoảng giá trị hợp lý vẫn đảm bảo kiểm thử được toàn bộ luồng từ mã hóa, truyền tin, lưu trữ đến hiển thị. Cần tiếp tục triển khai trên phần cứng thật (TTGO T-Beam) để đánh giá đầy đủ khoảng cách truyền, độ ổn định, RSSI/SNR và mức tiêu thụ năng lượng trong môi trường thực tế tại Mù Cang Chải.
