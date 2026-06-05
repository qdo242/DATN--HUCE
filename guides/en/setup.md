# Setup Guide

## Requirements

- Python 3.10+
- Git

## Quick Setup

```bash
git clone https://github.com/qdo242/DATN--DoAnhQuan.git
cd DATN--DoAnhQuan
pip install -r requirements.txt
python server/init_db.py
```

## Run the System

Terminal 1 — Flask Server:
```bash
python server/app.py
```

Terminal 2 — Dashboard:
```bash
streamlit run server/dashboard.py
```

Open `http://localhost:8501` in your browser.

## Wokwi Simulation

1. Go to https://wokwi.com → New Project → ESP32
2. Copy 3 files: `wokwi/sketch.ino`, `wokwi/diagram.json`, `wokwi/wokwi.toml`
3. Press Start Simulation

To expose the server to the internet (for Wokwi):
```bash
npm install -g localtunnel
lt --port 5000 --subdomain your-name
```

Update `SERVER_URL` in `wokwi/sketch.ino` with the localtunnel URL.

## Encryption Note

This project uses a single Pre-Shared Key `key_x_1234567890` (16 bytes) for AES-128-CBC encryption. The key is hardcoded in both the ESP32 firmware and the Python server. No `.env` file required.
