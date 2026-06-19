# Phân tích hiệu năng và lựa chọn giải pháp

*Tham khảo: tài liệu hướng dẫn đồ án [A], [B]; code triển khai tại `server/app.py` và `wokwi/sketch.ino`; kinh nghiệm thực nghiệm mô phỏng*

## 1. Yêu cầu
- **Mục tiêu:** Truyền tin nhanh, đơn giản, ít tốn tài nguyên.
- **Thiết bị:** ESP32 @ 240MHz, 520KB SRAM, 4MB Flash.
- **Module LoRa:** SX1278, băng tần 433MHz.

## 2. So sánh các phương án mã hóa

| Phương án | Tốc độ | Code | RAM | Flash | Overhead | Bảo mật | Đánh giá |
|-----------|--------|------|-----|-------|----------|---------|----------|
| **Không mã hóa** | Nhanh nhất | 0 dòng | 0 | 0 | 0 | Không | Không an toàn |
| **XOR Cipher** | Rất nhanh (vài cycle/byte) | 3-5 dòng | ~0 | ~100B | 0 | Yếu | OK cho demo |
| **AES-128-CBC** | Nhanh (~17-18µs) | ~20 dòng | ~1KB | ~10KB | 16B IV | Tốt | **Được chọn** |
| **AES-128-GCM** | Nhanh (~20-25µs) | ~30 dòng | ~2KB | ~15KB | 12B Nonce + 16B Tag | Rất tốt | Mở rộng sau |
| **Chacha20-Poly1305** | Trung bình (SW: ~50µs) | ~40 dòng | ~2KB | ~12KB | 12B Nonce + 16B Tag | Rất tốt | ESP32 không có HW accel |
| **TLS 1.3** | Chậm (handshake ~200ms) | Phức tạp | >30KB | >100KB | ~100B | Cao nhất | Không phù hợp IoT |

## 3. Phân tích chi tiết

### 3.1. AES-128-CBC with Hardware Accelerator
- ESP32 có module AES hardware accelerator riêng (không chiếm CPU cycles cho mã hóa).
- Thời gian mã hóa khối 16 byte: ~17-18 micro giây (đo từ Wokwi simulation).
- So với software implementation (ESP32 không có HW AES): ~200-300µs → nhanh hơn ~10-15x.
- Mbed TLS wrapper: `mbedtls_aes_crypt_cbc()` tự động chọn HW hay SW [5].

### 3.2. Chi phí Overhead

| Loại | Kích thước | So với plaintext (180 byte) |
|------|-----------|------------------------------|
| Plaintext JSON | ~180 bytes | 1x |
| + IV (16 byte) + ciphertext (176-192 byte) | ~192-208 bytes | ~1.1x |
| + hex encode | ~384-416 ký tự hex | ~2.2x |
| + HTTP JSON wrapper | ~416-456 ký tự hex | ~2.4x |

### 3.3. Thông lượng (Throughput)
- LoRa SX1278 @ SF7 CR4/5: ~5.5 kbps.
- Gói tin ~500 byte hex → thời gian truyền LoRa lý thuyết: ~725ms.
- Server xử lý: giải mã ~0.5ms + seq ~0.3ms + DB ~0.8ms = ~1.6ms.
- **Nút cổ chai:** LoRa (hàng trăm ms) >> mã hóa (µs).

### 3.4. Tiêu thụ năng lượng (ước tính)
| Hoạt động | Thời gian | Dòng (ESP32 @ 240MHz) | Năng lượng |
|-----------|-----------|----------------------|------------|
| AES-128-CBC encrypt | ~18 µs | ~80 mA | ~1.44 µJ |
| LoRa TX (SF7, 20dBm) | ~200 ms | ~120 mA | ~24,000 µJ |
| GPS fix | ~1 s | ~45 mA | ~45,000 µJ |

Kết luận: **Mã hóa AES chiếm <0.01% năng lượng so với LoRa TX.** Không cần tối ưu thêm.

## 4. Kết luận

**AES-128-CBC** là lựa chọn phù hợp nhất vì:
1. **Tận dụng hardware accelerator ESP32** (tốc độ ~17-18µs, nhanh hơn SW ~10-15x).
2. **Thư viện mbedtls có sẵn** trong Arduino Core, code đơn giản [5].
3. **Bảo mật đủ tốt** cho ứng dụng IoT nghiên cứu.
4. **Chi phí overhead thấp:** chỉ thêm 16 byte IV mỗi gói tin (~2.2x hex, chấp nhận được).
5. **Năng lượng không đáng kể** so với LoRa TX (<0.01%).

Các phương án mạnh hơn (GCM, Chacha20, TLS) không cần thiết vì nút cổ chai là LoRa, không phải CPU/hash. Nếu cần nâng cao bảo mật, nên thêm HMAC trước khi chuyển sang GCM.
