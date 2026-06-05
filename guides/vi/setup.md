# Hướng dẫn thiết lập

## Yêu cầu

- Python 3.10+
- Git

## Cài đặt nhanh

```bash
git clone https://github.com/qdo242/DATN--DoAnhQuan.git
cd DATN--DoAnhQuan
pip install -r requirements.txt
python server/init_db.py
```

## Chạy hệ thống

Terminal 1 — Flask Server:
```bash
python server/app.py
```

Terminal 2 — Dashboard:
```bash
streamlit run server/dashboard.py
```

Mở `http://localhost:8501` trên trình duyệt.

## Mô phỏng Wokwi

1. Vào https://wokwi.com → New Project → ESP32
2. Copy 3 file: `wokwi/sketch.ino`, `wokwi/diagram.json`, `wokwi/wokwi.toml`
3. Nhấn Start Simulation

Để expose server ra internet (cho Wokwi):
```bash
npm install -g localtunnel
lt --port 5000 --subdomain ten-cua-ban
```

Cập nhật `SERVER_URL` trong `wokwi/sketch.ino` với URL localtunnel.

## Ghi chú mã hóa

Hệ thống dùng một Pre-Shared Key `key_x_1234567890` (16 byte) cho AES-128-CBC. Key được hardcode trong cả firmware ESP32 và Python server. Không cần file `.env`.
