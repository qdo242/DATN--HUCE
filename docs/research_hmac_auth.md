# Tham khảo: Cơ chế xác thực bằng HMAC (Phương án mở rộng)

*Tham khảo: tài liệu hướng dẫn đồ án [A], [B]; code triển khai AES-CBC tại `server/app.py` và `wokwi/sketch.ino` (HMAC chưa triển khai)*

## Khái niệm
HMAC (Hash-based Message Authentication Code) là cơ chế xác thực gói tin dùng khóa bí mật kết hợp với hàm băm (SHA-256). HMAC-SHA256 tạo ra mã xác thực 32 byte giúp đảm bảo:
1. **Tính toàn vẹn:** Dữ liệu không bị sửa đổi trên đường truyền.
2. **Xác thực nguồn gốc:** Gói tin thực sự đến từ thiết bị có khóa.

## Tại sao HMAC cần thiết?
- AES-128-CBC chỉ đảm bảo **tính bí mật** (không ai đọc được nội dung) và một phần tính toàn vẹn (padding error khi dữ liệu bị sửa).
- HMAC bổ sung **xác thực nguồn gốc**: mỗi node Xi có key riêng, đảm bảo gói tin đến từ đúng Xi chứ không phải thiết bị giả mạo.

## Thiết kế đề xuất

### Cấu trúc gói tin mở rộng (với HMAC)

| Offset | Field | Length | Description |
|--------|-------|--------|-------------|
| 0 | **Gateway ID** | 4 bytes | e.g. `b"Xi_01"` |
| 4 | **IV** | 16 bytes | AES-CBC IV |
| 20 | **Ciphertext** | Variable | AES-128-CBC encrypted JSON |
| End-32 | **HMAC-SHA256** | 32 bytes | HMAC của toàn bộ gói (Gateway ID + IV + Ciphertext) |

### Thứ tự xử lý tại Server
```python
# 1. Kiểm tra HMAC trước
hmac_computed = hmac.new(device_key, raw_packet, hashlib.sha256).digest()
if hmac_computed != received_hmac:
    reject()

# 2. Giải mã AES-CBC sau (chỉ khi HMAC khớp)
cipher = AES.new(network_key, AES.MODE_CBC, iv=iv)
plaintext = cipher.decrypt(ciphertext).rstrip(b'\0')
```

## So sánh với giải pháp hiện tại

| Tiêu chí | AES-CBC (hiện tại) | AES-CBC + HMAC (mở rộng) |
|----------|-------------------|--------------------------|
| Độ phức tạp | Thấp (~20 dòng) | Trung bình (~40 dòng) |
| Tài nguyên | ~1KB RAM, ~10KB Flash | Thêm ~1KB RAM, ~5KB Flash (SHA-256) |
| Bảo mật | Đủ dùng cho nghiên cứu | Cao hơn, chống giả mạo |
| Xác thực nguồn gốc | Yếu (qua key chung) | Mạnh (key riêng mỗi node) |
| Tốc độ | ~17-18µs (encrypt) | +~10µs (HMAC-SHA256) |
| Overhead gói tin | 16 byte (IV) | 16 byte (IV) + 32 byte (HMAC) |

## Ghi chú triển khai

- **Mbed TLS** có hỗ trợ HMAC-SHA256 qua `mbedtls_md_hmac()` [5].
- **PyCryptodome** có `HMAC.new(key, msg, digestmod=SHA256)` [6].
- **Tồn tại sẵn trong ESP32 Arduino Core** (thư viện `esp_sha.h`).

Do mục tiêu chính của đồ án là truyền tin nhanh, đơn giản, nên đồ án chưa triển khai HMAC. Đây có thể là hướng phát triển trong tương lai nếu cần nâng cao bảo mật.
