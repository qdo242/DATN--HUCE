---
name: iot-datn
description: Use when working on the IoT security graduation project (DATN). Covers ESP32 firmware, LoRa protocol, AES-128-CBC, Flask server, Streamlit dashboard, and Wokwi simulation.
---

# IoT Security Graduation Project (DATN)

## QUAN TRỌNG: ĐỌC ĐỀ TÀI TRƯỚC KHI LÀM

**BẮT BUỘC:** Khi bắt đầu làm việc với project này, agent phải **đọc `docs/thesis.md`** trước.
Sau đó kiểm tra tính chính xác: mọi code, tài liệu, cấu hình phải khớp với đề tài.
Nếu phát hiện sai lệch (thiếu tính năng, sai kiến trúc, sai giao thức), phải báo lại cho user và đề xuất sửa.

## Project Overview
**Thesis:** "Xây dựng giải pháp truyền tin bảo mật giữa các thiết bị IoT"  
**Goal:** Fast, simple, low-resource IoT communication with moderate security  
**Architecture:** Xi sensor nodes → LoRa → Y Gateway → WiFi/4G → Flask Server → Streamlit Dashboard

## Key Design Decisions
- **One Pre-Shared Key** for the whole network (teacher's requirement: "mạng IoT này mục đích chính là truyền tin, yêu cầu nhanh, đơn giản nhất / ít tốn tài nguyên nhất, mức độ bảo mật không quá cao")
- **AES-128-CBC** with hardware acceleration on ESP32 (~17-18µs), random IV per packet, zero-padding
- **Custom LoRa P2P protocol** (text-based: `B|`, `A|`, `D|`) instead of LoRaWAN
- **Sequence number** anti-replay: server checks `seq > last_seq`
- **Wokwi simulation** for thesis defense (LoRa/GPS/MAX30102 simulated with `random()`)

## Running the Project (3 terminals)
```bash
# Terminal 1: Server
python server/init_db.py
python server/app.py              # Flask @ :5000

# Terminal 2: Dashboard
streamlit run server/dashboard.py # Streamlit @ :8501

# Terminal 3 (optional): localtunnel for Wokwi
lt --port 5000 --subdomain <name>
```

## Wokwi Simulation
- **3 files** to copy to https://wokwi.com: `sketch.ino`, `diagram.json`, `wokwi.toml`
- WiFi SSID: `Wokwi-GUEST` (no password)
- BME280 on Wokwi is SPI-only (custom chip) — removed from diagram, all sensors use `random()`
- OLED: `board-ssd1306` at I2C 0x3C, needs `Wire.begin(21, 22)` before `oled.begin()`
- Update `SERVER_URL` in `sketch.ino` before uploading

## Key Files
| File | Description |
|------|-------------|
| `wokwi/sketch.ino` | Wokwi simulation (ESP32 + OLED + WiFi + AES + HTTP POST) |
| `wokwi/diagram.json` | Wokwi wiring (ESP32 + OLED SSD1306) |
| `hardware/xi_node/xi_node.ino` | T-Beam firmware (BME280 + MAX30102 + GPS + LoRa + AES) |
| `hardware/y_gateway/y_gateway.ino` | Y Gateway firmware (ESP32 + LoRa + WiFi forwarder) |
| `server/app.py` | Flask server (AES-CBC decrypt + anti-replay + SQLite) |
| `server/init_db.py` | Database schema (devices + telemetry) |
| `server/dashboard.py` | Streamlit dashboard (Leaflet map + sensor charts) |

## Protocol
```
Beacon: B|<Xi_ID>
ACK:    A|<Xi_ID>|<Y_ID>
Data:   D|<Xi_ID>|<hex(IV16 + AES_CBC_ciphertext)>
```

## Pin Mapping (TTGO T-Beam)
- LoRa SPI: SCK=5, MISO=19, MOSI=27, CS=18, RST=23, DIO0=26
- GPS UART2: RX=12, TX=15
- I2C: SDA=21, SCL=22
- OLED: I2C 0x3C
- BME280: I2C 0x76

## Common Issues
| HTTP Error | Cause | Fix |
|-----------|-------|-----|
| 403 "Decryption Failed" | mbedtls overwrites IV | Use `iv_copy` in `aes_encrypt()` |
| 403 "Device not found" | device_id case mismatch | Use `Xi_01` (not `XI_01`) |
| 403 "Replay attack" | seq <= last_seq | Random starting seq |
| -1 | localtunnel not running | Start `lt --port 5000` |

## Hardware Status
- Teacher purchased: 1× TTGO T-Beam, 1× BME280, 1× MAX30102, 1× OLED SSD1306
- Missing: Y Gateway (ESP32 DevKit + LoRa SX1278 not purchased)
- Workaround: T-Beam WiFi direct to Server, or USB serial → laptop Python script
