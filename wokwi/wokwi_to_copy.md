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

Cập nhật URL vào `SERVER_URL` trong code Wokwi trước khi copy.

### Terminal 3: Dashboard

```bash
python -m streamlit run server\dashboard.py
```

Mở `http://localhost:8501`.

---

## Cách chạy Wokwi

1. Vào https://wokwi.com → **New Project** → **ESP32**
2. Copy 3 file bên dưới vào Wokwi
3. Nhấn **Start Simulation**
4. Xem Serial Output + OLED hiển thị trạng thái

## `diagram.json`

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

## `wokwi.toml`

```toml
[wokwi]
version = 1
firmware = 'sketch.ino'
diagram = 'diagram.json'
```

## `sketch.ino`

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <mbedtls/aes.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// AES-128 key (16 bytes = "key_x_1234567890")
const uint8_t NETWORK_KEY[16] = {
  0x6B, 0x65, 0x79, 0x5F, 0x78, 0x5F, 0x31, 0x32,
  0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30
};
const char* XI_ID = "Xi_01";
const char* Y_ID  = "Y_01";
// THAY bang localtunnel URL cua ban
const char* SERVER_URL = "https://tasty-roses-unite.loca.lt/receive-data";

#define OLED_RESET -1
Adafruit_SSD1306 oled(128, 64, &Wire, OLED_RESET);

char json_buf[512];
uint32_t seq;
uint32_t cycles = 0;
float lat = 21.00355, lon = 105.84255;

// AES-128-CBC encrypt, tra ve do dai ciphertext
// QUAN TRONG: mbedtls ghi de bien iv => dung iv_copy de luu lai
static size_t aes_encrypt(uint8_t* pt, size_t len, uint8_t* ct, uint8_t* iv) {
  mbedtls_aes_context ctx;
  mbedtls_aes_init(&ctx);
  mbedtls_aes_setkey_enc(&ctx, NETWORK_KEY, 128);
  uint8_t iv_copy[16];
  for (int i = 0; i < 16; i++) iv_copy[i] = random(256);
  size_t pl = ((len + 15) / 16) * 16;
  uint8_t pad[256];
  memset(pad, 0, pl);
  memcpy(pad, pt, len);
  memcpy(iv, iv_copy, 16);
  mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT, pl, iv, pad, ct);
  memcpy(iv, iv_copy, 16);
  mbedtls_aes_free(&ctx);
  return pl;
}

// Hien thi len OLED SSD1306
void hien_thi(const char* line1, const char* line2,
              const char* line3, const char* line4) {
  oled.clearDisplay();
  oled.setTextColor(WHITE);
  oled.setTextSize(1);
  oled.setCursor(0, 0);
  oled.println(line1 ? line1 : "");
  oled.setCursor(0, 14);
  oled.println(line2 ? line2 : "");
  oled.setCursor(0, 28);
  oled.println(line3 ? line3 : "");
  oled.setCursor(0, 42);
  oled.println(line4 ? line4 : "");
  oled.display();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n==========================================");
  Serial.println(" MÔ PHỎNG HỆ THỐNG XI -> Y -> SERVER");
  Serial.println(" (ESP32 + BME280 + OLED + AES + WiFi)");
  Serial.println("==========================================");

  delay(500);
  oled.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  oled.clearDisplay();
  oled.display();
  hien_thi("Đang khởi động...", "", "", "");
  Serial.println("[+] OLED OK");

  WiFi.mode(WIFI_STA);
  WiFi.begin("Wokwi-GUEST");
  Serial.print("[WiFi] Kết nối...");
  hien_thi("Đang kết nối WiFi...", "Wokwi-GUEST", "", "");
  int w = 0;
  while (WiFi.status() != WL_CONNECTED && w < 80) {
    delay(500); Serial.print(".");
    w++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
    hien_thi("WiFi OK", WiFi.localIP().toString().c_str(), "", "");
  } else {
    Serial.println("\n[WiFi] FAIL");
    hien_thi("WiFi FAIL", "Vẫn tiếp tục...", "", "");
  }

  randomSeed(analogRead(0));
  seq = 1000 + random(9000);
  delay(1000);
}

