# Encryption Scheme

## Lựa chọn: AES-128-CBC

Do mục tiêu chính là **truyền tin nhanh, đơn giản, ít tài nguyên**, đồ án chọn AES-128-CBC vì:
- ESP32 có hardware accelerator AES (tốc độ ~17-18us)
- Thư viện mbedtls có sẵn, code đơn giản
- Bảo mật đủ tốt cho ứng dụng IoT nghiên cứu

## Phương án tham khảo: XOR Cipher

Code 3-5 dòng, cực nhanh, không tốn RAM:
```python
def xor_encrypt(data, key):
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))
# Giải mã: xor_encrypt(data, key) (X XOR K) XOR K = X
```

## AES-128-CBC Implementation

### ESP32 (mbedtls):
```cpp
mbedtls_aes_context ctx;
mbedtls_aes_init(&ctx);
mbedtls_aes_setkey_enc(&ctx, NETWORK_KEY, 128);
for (int i = 0; i < 16; i++) iv[i] = random(256);
mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT, pl, iv, pad, ct);
```

### Python (Server):
```python
iv = secrets.token_bytes(16)
cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
ciphertext = cipher.encrypt(padded_plaintext)
```

## Packet Format
```
[16-byte IV] + [Ciphertext] → hex → POST JSON
```

## Key Management
- Pre-Shared Key toàn mạng: `b'key_x_1234567890'` (16 bytes)
- Nếu 1 node bị lộ key → toàn mạng bị lộ
- Chấp nhận được do môi trường phòng lab, trọng tâm là truyền tin IoT
