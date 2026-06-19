# Mô hình hiểm họa và Phân tích an ninh

*Tham khảo: tài liệu hướng dẫn đồ án [A], [B]; OWASP IoT Security Guidance [10]; code chống replay tại `server/app.py`*

## 1. Giả định hệ thống
- **Mạng IoT dùng chung một Pre-Shared Key (PSK)** (theo tài liệu hướng dẫn [A], [B]).
- **Mục tiêu chính:** Truyền tin nhanh, đơn giản, ít tài nguyên.
- **Mức độ bảo mật:** Không yêu cầu quá cao, phù hợp nghiên cứu và phòng lab [24].
- **Môi trường:** Vùng đồi núi Mù Cang Chải, hạ tầng mạng hạn chế.

## 2. Các kịch bản tấn công

| Kịch bản | Mô tả | Phòng chống |
|----------|-------|-------------|
| **Nghe lén (Eavesdropping)** | Kẻ tấn công thu thập dữ liệu trên đường truyền LoRa / WiFi | AES-128-CBC mã hóa payload (kẻ tấn công không có key sẽ không giải mã được) |
| **Tấn công phát lại (Replay)** | Gửi lại gói tin cũ đã thu được | Sequence Number kiểm tra tại Server (`seq > last_seq`) |
| **Giả mạo (Impersonation)** | Thiết bị lạ gửi dữ liệu giả danh Xi hợp lệ | Cần biết key `key_x_1234567890` mới mã hóa được payload hợp lệ |
| **Sửa đổi dữ liệu (Tampering)** | Thay đổi nội dung gói tin trên đường truyền | CBC decryption sẽ fail (padding error) nếu ciphertext bị sửa [4] |
| **Từ chối dịch vụ (DoS)** | Gửi flood request vào Server | ThreadPoolExecutor giới hạn worker; có thể mở rộng rate limit |

## 3. Cơ chế phòng chống chi tiết

### 3.1. Mã hóa AES-128-CBC chống nghe lén
- Payload JSON được mã hóa với IV ngẫu nhiên 16 byte trước khi truyền.
- Kẻ tấn công thu được ciphertext hex nhưng không có key (16 byte = 2^128 khả năng) không thể giải mã.
- IV thay đổi mỗi lần → cùng plaintext cho ciphertext khác nhau.

### 3.2. Sequence Number chống Replay
- Mỗi gói tin chứa trường `seq` (uint32, tăng dần, khởi tạo random 1000-9999).
- Server lưu `last_seq` riêng cho từng device trong bảng `devices`.
- Chỉ chấp nhận nếu `seq > last_seq`; nếu `seq <= last_seq` → HTTP 403 "Replay attack" (xem code tại `server/app.py`).

### 3.3. Tính toàn vẹn nhờ CBC
- Nếu kẻ tấn công sửa ciphertext trên đường truyền, quá trình giải mã CBC sẽ tạo ra plaintext sai (padding không khớp hoặc dữ liệu rác) → Server từ chối.

## 4. Hạn chế của giải pháp hiện tại

| Hạn chế | Tác động | Hướng khắc phục (tương lai) |
|---------|----------|------------------------------|
| **Một key cho toàn mạng** | Nếu 1 node bị lộ key → toàn bộ mạng bị ảnh hưởng | Dùng key riêng từng node, quản lý qua key server |
| **Không xác thực nguồn gốc** | Thiết bị lạ có thể gửi dữ liệu nếu biết key | Thêm HMAC-SHA256 với key riêng cho mỗi node |
| **NULL padding dễ phân biệt** | Kẻ tấn công biết chính xác độ dài plaintext | Chuyển sang PKCS#7 padding |
| **No rate limiting** | Server có thể bị DoS | Thêm Flask-Limiter hoặc nginx rate limit |

## 5. Kết luận
- Với mục đích nghiên cứu và môi trường phòng lab, các biện pháp hiện tại (AES-CBC + seq) là đủ dùng.
- Trọng tâm của đồ án là truyền tin IoT, không phải bảo mật cấp cao.
- Các hạn chế được ghi nhận và có thể cải thiện trong phiên bản mở rộng.