void loop() {
  char buf[32];

  // PHASE 1: BEACON
  Serial.println("\n--- BEACON ---");
  hien_thi("XI: Phát Beacon", "B|Xi_01", "", "Chờ ACK...");
  Serial.printf("[XI] Phát Beacon (LoRa): B|%s\n", XI_ID);
  delay(1500);

  // PHASE 2: ACK
  Serial.println("\n--- ACK ---");
  hien_thi("Y: Nhận Beacon", "Từ Xi_01", "Gửi ACK...", "A|Xi_01|Y_01");
  Serial.printf("[Y]  Nhận Beacon từ %s\n", XI_ID);
  Serial.printf("[Y]  Gửi ACK (LoRa): A|%s|%s\n", XI_ID, Y_ID);
  delay(1000);
  hien_thi("XI: Nhận ACK", "Từ Y_01", "", "Đang đọc sensor...");
  Serial.printf("[XI] Nhận ACK từ %s\n", Y_ID);

  // PHASE 3: SENSOR + AES
  Serial.println("\n--- SENSOR + ENCRYPT ---");

  // Tất cả cảm biến đều mô phỏng bằng random()
  float t = 28.0 + random(-30, 30) / 10.0;
  float h = 60.0 + random(-20, 20) / 10.0;
  float p = 1005.0 + random(30);
  float c2 = 400 + random(50);
  float co = 5.0 + random(30) / 10.0;
  float nh3 = 2.0 + random(20) / 10.0;
  int   hr = random(2) ? 65 + random(20) : 0;
  float spo2 = hr ? 95.0 + random(50)/10.0 : 0;
  lat += 0.00005; lon += 0.00005;
  int sats = 6 + random(4);

  // Hiển thị sensor lên OLED
  snprintf(buf, sizeof(buf), "T:%.1fC H:%.0f%% P:%.0f", t, h, p);
  char buf2[32];
  snprintf(buf2, sizeof(buf2), "HR:%d SpO2:%.0f%%", hr, spo2);
  char buf3[32];
  snprintf(buf3, sizeof(buf3), "GPS:%.5fN %.5fE", lat, lon);
  hien_thi("XI: Đọc cảm biến", buf, buf2, buf3);

  Serial.printf("  SIM: T=%.1fC H=%.0f%% P=%.0fhPa\n", t, h, p);
  Serial.printf("  SIM: HR=%d SpO2=%.0f%%\n", hr, spo2);
  Serial.printf("  SIM: GPS=%.5fN %.5fE alt=10m sats=%d\n", lat, lon, sats);
  Serial.printf("  SIM: CO2=%.0f CO=%.1f NH3=%.1f\n", c2, co, nh3);

  snprintf(json_buf, sizeof(json_buf),
    "{\"id\":\"%s\",\"t\":%.1f,\"h\":%.1f,\"p\":%.1f,"
    "\"hr\":%d,\"spo2\":%.0f,"
    "\"co2\":%.0f,\"co\":%.1f,\"nh3\":%.1f,"
    "\"lat\":%.5f,\"lon\":%.5f,\"alt\":%.0f,\"sats\":%d,"
    "\"gw\":\"%s\",\"seq\":%u}",
    XI_ID, t, h, p, hr, spo2, c2, co, nh3,
    lat, lon, 10.0, sats, Y_ID, seq++);

  uint8_t iv[16], ct[256];
  size_t el = aes_encrypt((uint8_t*)json_buf, strlen(json_buf), ct, iv);

  char hex[512]; hex[0] = 0; char b[4];
  for (size_t i = 0; i < 16 + el; i++) {
    uint8_t v = i < 16 ? iv[i] : ct[i - 16];
    sprintf(b, "%02x", v); strcat(hex, b);
  }

  Serial.printf("[XI] AES-CBC: %d bytes (IV=16 + CT=%d)\n", 16 + el, el);
  Serial.printf("[XI] Hex: %.32s...\n", hex);

  char data_pkt[580];
  snprintf(data_pkt, sizeof(data_pkt), "D|%s|%s", XI_ID, hex);
  Serial.printf("[XI] Gửi data (LoRa): D|%s|<hex> (%d bytes)\n", XI_ID, strlen(hex));
  hien_thi("XI: AES xong", "Gửi data...", "", "");

  // PHASE 4: FORWARD
  Serial.println("\n--- FORWARD TO SERVER ---");
  hien_thi("Y: Nhận data", "Chuyển tiếp lên", "Server...", "");
  Serial.printf("[Y]  Nhận data từ %s\n", XI_ID);

  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("[Y]  WiFi mất kết nối, kết nối lại...");
    WiFi.reconnect();
    int r = 0;
    while (WiFi.status() != WL_CONNECTED && r < 30) {
      delay(500); Serial.print(".");
      r++;
    }
    Serial.println(WiFi.status() == WL_CONNECTED ? " OK" : " FAIL");
  }

  int http_code = -1;
  if (WiFi.status() == WL_CONNECTED) {
    char body[580];
    snprintf(body, sizeof(body), "{\"payload\":\"%s\"}", hex);
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    http_code = http.POST((uint8_t*)body, strlen(body));
    Serial.printf("[SERVER] HTTP %d - %s\n", http_code,
      http_code == 200 ? "THÀNH CÔNG!" : "THẤT BẠI");
    http.end();
  } else {
    Serial.println("[Y]  Không có WiFi, bỏ qua forward");
  }

  char status_line[32];
  snprintf(status_line, sizeof(status_line), "HTTP %d", http_code);
  hien_thi("Server:", status_line,
    http_code == 200 ? "THÀNH CÔNG!" : "THẤT BẠI", "");

  Serial.println("\n=== HOÀN THÀNH 1 CHU KỲ ===\n");

  cycles++;
  if (cycles >= 4) {
    Serial.println("=== ĐÃ HOÀN THÀNH 4 CHU KỲ MÔ PHỎNG ===");
    hien_thi("Hoàn thành!", "4 chu kỳ mô phỏng", "Xem Dashboard", "localhost:8501");
    while (1) delay(10000);
  }
  delay(3000);
}
```

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
