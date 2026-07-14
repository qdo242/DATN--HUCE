### 2.3.3. Mã hóa đối xứng với AES, CBC

#### Vấn đề khi áp dụng cho IoT mô-đun

Hệ thống IoT gồm các node cảm biến (Xi) với vi điều khiển ESP32 có 320 KB RAM, 4 MB Flash, CPU Xtensa 240 MHz. Khi chọn thuật toán mã hóa, cần đảm bảo:

- **Đơn giản nhất, nhanh nhất, dễ triển khai trên ESP32** — ưu tiên hàng đầu.
- **Chấp nhận toàn mạng dùng chung một khóa bí mật** (Pre-Shared Key — PSK).
- **Lược bớt các tính năng phức tạp** như key negotiation, chứng thực số, nhiều vòng lặp khóa.

Kích thước khóa 16 byte (128 bit) được chọn vì:
- AES định nghĩa khóa 128 bit = 16 byte [FIPS 197].
- IV trong chế độ CBC bằng đúng kích thước khối AES (16 byte) [SP 800-38A].
- Đủ nhỏ lưu trong RAM ESP32, vừa đủ lớn chống tấn công vét cạn (2^128 tổ hợp).
- Thư viện mbedtls hỗ trợ sẵn AES-128 trên ESP-IDF và Arduino Core.

#### Thuật toán AES

AES (Advanced Encryption Standard) là thuật toán mã hóa khối đối xứng do NIST công bố năm 2001 [FIPS 197]. AES-128 xử lý khối 128 bit, sử dụng khóa 128 bit (16 byte), thực hiện 10 vòng biến đổi trên ma trận 4×4 byte. Mỗi vòng gồm 4 phép biến đổi:

1. **SubBytes** — thay thế từng byte bằng giá trị trong S-box (tra bảng phi tuyến).
2. **ShiftRows** — dịch vòng các hàng của ma trận.
3. **MixColumns** — nhân ma trận trên mỗi cột với đa thức cố định.
4. **AddRoundKey** — XOR ma trận trạng thái với khóa vòng.

Vòng cuối cùng bỏ qua MixColumns.

**CBC mode (Cipher Block Chaining)** không thay đổi thuật toán AES mà quy định cách liên kết các khối [SP 800-38A]:

```
C1 = AES_K(P1 XOR IV)
Ci = AES_K(Pi XOR C(i-1)), i > 1
```

Mỗi khối plaintext được XOR với ciphertext khối trước (hoặc IV cho khối đầu) trước khi mã hóa. Cơ chế này đảm bảo hai gói tin giống nhau mã hóa ra ciphertext khác nhau nếu IV khác nhau.

*Hình 2.11. Các phép biến đổi trong một vòng mã hóa AES*
*Hình 2.12. Minh họa phép ShiftRows và MixColumns của AES*
*Bảng 2.2. Cấu trúc payload AES-128-CBC*

#### Triển khai AES-CBC trên ESP32

Nhờ **hardware accelerator** tích hợp sẵn trên ESP32, AES-CBC chỉ mất khoảng **17-18 micro giây** cho một gói tin nhỏ [đo từ thực nghiệm], nhanh hơn rất nhiều so với triển khai phần mềm. Code triển khai sử dụng thư viện mbedtls:

```cpp
// File: hardware/xi_node/xi_node.ino:76-91
static size_t aes_encrypt(uint8_t* pt, size_t len, uint8_t* ct, uint8_t* iv) {
  mbedtls_aes_context ctx;
  mbedtls_aes_init(&ctx);
  mbedtls_aes_setkey_enc(&ctx, NETWORK_KEY, 128);
  uint8_t iv_copy[16];
  for (int i = 0; i < 16; i++) iv_copy[i] = random(256);
  size_t pl = ((len + 15) / 16) * 16;
  uint8_t pad[256];
  memset(pad, 0, pl);
  memcpy(pad, pt, len);
  memcpy(iv, iv_copy, 16);
  mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT, pl, iv, pad, ct);
  memcpy(iv, iv_copy, 16);
  mbedtls_aes_free(&ctx);
  return pl;
}
```

