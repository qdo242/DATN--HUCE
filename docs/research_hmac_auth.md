# Tham khảo: Cơ chế xác thực bằng HMAC (Phương án mở rộng)

## Khái niệm
HMAC (Hash-based Message Authentication Code) là cơ chế xác thực gói tin dùng khóa bí mật + hàm băm. Nếu muốn nâng cao bảo mật, có thể kết hợp HMAC vào hệ thống.

## So sánh với giải pháp hiện tại

| Tiêu chí | XOR/AES-CBC (đang dùng) | + HMAC (mở rộng) |
|----------|------------------------|-------------------|
| Độ phức tạp | Thấp | Trung bình |
| Tài nguyên | Thấp | Thêm ~1KB RAM |
| Bảo mật | Đủ dùng | Cao hơn |
| Xác thực nguồn gốc | Qua key chung | Qua Gateway Key riêng |

## Ghi chú
Do mục tiêu chính của đồ án là truyền tin nhanh, đơn giản, nên đồ án chưa triển khai HMAC. Đây có thể là hướng phát triển trong tương lai nếu cần nâng cao bảo mật.
