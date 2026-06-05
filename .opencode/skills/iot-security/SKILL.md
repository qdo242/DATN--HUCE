---
name: iot-security
description: "Use this skill for the IoT Security graduation thesis project (DATN) by Do Anh Quan and Ta Huy Hoang. The project builds a secure IoT communication system between sensor nodes (Xi), a mobile gateway (Y), and a Flask backend server. Trigger when working on: AES-128-CBC encryption, XOR cipher, LoRa Beacon/ACK handshake protocol, Flask server API, SQLite database, Streamlit dashboard with Leaflet map, Wokwi ESP32 simulation, or any security testing (anti-replay, decryption errors). Also trigger when the user references any file under server/, wokwi/, docs/, guides/, or plan/."
license: MIT
---

# IoT Secure Communication System (Xi -> Y -> Server)

## Architecture
- **Nodes (Xi)**: ESP32 sensor nodes measuring temperature, humidity, CO, CO2, NH3 + GPS
- **Gateway (Y)**: Mobile ESP32 receiving LoRa messages, forwarding to Server via WiFi
- **Server**: Flask backend with SQLite, AES decryption, Streamlit dashboard + Leaflet map

## Quick Start
```powershell
pip install -r requirements.txt
python server/init_db.py
python server/app.py          # Terminal 1
streamlit run server/dashboard.py  # Terminal 2
python server/main_test.py    # Terminal 3
```

## Skill Structure

| Directory | Contents |
|-----------|----------|
| [protocol/](protocol/) | Packet structure, Beacon/ACK protocol, Encryption scheme |
| [reference/](reference/) | API reference, Database schema, Wokwi reference |
| [rules/](rules/) | Coding standards, Security rules |
| [validation/](validation/) | Test scenarios, Verification checklist |
| [workflow/](workflow/) | Development workflow, Testing workflow |

## Quick Reference

### Encryption
- **Method:** `AES-128-CBC` with 16-byte IV + NULL padding (Pre-Shared Key toàn mạng)
- **Alternative:** `XOR Cipher` (đơn giản nhất, tham khảo `server/xor_cipher.py`)
- **Key:** `b'key_x_1234567890'` (16 bytes)
- **Tốc độ AES-CBC trên ESP32:** ~17-18 micro giây (nhờ hardware accelerator)

### Key Files
| File | Purpose |
|------|---------|
| `server/app.py` | Flask API `/receive-data` + seq check |
| `server/xor_cipher.py` | XOR cipher tham khảo (3 dòng code) |
| `server/dashboard.py` | Streamlit + Leaflet map |
| `wokwi/sketch.ino` | ESP32 firmware (AES-CBC) |
| `docs/research_encryption_comparison.md` | So sánh XOR vs AES-CBC |

### Test Commands
```powershell
python server/main_test.py       # Basic test (AES-CBC)
python server/simulator.py       # Full simulation
python server/check_my_server.py # Connectivity test
python server/xor_cipher.py      # XOR cipher demo
```

## Project Team
- **Đỗ Anh Quân** — Encryption, Flask Server, Database, Web Map
- **Tạ Huy Hoàng** — Hardware, Beacon/ACK, LoRa, Gateway
