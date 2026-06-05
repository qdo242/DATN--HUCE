# Xay dung giai phap truyen tin bao mat giua cac thiet bi IoT

Hệ thống IoT: Xi node (ESP32 + cảm biến) → LoRa → Y Gateway → WiFi → Server → Dashboard.

## Yeu cau

- Python 3.10+
- Git

## Clone & chay

```bash
git clone https://github.com/qdo242/DATN--DoAnhQuan.git
cd DATN--DoAnhQuan
pip install -r requirements.txt
python server/init_db.py
```

Mo Terminal 1:
```bash
python server/app.py
```

Mo Terminal 2:
```bash
streamlit run server/dashboard.py
```

Mo `http://localhost:8501`.

## Mo phong Wokwi

1. Vao https://wokwi.com → New Project → ESP32
2. Copy 3 file vao Wokwi: `wokwi/sketch.ino`, `wokwi/diagram.json`, `wokwi/wokwi.toml`
3. Chinh `SERVER_URL` trong `sketch.ino` neu dung localtunnel
4. Start Simulation

Neu can expose server ra internet:
```bash
npm install -g localtunnel
lt --port 5000 --subdomain ten-cua-ban
```

## Cau truc thu muc

```
DATN--DoAnhQuan/
├── hardware/          # Firmware ESP32 (Xi node, Y Gateway)
├── server/            # Flask + Streamlit + SQLite
├── wokwi/             # Mo phong Wokwi (3 file copy-paste)
├── docs/              # Tai lieu de tai, workflow
├── guides/            # Outline, huong dan cai dat
├── requirements.txt   # Python dependencies
└── README.md
```
