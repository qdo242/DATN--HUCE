# Cơ chế chống tấn công phát lại (Anti-Replay)

## Bài toán
Kẻ tấn công thu chặn một gói tin hợp lệ và gửi lại sau đó để làm sai lệch dữ liệu hệ thống.

## Giải pháp: Sequence Number
Mỗi bản tin JSON chứa trường `seq` tăng dần:

```json
{"id":"Xi_01", "t":28.5, "seq":1}
```

**Logic kiểm tra tại Server:**
- Server lưu `last_seq` cho từng thiết bị trong bảng `devices`
- Nếu `seq_moi > last_seq` → chấp nhận
- Nếu `seq_moi <= last_seq` → cảnh báo Replay Attack

## Tại sao seq nằm trong payload mã hóa?
Vì `seq` nằm trong JSON đã được AES mã hóa, kẻ tấn công không thể sửa đổi mà không làm hỏng toàn bộ gói tin. Khi giải mã thất bại, Server sẽ từ chối ngay lập tức.

## Ưu điểm so với Timestamp
- IoT node thường không có RTC pin hoặc đồng bộ NTP
- Sequence Number đơn giản, không cần đồng hồ
