# IoT Security Project — AI Agent Guide

## Project Overview
IoT security graduation project: Xi sensor nodes → LoRa → Y Gateway → WiFi/4G → Flask Server → Streamlit Dashboard. Uses AES-128-CBC encryption with ESP32 (TTGO T-Beam).

## Quick Start
```bash
pip install -r requirements.txt
python server/init_db.py
python server/app.py          # Terminal 1: Flask @ :5000
streamlit run server/dashboard.py  # Terminal 2: Dashboard @ :8501
```

## Wokwi Simulation
- 3 files to copy: `wokwi/sketch.ino`, `wokwi/diagram.json`, `wokwi/wokwi.toml`
- WiFi SSID: `Wokwi-GUEST` (no password)
- Server URL: update `SERVER_URL` in `sketch.ino` before uploading to Wokwi
- For internet access: `lt --port 5000 --subdomain <name>` (localtunnel)

## Key Files
| File | Purpose |
|------|---------|
| `wokwi/sketch.ino` | Wokwi simulation (ESP32, OLED, WiFi, AES, HTTP) |
| `hardware/xi_node/xi_node.ino` | TTGO T-Beam firmware (real hardware) |
| `hardware/y_gateway/y_gateway.ino` | Y Gateway firmware (ESP32+LoRa) |
| `server/app.py` | Flask server, AES-CBC decrypt, anti-replay |
| `server/init_db.py` | SQLite schema, device seeding |
| `server/dashboard.py` | Streamlit + Leaflet map |

## Architecture
```
Xi → LoRa(Beacon/ACK/Data) → Y → HTTP POST → Flask → SQLite → Streamlit
```
- Beacon: `B|<Xi_ID>`
- ACK: `A|<Xi_ID>|<Y_ID>`
- Data: `D|<Xi_ID>|<hex(IV16 + AES_CBC)>`
- JSON payload: `{id, t, h, p, hr, spo2, co2, co, nh3, lat, lon, alt, sats, gw, seq}`

## Security
- AES-128-CBC with mbedtls hardware acceleration (~17µs)
- Pre-Shared Key: `key_x_1234567890` (same for all devices)
- Anti-replay: server checks `seq > last_seq` per device
- Zero-padding: `memset(0)` on ESP32, `rstrip(b'\0')` on Python

## Known Issues
- Wokwi BME280 only supports SPI, not I2C — use random() fallback
- Wokwi has no LoRa, GPS NEO-M8N, or MAX30102 — simulated with random()
- Missing hardware: Y Gateway (ESP32 + LoRa SX1278 not purchased yet)
- OLED Wokwi display: `board-ssd1306` at 0x3C, needs `Wire.begin(21, 22)` before `oled.begin()`

## Common HTTP Errors
| Code | Reason | Fix |
|------|--------|-----|
| 403 | "Decryption Failed" | IV overwritten by mbedtls → use iv_copy |
| 403 | "Device not found" | device_id case mismatch → use `Xi_01` |
| 403 | "Replay attack" | seq <= last_seq → random starting seq |
| -1 | Connection refused | localtunnel not running or URL wrong |

## Pin Mapping (T-Beam)
- LoRa SPI: SCK=5, MISO=19, MOSI=27, CS=18, RST=23, DIO0=26
- GPS UART2: RX=12, TX=15
- I2C: SDA=21, SCL=22
- OLED: I2C 0x3C
- BME280: I2C 0x76
