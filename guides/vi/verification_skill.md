# Phương pháp kiểm định và xác thực hệ thống

## 1. Quy trình kiểm tra

### 1.1. Kiểm thử đơn vị
- **Mục tiêu:** Xác minh mã hóa AES-128-CBC (ESP32) và giải mã (Server) cho kết quả đúng.
- **Phương pháp:** Dùng `server/main_test.py` gửi gói tin mã hóa mẫu, kiểm tra HTTP 200.

### 1.2. Kiểm thử tích hợp
- **Mục tiêu:** Đảm bảo luồng đầy đủ hoạt động: Xi → LoRa (mô phỏng) → Y → HTTP POST → Server.
- **Phương pháp:** Chạy `main_test.py` — gửi 2 gói tin kiểm tra, xác nhận server phản hồi.

### 1.3. Kiểm thử an ninh
- **Tấn công phát lại (Replay):** Server kiểm tra `seq > last_seq`. Gửi lại gói tin cũ → HTTP 403.
- **Sai key:** Giải mã thất bại → HTTP 403 "Decryption Failed".
- **Sai Device ID:** Server kiểm tra device trong DB → HTTP 403 "Device not found".

## 2. Mô phỏng Wokwi

Copy 3 file lên https://wokwi.com, bắt đầu mô phỏng. Quan sát serial output:
- Kết nối WiFi
- Bắt tay Beacon → ACK
- Mã hóa AES
- Kết quả HTTP POST (mong đợi 200)

## 3. Dọn dẹp

Xóa file `iot_security.db` và chạy `python server/init_db.py` để reset.
