# Hướng dẫn chạy mô phỏng Wokwi + Server + Dashboard

## Kiến trúc hệ thống

```
Xi node (ESP32 + LoRa + cảm biến)
  │
  ├─ Bật nguồn → gửi Beacon "B|<Xi_ID>"
  │
  ├─ Chờ ACK từ Y Gateway
  │
  ├─ Đọc cảm biến (BME280, MAX30102, GPS, MQ)
  │
  ├─ Mã hóa JSON bằng AES-128-CBC
  │
  └─ Gửi "D|<Xi_ID>|<hex_encrypted>" qua LoRa
       │
       ▼
Y Gateway (ESP32 + LoRa + WiFi)
       │
       ├─ Quét LoRa → nhận Beacon → gửi ACK
       ├─ Nhận data → forward HTTP POST lên Server
       │
       ▼
Flask Server (Python)
       │
       ├─ Giải mã AES-128-CBC
       ├─ Chống replay attack (seq)
       ├─ Lưu vào SQLite
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

Giữ terminal này chạy. Server lắng nghe tại `http://127.0.0.1:5000`.

---

### Terminal 2: Localtunnel

```bash
lt --port 5000 --subdomain ten-cua-ban
```

Lấy URL (ví dụ `https://ten-cua-ban.loca.lt`) và **cập nhật vào `SERVER_URL`** trong code Wokwi trước khi copy.

---

### Terminal 3: Dashboard

```bash
python -m streamlit run server\dashboard.py
```

Mở trình duyệt tại `http://localhost:8501`.

---

## Cách chạy Wokwi

1. Vào https://wokwi.com → **New Project** → **ESP32**
2. Copy nội dung 3 file bên dưới vào Wokwi:
   - `sketch.ino` → file `.ino` bên trái
   - `diagram.json` → file `diagram.json`
   - `wokwi.toml` → file `wokwi.toml`
3. Nhấn **Start Simulation**
4. Quan sát Serial Output

> Wokwi chạy 1 ESP32 đóng 2 vai trò Xi + Y, output serial thể hiện toàn bộ luồng giao thức.

---

## `sketch.ino`

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <mbedtls/aes.h>

// AES-128 key (16 bytes) = "key_x_1234567890"
const uint8_t NETWORK_KEY[16] = {
  0x6B, 0x65, 0x79, 0x5F, 0x78, 0x5F, 0x31, 0x32,
  0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30
};
const char* XI_ID = "Xi_01";
const char* Y_ID  = "Y_01";
// THAY URL nay bang localtunnel URL cua ban
const char* SERVER_URL = "https://dirty-dingos-serve.loca.lt/receive-data";

char json_buf[512];
uint32_t seq = 1;
float lat = 21.00355, lon = 105.84255;

// AES-128-CBC encrypt, tra ve do dai ciphertext
// QUAN TRONG: mbedtls ghi đè bien iv => phai dung iv_copy de luu lai
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
  memcpy(iv, iv_copy, 16);  // khoi phuc IV goc
  mbedtls_aes_free(&ctx);
  return pl;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== MO PHONG XI -> Y -> SERVER ===");

  WiFi.mode(WIFI_STA);
  WiFi.begin("Wokwi-GUEST");
  Serial.print("[WiFi] Ket noi...");
  int w = 0;
  while (WiFi.status() != WL_CONNECTED && w < 80) {
    delay(500); Serial.print(".");
    w++;
  }
  if (WiFi.status() == WL_CONNECTED)
    Serial.printf("\n[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
  else
    Serial.println("\n[WiFi] FAIL");
  randomSeed(analogRead(0));
}

