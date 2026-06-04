# Mô hình hiểm họa và Phân tích an ninh

## 1. Giả định hệ thống
- **Mạng IoT dùng chung một Pre-Shared Key (PSK)**
- **Mục tiêu chính:** Truyền tin nhanh, đơn giản, ít tài nguyên
- **Mức độ bảo mật:** Không yêu cầu quá cao

## 2. Các kịch bản tấn công

| Kịch bản | Mô tả | Phòng chống |
|----------|-------|-------------|
| **Nghe lén (Eavesdropping)** | Kẻ tấn công thu thập dữ liệu trên đường truyền | AES-128-CBC mã hóa payload |
| **Tấn công phát lại (Replay)** | Gửi lại gói tin cũ đã thu được | Sequence Number kiểm tra tại Server |
| **Giả mạo (Impersonation)** | Thiết bị lạ gửi dữ liệu | Cần biết key mới mã hóa được |
| **Sửa đổi dữ liệu (Tampering)** | Thay đổi nội dung gói tin | CBC decryption sẽ fail nếu dữ liệu bị sửa |

## 3. Hạn chế
- Do dùng chung một key toàn mạng, nếu 1 node bị lộ key thì toàn bộ mạng bị ảnh hưởng
- Tuy nhiên, với mục đích nghiên cứu và môi trường phòng lab, điều này chấp nhận được
- Trọng tâm của đồ án là truyền tin IoT, không phải bảo mật cấp cao
