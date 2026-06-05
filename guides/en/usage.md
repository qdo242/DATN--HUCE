# Usage Guide

## System Architecture

```
Xi node (ESP32 + sensors + LoRa) --> LoRa --> Y Gateway (ESP32 + LoRa + WiFi)
                                                  |
                                                  v
                                       Flask Server (Python + SQLite)
                                                  |
                                                  v
                                       Streamlit Dashboard (Web Map + Charts)
```

## Protocol Flow

1. **Beacon**: Xi sends `B|<Xi_ID>` over LoRa
2. **ACK**: Y replies `A|<Xi_ID>|<Y_ID>` when it receives the Beacon
3. **Sensing**: Xi reads sensors (temperature, humidity, CO, CO2, NH3) and GPS
4. **Encryption**: Xi encrypts JSON payload with AES-128-CBC (random IV each packet)
5. **Data**: Xi sends `D|<Xi_ID>|<hex(IV + ciphertext)>` over LoRa
6. **Forward**: Y receives data, wraps as `{"payload":"<hex>"}`, POSTs to Server
7. **Process**: Server decrypts AES, checks seq number (anti-replay), saves to SQLite
8. **Display**: Dashboard shows data on Leaflet map and sensor charts

## How to Run

See `setup.md` for installation steps.

After running, access:
- Server API: `http://127.0.0.1:5000`
- Dashboard: `http://localhost:8501`

## Test

```bash
python server/main_test.py
```

## Wokwi Simulation

Copy 3 files to https://wokwi.com:
- `wokwi/sketch.ino`
- `wokwi/diagram.json`
- `wokwi/wokwi.toml`

The simulation demonstrates the full flow: WiFi → Beacon → ACK → AES encrypt → HTTP POST 200.
