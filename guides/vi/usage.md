# Hướng dẫn sử dụng

## Kiến trúc hệ thống

```
Xi node (ESP32 + cảm biến + LoRa) --> LoRa --> Y Gateway (ESP32 + LoRa + WiFi)
                                                  |
                                                  v
                                       Flask Server (Python + SQLite)
                                                  |
                                                  v
                                       Streamlit Dashboard (Web Map + Biểu đồ)
```

## Luồng giao thức

1. **Beacon**: Xi gửi `B|<Xi_ID>` qua LoRa
2. **ACK**: Y trả lời `A|<Xi_ID>|<Y_ID>` khi nhận được Beacon
3. **Đo lường**: Xi đọc cảm biến (nhiệt độ, độ ẩm, CO, CO2, NH3) và GPS
4. **Mã hóa**: Xi mã hóa JSON bằng AES-128-CBC (IV ngẫu nhiên mỗi gói)
5. **Gửi dữ liệu**: Xi gửi `D|<Xi_ID>|<hex(IV + ciphertext)>` qua LoRa
6. **Chuyển tiếp**: Y nhận dữ liệu, gói thành `{"payload":"<hex>"}`, POST lên Server
7. **Xử lý**: Server giải mã AES, kiểm tra seq (chống replay), lưu SQLite
8. **Hiển thị**: Dashboard hiển thị dữ liệu lên bản đồ Leaflet và biểu đồ

## Cách chạy

Xem `setup.md` để biết các bước cài đặt.

Sau khi chạy, truy cập:
- Server API: `http://127.0.0.1:5000`
- Dashboard: `http://localhost:8501`

## Kiểm tra

```bash
python server/main_test.py
```

## Mô phỏng Wokwi

Copy 3 file lên https://wokwi.com:
- `wokwi/sketch.ino`
- `wokwi/diagram.json`
- `wokwi/wokwi.toml`

Mô phỏng chạy luồng đầy đủ: WiFi → Beacon → ACK → AES mã hóa → HTTP POST 200.
