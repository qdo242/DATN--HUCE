# Phân tích hiệu năng và lựa chọn giải pháp

## 1. Yêu cầu
- **Mục tiêu:** Truyền tin nhanh, đơn giản, ít tốn tài nguyên
- **Thiết bị:** ESP32 (240MHz, 520KB SRAM, 4MB Flash)
- **Module LoRa:** SX1278, băng tần 433MHz

## 2. So sánh các phương án mã hóa

| Phương án | Tốc độ | Code | RAM | Bảo mật | Đánh giá |
|-----------|--------|------|-----|---------|----------|
| **Không mã hóa** | Nhanh nhất | 0 dòng | 0 | Không | Không an toàn |
| **XOR Cipher** | Rất nhanh | 3-5 dòng | ~0 | Yếu | OK cho demo |
| **AES-128-CBC** | Nhanh (~17us) | ~20 dòng | ~1KB | Tốt | **Được chọn** |
| **AES-128-GCM** | Nhanh (~20us) | ~30 dòng | ~2KB | Rất tốt | Mở rộng sau |
| **TLS** | Chậm | Phức tạp | >30KB | Cao nhất | Không phù hợp |

## 3. Kết luận
**AES-128-CBC** là lựa chọn phù hợp nhất vì:
- Tận dụng hardware accelerator ESP32 (tốc độ ~17-18us)
- Thư viện mbedtls có sẵn, code đơn giản
- Bảo mật đủ tốt cho ứng dụng IoT nghiên cứu
- Chi phí overhead thấp: chỉ thêm 16 byte IV mỗi gói tin