void loop() {
  // PHASE 1: BEACON
  Serial.println("\n--- BEACON ---");
  Serial.printf("[XI] Phat Beacon (LoRa): B|%s\n", XI_ID);
  delay(1500);

  // PHASE 2: ACK
  Serial.println("\n--- ACK ---");
  Serial.printf("[Y]  Nhan Beacon tu %s\n", XI_ID);
  Serial.printf("[Y]  Gui ACK (LoRa): A|%s|%s\n", XI_ID, Y_ID);
  delay(1000);
  Serial.printf("[XI] Nhan ACK tu %s\n", Y_ID);

  // PHASE 3: SENSOR + AES + SEND
  Serial.println("\n--- SENSOR + ENCRYPT ---");
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

  Serial.printf("  BME280  -> T=%.1fC  H=%.0f%%  P=%.0fhPa\n", t, h, p);
  Serial.printf("  MAX30102-> HR=%d bpm  SpO2=%.0f%%\n", hr, spo2);
  Serial.printf("  GPS     -> lat=%.5f lon=%.5f alt=10m sats=%d\n", lat, lon, sats);
  Serial.printf("  MQ (sim)-> CO2=%.0f CO=%.1f NH3=%.1f\n", c2, co, nh3);

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
  Serial.printf("[XI] AES-CBC: IV + CT = %d bytes\n", 16 + el);

  char data_pkt[580];
  snprintf(data_pkt, sizeof(data_pkt), "D|%s|%s", XI_ID, hex);
  Serial.printf("[XI] Gui data (LoRa): %s\n", data_pkt);

  // PHASE 4: FORWARD
  Serial.println("\n--- FORWARD TO SERVER ---");
  Serial.printf("[Y]  Nhan data tu %s\n", XI_ID);
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("[Y]  WiFi mat ket noi, ket noi lai...");
    WiFi.reconnect();
    int r = 0;
    while (WiFi.status() != WL_CONNECTED && r < 30) {
      delay(500); Serial.print(".");
      r++;
    }
    Serial.println(WiFi.status() == WL_CONNECTED ? " OK" : " FAIL");
  }

  if (WiFi.status() == WL_CONNECTED) {
    char body[580];
    snprintf(body, sizeof(body), "{\"payload\":\"%s\"}", hex);
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    int r = http.POST((uint8_t*)body, strlen(body));
    Serial.printf("[SERVER] HTTP %d\n", r);
    http.end();
  } else {
    Serial.println("[Y]  Khong co WiFi");
  }

  Serial.println("\n=== HOAN THANH 1 CHU KY ===\n");
  if (seq > 4) {
    Serial.println("=== HOAN THANH 4 CHU KY ===");
    while (1) delay(10000);
  }
  delay(3000);
}
```

---

## `diagram.json`

```json
{
  "version": 1,
  "author": "Do Anh Quan & Ta Huy Hoang",
  "editor": "wokwi",
  "parts": [
    { "type": "board-esp32-devkit-v1", "id": "esp", "top": -100, "left": -300, "attrs": {} }
  ],
  "connections": [
    ["esp:TX0", "$serialMonitor:RX", "", []],
    ["esp:RX0", "$serialMonitor:TX", "", []]
  ],
  "dependencies": {}
}
```

---

## `wokwi.toml`

```toml
[wokwi]
version = 1
firmware = 'sketch.ino'
diagram = 'diagram.json'
```

---

## Các vấn đề đã gặp và cách fix

| Vấn đề | Nguyên nhân | Fix |
|--------|-------------|-----|
| Wokwi VS Code extension boot loop `rst:0x3` | Extension không ổn định trên máy này | Dùng Wokwi web thay thế |
| WiFi không kết nối | Timeout ngắn + thiếu `WiFi.mode(WIFI_STA)` | Tăng timeout 80 lần + thêm `WiFi.mode(WIFI_STA)` |
| HTTP -1 (kết nối thất bại) | Localtunnel chưa chạy, hoặc URL sai | Chạy `lt --port 5000`, cập nhật `SERVER_URL` |
| HTTP 403 - Decryption Failed | mbedtls ghi đè biến `iv` sau khi encrypt | Dùng `iv_copy` để lưu IV gốc |
| HTTP 403 - Device not found | Sai case: `XI_01` vs `Xi_01` | Đồng bộ device_id |
| HTTP 503 | Server Flask chưa chạy | Chạy `python server/app.py` trước |

---

## Ghi chú quan trọng

- **Pre-Shared Key:** Cả ESP32 và Server dùng chung key `key_x_1234567890`
- **Chống replay:** Sequence number (`seq`) tăng dần, server kiểm tra `seq > last_seq`
- **AES padding:** Zero-padding (ESP32 dùng `memset 0`, server dùng `rstrip(b'\0')`)
- **IV ngẫu nhiên:** Mỗi gói tin có IV 16 bytes mới, gửi kèm trong hex payload
- **Localtunnel:** Mỗi lần chạy lại `lt` có thể ra URL khác — nhớ cập nhật lại `SERVER_URL`