Quy trình mã hóa:
1. JSON payload → AES-128-CBC Encrypt → Ciphertext → LoRa/WiFi.
2. Sinh IV ngẫu nhiên 16 byte mỗi lần gửi.
3. Zero padding: làm tròn độ dài lên bội số 16, điền 0x00.
4. Đóng gói: [16 byte IV] + [ciphertext] → chuyển sang hex string.

Mã nguồn hiện tại dùng zero padding, phù hợp với JSON kết thúc bằng '}'. Không nên mô tả là PKCS#7 vì cơ chế khác nhau. Phiên bản triển khai thực tế có thể chuyển sang PKCS#7 cho tổng quát hơn.

CBC chỉ bảo vệ tính bí mật, không tạo mã xác thực. Nếu ciphertext bị sửa, plaintext giải mã cũng bị thay đổi; lỗi JSON có thể phát hiện một số trường hợp nhưng không phải kiểm tra toàn vẹn mật mã. Phiên bản triển khai thực tế cần HMAC hoặc chế độ mã hóa có xác thực (AES-GCM).

#### Giải mã phía đầu cuối

Quá trình giải mã thực hiện tại Server Flask (`server/app.py:24-37`):

```
P1 = AES^-1_K(C1) XOR IV
Pi = AES^-1_K(Ci) XOR C(i-1), i > 1
```

*Hình 2.13. Quá trình mã hóa và giải mã trong chế độ CBC*

Các bước giải mã:
1. Chuyển payload hex thành mảng byte; từ chối nếu có ký tự không hợp lệ.
2. Kiểm tra raw payload có ít nhất 32 byte và ciphertext chia hết cho 16.
3. Tách 16 byte đầu làm IV; phần còn lại làm ciphertext.
4. Khởi tạo AES-CBC bằng cùng key 16 byte.
5. Giải mã toàn bộ ciphertext.
6. Loại zero padding (`rstrip(b'\0')`).
7. Giải mã UTF-8 và parse JSON.
8. Kiểm tra id, seq và kiểu dữ liệu trước khi ghi DB.

```python
# File: server/app.py:24-37
def verify_and_decrypt(raw_data):
    iv = raw_data[:16]
    ciphertext = raw_data[16:]
    cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
    plaintext = cipher.decrypt(ciphertext).rstrip(b'\0')
    data = json.loads(plaintext.decode('utf-8'))
    return data, None
```

**Gateway có cần giải mã không?** Không. Gateway Y chỉ chuyển tiếp khung hex qua HTTP (`hardware/y_gateway/y_gateway.ino:81-96`), không có khóa AES, không tham gia các bước trên. Nếu Gateway giải mã rồi mã hóa lại, hệ thống phải cấp khóa cho Gateway — tạo thêm điểm lộ plaintext và phải quản lý IV/padding ở hai liên kết khác nhau. Đề tài chọn thiết kế **end-to-end encryption**: mã hóa tại node Xi, chỉ giải mã tại Server cuối.

#### Tổng kết lựa chọn

Trong số các phương án mã hóa, đề tài đã cân nhắc:

| Phương án | Tốc độ | Bảo mật | Code | Ghi chú |
|-----------|--------|---------|------|---------|
| XOR Cipher | Cực nhanh | Rất yếu | 3-5 dòng | Phù hợp demo, không dùng cho production |
| AES-128-CBC | Rất nhanh (HW accel) | Tốt (chuẩn NIST) | ~20 dòng | **Được chọn** |
| HMAC-SHA256 | Rất nhanh | Xác thực, không mã hóa | ~10 dòng | Không che giấu dữ liệu |

Do mức độ bảo mật của mạng IoT này không yêu cầu quá cao, trọng tâm là truyền tin giữa các thiết bị IoT, **AES-128-CBC với khóa tĩnh dùng chung toàn mạng** là lựa chọn phù hợp: vừa tận dụng hardware accelerator ESP32, vừa đảm bảo an toàn và tính chuyên nghiệp.

**Nguồn:**
- Nội dung AES và CBC: FIPS 197 [15], SP 800-38A [16].
- Code ESP32: `hardware/xi_node/xi_node.ino:76-91`, `wokwi/xi_01/sketch.ino:24-39`.
- Code Server: `server/app.py:24-37`.
- So sánh phương án: tài liệu tham khảo mã hóa (1-Mahoa.docx, 2-Mahoa2.docx).
