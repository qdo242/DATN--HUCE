# Đo hiệu năng hệ thống

*Tham khảo: kết quả đo từ các file code trong repository (`server/app.py`, `wokwi/sketch.ino`, `server/simulator.py`); datasheet ESP32 [3], thư viện mbedtls [5] và PyCryptodome [6]*

## 1. Các chỉ số đo

| Chỉ số | Mô tả | Công cụ đo |
|--------|-------|------------|
| **Thời gian mã hóa AES-CBC** | Từ lúc gọi `aes_encrypt()` đến khi có ciphertext | `micros()` trên ESP32 [10], `time.time()` trên Python |
| **Thời gian giải mã AES-CBC** | Từ lúc nhận hex payload đến khi giải mã xong | Server log (tự động in sau mỗi request) |
| **Thời gian kiểm tra seq** | So sánh seq với last_seq trong DB | Server log |
| **Thời gian ghi DB** | INSERT telemetry vào SQLite | Server log |
| **Thời gian HTTP round-trip** | Từ lúc Xi POST đến khi nhận HTTP 200 | `millis()` trên ESP32 |
| **Thời gian LoRa (mô phỏng)** | delay() giữa các phase (Beacon/ACK/Data) | Code định sẵn |
| **Kích thước gói tin** | Plaintext vs ciphertext + IV + hex overhead | Serial output |
| **Throughput** | Số gói tin xử lý được mỗi giây | Đếm request/giây |

## 2. Cách đo

### Trên ESP32 (Wokwi / hardware)
Dùng `micros()` hoặc `millis()`:

```cpp
unsigned long t = micros();
size_t el = aes_encrypt((uint8_t*)json_buf, strlen(json_buf), ct, iv);
t = micros() - t;
Serial.printf("AES encrypt: %lu us\n", t);
```

### Trên Server (Flask)
Server tự động in thời gian sau mỗi request:
```
[+] Xi_01: decrypt=0.5ms seq=0.3ms log=0.8ms total=1.6ms
```
Server dùng `time.perf_counter()` trước và sau mỗi bước xử lý (xem code tại `server/app.py`).

### Benchmark script
Chạy `server/main_test.py` hoặc `server/simulator.py` và quan sát log.

## 3. Kết quả dự kiến (tham khảo từ datasheet và thực nghiệm mô phỏng)

| Chỉ số | Giá trị dự kiến | Ghi chú |
|--------|----------------|---------|
| AES-128-CBC encrypt (ESP32) | ~17-18 us | Hardware accelerator mbedtls (đo từ Wokwi simulation) |
| AES-128-CBC decrypt (Python) | ~0.3-0.5 ms | PyCryptodome (đo từ server log) |
| Kiểm tra seq (SQLite) | ~0.2-0.3 ms | Query đơn giản |
| Ghi telemetry (SQLite) | ~0.5-1.0 ms | INSERT |
| HTTP round-trip (local) | ~50-200 ms | Không qua localtunnel |
| HTTP round-trip (localtunnel) | ~150-500 ms | Qua localtunnel relay |
| LoRa Beacon→ACK (mô phỏng) | ~2.5s | delay() cố định |
| Throughput server | ~200-500 req/s | ThreadPoolExecutor 4 workers |
| Kích thước plaintext | ~180 byte | JSON 15 trường |
| Kích thước ciphertext hex | ~528 ký tự hex | 16 IV + 180 ciphertext + padding |
| Overhead mã hóa | ~2.9x | So với plaintext gốc |

## 4. Yếu tố ảnh hưởng

- Localtunnel: tăng latency HTTP (có thể +100-300ms so với local)
- Wokwi: chạy chậm hơn hardware thật (mô phỏng ESP32 chậm ~5-10x)
- SQLite: ghi đồng thời nhiều node có thể gây lock (đã xử lý bằng ThreadPoolExecutor)
- AES-CBC padding: dữ liệu ngắn bị pad lên bội số 16 byte (thêm tối đa 15 byte overhead)
