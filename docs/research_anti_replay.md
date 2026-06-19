# Cơ chế chống tấn công phát lại (Anti-Replay)

*Tham khảo: tài liệu hướng dẫn đồ án [A], [B]; code triển khai tại `server/app.py` (hàm kiểm tra seq)*

## Bài toán
Kẻ tấn công thu chặn một gói tin hợp lệ (nghe lén trên LoRa/WiFi) và gửi lại sau đó để làm sai lệch dữ liệu hệ thống. Đây là một trong những kịch bản phổ biến nhất trong tấn công IoT.

## Giải pháp: Sequence Number

### Cách hoạt động
Mỗi bản tin JSON chứa trường `seq` (uint32) tăng dần theo mỗi lần gửi:

```json
{"id":"Xi_01", "t":28.5, "seq":1}
```

**Logic kiểm tra tại Server:**
- Server lưu `last_seq` cho từng thiết bị trong bảng `devices`
- Nếu `seq_moi > last_seq` → chấp nhận, cập nhật `last_seq = seq_moi`
- Nếu `seq_moi <= last_seq` → HTTP 403 "Replay attack detected"

### Khởi tạo seq
- Khi ESP32 (Xi) khởi động, chọn ngẫu nhiên `seq = 1000 + random(9000)`.
- Mục đích: tránh trùng seq khi thiết bị reset nhiều lần (seq cũ trong DB thấp hơn).

## Tại sao seq nằm trong payload mã hóa?
- `seq` là một trường trong JSON, toàn bộ JSON được mã hóa AES-128-CBC trước khi truyền.
- Kẻ tấn công không thể sửa đổi seq mà không làm hỏng toàn bộ ciphertext (CBC property).
- Nếu giải mã thất bại, Server trả về HTTP 403 "Decryption Failed".

## Ưu điểm so với Timestamp

| Tiêu chí | Sequence Number | Timestamp |
|----------|----------------|-----------|
| **Đồng hồ** | Không cần | Cần RTC pin / NTP sync |
| **Độ phức tạp** | Thấp (uint32 + 1 dòng so sánh) | Trung bình (cần xử lý chênh lệch múi giờ, drift) |
| **IoT Node** | Phù hợp (ESP32 không cần RTC pin) | Không phù hợp (thiết bị thường không có NTP) |
| **Chống Replay** | Tốt nếu seq tăng nghiêm ngặt | Phụ thuộc vào độ chính xác đồng hồ |

Kết luận: Sequence Number là lựa chọn tối ưu cho IoT device không có RTC.

## Pseudocode kiểm tra

**Server (Python)**:
```python
if payload.seq <= device.last_seq:
    return {"error": "Replay attack detected"}, 403
device.last_seq = payload.seq
```

**ESP32 (C++):**
```cpp
seq = 1000 + esp_random() % 9000;  // mỗi lần boot
// seq++ sau mỗi lần gửi
seq++;
```
