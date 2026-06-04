# So sánh Phương án Mã hóa: XOR vs AES-128-CBC

## 1. Tiêu chí so sánh

Do mục đích chính của hệ thống IoT là **truyền tin nhanh, đơn giản, ít tốn tài nguyên**, các phương án mã hóa được đánh giá dựa trên:

- **Tốc độ xử lý** (quan trọng nhất)
- **Độ phức tạp code** (dễ triển khai trên ESP32)
- **Tài nguyên tiêu thụ** (RAM, Flash)
- **Mức độ bảo mật** (không yêu cầu quá cao)

## 2. So sánh chi tiết

| Tiêu chí | XOR Cipher | AES-128-CBC |
|----------|-----------|-------------|
| **Số dòng code** | 3-5 dòng | ~20 dòng |
| **Tốc độ** | Cực nhanh (vài CPU cycle/byte) | Rất nhanh (~17-18us nhờ HW accel) |
| **RAM** | Gần như 0 | ~1-2 KB |
| **Bảo mật** | Yếu (dễ bẻ khóa) | Tốt (chuẩn công nghiệp) |
| **Phần cứng hỗ trợ** | Không cần | ESP32 có AES accelerator |
| **Padding** | Không cần | Cần NULL padding |
| **IV** | Không cần | Cần 16-byte IV ngẫu nhiên |

## 3. Kết luận

- **XOR Cipher:** Phù hợp để minh họa cơ chế mã hóa đơn giản, code ngắn gọn
- **AES-128-CBC:** Được chọn cho đồ án vì tận dụng được hardware accelerator của ESP32, bảo mật tốt hơn, tính chuyên nghiệp cao hơn trong khi vẫn đảm bảo tốc độ xử lý nhanh

Cả 2 phương án đều chấp nhận được do mức độ bảo mật của mạng IoT này không yêu cầu quá cao, trọng tâm là truyền tin giữa các thiết bị IoT.
