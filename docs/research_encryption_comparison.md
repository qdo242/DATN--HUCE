# So sánh Phương án Mã hóa: XOR vs AES-128-CBC

*Tham khảo: tài liệu hướng dẫn đồ án [A], [B]; AES standard [1]; code mẫu XOR tại `server/xor_cipher.py`, AES-CBC tại `server/app.py` và `wokwi/sketch.ino`*

## 1. Tiêu chí so sánh

Do mục đích chính của hệ thống IoT là **truyền tin nhanh, đơn giản, ít tốn tài nguyên**, các phương án mã hóa được đánh giá dựa trên:

- **Tốc độ xử lý** (quan trọng nhất) — đo bằng micro giây
- **Độ phức tạp code** (dễ triển khai trên ESP32) — đo bằng số dòng code
- **Tài nguyên tiêu thụ** (RAM, Flash) — đo bằng KB
- **Mức độ bảo mật** (không yêu cầu quá cao) — đánh giá định tính

## 2. So sánh chi tiết

| Tiêu chí | XOR Cipher | AES-128-CBC |
|----------|-----------|-------------|
| **Số dòng code** | 3-5 dòng | ~20 dòng |
| **Tốc độ** | Cực nhanh (vài CPU cycle/byte) | Rất nhanh (~17-18µs nhờ HW accel) |
| **RAM** | Gần như 0 | ~1-2 KB (context struct + buffer) |
| **Flash** | ~100 byte | ~10 KB (mbedtls AES module) |
| **Bảo mật** | Yếu (dễ bẻ khóa bằng phân tích tần suất) | Tốt (chuẩn công nghiệp, 2^128 key space) |
| **Phần cứng hỗ trợ** | Không cần | ESP32 có AES accelerator |
| **Padding** | Không cần | Cần NULL padding lên bội số 16 byte |
| **IV** | Không cần | Cần 16-byte IV ngẫu nhiên mỗi gói tin |
| **Tính toàn vẹn** | Không | CBC phát hiện sửa đổi (padding error) |
| **Khả năng chống replay** | Không (phải tự thêm seq) | Cần thêm seq ngoài mã hóa (đã triển khai) |

### 2.1. XOR Cipher — Phân tích

- Phép XOR (`^`) là phép toán bit cơ bản trong đại số Boolean [7].
- Công thức: `ciphertext[i] = plaintext[i] XOR key[i % key_len]`
- Giải mã: `plaintext[i] = ciphertext[i] XOR key[i % key_len]`
- **Nhược điểm:** Nếu key ngắn hơn plaintext, mẫu lặp lại; dễ bị phân tích tần suất. Với key `key_x_1234567890` (16 byte) cố định, XOR cipher về cơ bản tương đương mã hóa Caesar trên mỗi byte.
- **Khi nào dùng:** Chỉ phù hợp demo, minh họa, hoặc dữ liệu không yêu cầu bảo mật.

### 2.2. AES-128-CBC — Phân tích

- AES-128 thực hiện 10 rounds (SubBytes, ShiftRows, MixColumns, AddRoundKey) trên ma trận 4×4 byte [3].
- CBC mode: mỗi khối plaintext được XOR với ciphertext khối trước (hoặc IV cho khối đầu) trước khi mã hóa [4].
- ESP32 có AES accelerator phần cứng (`mbedtls_aes_crypt_cbc`), không dùng software implementation [10][17].
- **Padding:** NULL byte (`\0`) — đơn giản nhưng dễ bị lộ độ dài plaintext thật. PKCS#7 là lựa chọn tốt hơn cho production.

## 3. Kết luận

- **XOR Cipher:** Phù hợp để minh họa cơ chế mã hóa đơn giản, code ngắn gọn trong thuyết minh.
- **AES-128-CBC:** **Được chọn** cho đồ án vì:
  1. Tận dụng hardware accelerator ESP32 (tốc độ ~17-18µs, không ảnh hưởng đến hiệu năng truyền tin)
  2. Bảo mật tốt (chuẩn NIST, được kiểm chứng rộng rãi)
  3. Tính chuyên nghiệp cao hơn
  4. Vẫn đảm bảo tốc độ xử lý nhanh, code đơn giản

Cả 2 phương án đều chấp nhận được do mức độ bảo mật của mạng IoT này không yêu cầu quá cao, trọng tâm là truyền tin giữa các thiết bị IoT.
