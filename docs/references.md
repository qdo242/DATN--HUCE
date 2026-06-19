# Tài liệu tham khảo

## 1. Tài liệu hướng dẫn đồ án (từ giảng viên)

- **[A]** *1-Mahoa.docx* — Tài liệu hướng dẫn mã hóa cơ bản, giới thiệu XOR Cipher và AES-128-CBC. File nằm tại thư mục gốc repository.
- **[B]** *2-Mahoa2.docx* — Tài liệu hướng dẫn mã hóa nâng cao, phân tích sâu hơn về cấu trúc gói tin bảo mật và cơ chế chống tấn công replay. File nằm tại thư mục gốc repository.

## 2. Tiêu chuẩn & tài liệu tham khảo kỹ thuật (công khai, có thể truy xuất online)

- **[1]** **FIPS 197** — *Advanced Encryption Standard (AES)*. National Institute of Standards and Technology (NIST). https://doi.org/10.6028/NIST.FIPS.197
- **[2]** **NIST SP 800-38A** — *Recommendation for Block Cipher Modes of Operation: Methods and Techniques*. NIST. https://doi.org/10.6028/NIST.SP.800-38A
- **[3]** **ESP32 Series Datasheet** — Espressif Systems. Dual-core Xtensa LX6, tích hợp AES hardware accelerator. https://www.espressif.com/en/support/documents/technical-documents
- **[4]** **Semtech SX1276/77/78/79 Datasheet** — Semtech Corporation. LoRa Modem, 137 MHz to 1020 MHz. https://www.semtech.com/products/wireless-rf/lora-connect/sx1278
- **[5]** **Mbed TLS** — Thư viện mật mã cho thiết bị nhúng, có sẵn trong ESP32 Arduino Core. https://github.com/Mbed-TLS/mbedtls
- **[6]** **PyCryptodome** — Thư viện mật mã Python, cung cấp `Crypto.Cipher.AES`. https://www.pycryptodome.org/
- **[7]** **Flask** — Micro web framework Python. https://flask.palletsprojects.com/
- **[8]** **Streamlit** — Dashboard framework Python. https://streamlit.io/
- **[9]** **Folium + Leaflet.js** — Thư viện bản đồ OpenStreetMap. https://python-visualization.github.io/folium/ — https://leafletjs.com/
- **[10]** **OWASP IoT Security Guidance** — Hướng dẫn bảo mật IoT. https://owasp.org/www-project-iot-security-guidance/

## 3. Code triển khai trong đồ án

| File | Vai trò | Nội dung chính |
|------|---------|----------------|
| `hardware/xi_node/xi_node.ino` | Firmware T-Beam | AES-CBC encrypt, LoRa Beacon/ACK/Data, đọc BME280+MAX30102+GPS |
| `hardware/y_gateway/y_gateway.ino` | Firmware Y Gateway | LoRa receive → HTTP POST lên Server |
| `wokwi/sketch.ino` | Mô phỏng Wokwi | Giả lập Xi node (random sensor, AES-CBC, HTTP POST) |
| `server/app.py` | Flask Server | AES-CBC decrypt, seq check, SQLite write, ThreadPoolExecutor |
| `server/init_db.py` | Khởi tạo DB | SQLite schema (bảng devices + telemetry), seed 3 devices (Xi_01, Xi_02, Y_01) |
| `server/dashboard.py` | Dashboard | Streamlit + Leaflet map (Mù Cang Chải) + biểu đồ + device list |
| `server/xor_cipher.py` | Tham khảo XOR | Mã hóa XOR với key `key_x_1234567890` |
| `server/main_test.py` | Test nhanh | Gửi 2 gói mẫu lên server, kiểm tra HTTP 200 |
| `server/simulator.py` | Mô phỏng node | Giả lập Xi_01 + Xi_02 gửi POST trực tiếp |
| `server/self_test_logic.py` | Tự kiểm tra | Kiểm tra AES-CBC, anti-replay, DB write |
| `server/verify_wokwi.py` | Xác minh Wokwi | Mô phỏng quy trình Wokwi (Beacon→ACK→Data→HTTP) |
| `server/final_check.py` | Kiểm tra tổng thể | Toàn bộ luồng hệ thống |
| `server/check_my_server.py` | Ping server | Gửi request kiểm tra server online |
| `docs/thesis.md` | Đề tài | Mô tả ngữ cảnh, nội dung công việc, phương án mã hóa |
| `docs/workflow.md` | Kiến trúc | Sơ đồ hệ thống, giao thức LoRa, DB schema |
| `docs/references.md` | Tham khảo | File này |
| `docs/benchmark.md` | Hiệu năng | 8 chỉ số đo, cách đo, kết quả dự kiến |
| `docs/threat_model.md` | Bảo mật | Mô hình hiểm họa, phân tích và phòng chống |
| `docs/research_encryption_comparison.md` | So sánh | XOR vs AES-128-CBC |
| `docs/research_anti_replay.md` | Chống replay | Sequence number |
| `docs/research_hmac_auth.md` | HMAC | Xác thực mở rộng |
| `docs/research_performance.md` | Hiệu năng | So sánh các phương án mã hóa |

## 4. Tham khảo phần cứng (GitHub, tutorial)

### TTGO T-Beam (ESP32 + LoRa SX1276 + GPS NEO-M8N + OLED)

- **[11]** **LilyGo-LoRa-Series** — Repository chính thức từ LilyGo, chứa mã nguồn và tài liệu cho các board LoRa (T-Beam, T3 v1.6/v1.7, T3 v1.0 LoRa 868M). https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series
- **[12]** **Lora-TTNMapper-T-Beam** — Dự án T-Beam TTNMapper: bản đồ LoRaWAN sử dụng T-Beam. https://github.com/TGM3D/Lora-TTNMapper-T-Beam
- **[13]** **ttgo-tbeam-sensor-node-bme280** — Node cảm biến T-Beam + BME280. https://github.com/kizniche/ttgo-tbeam-sensor-node-bme280
- **[14]** **rdz_ttgo_sonde — Supported displays** — Wiki danh sách màn hình hỗ trợ trên T-Beam (OLED SSD1306, SH1106...). https://github-wiki-see.page/m/dl9rdz/rdz_ttgo_sonde/wiki/Supported-displays
- **[15]** **TTGO-T-Beam-Car-Tracker** — Dự án tracker xe hơi dùng T-Beam. https://relatedrepos.com/gh/tekk/TTGO-T-Beam-Car-Tracker

### Thư viện cảm biến

- **[16]** **Adafruit BME280 Library** — Thư viện Arduino cho cảm biến BME280 (nhiệt độ, độ ẩm, áp suất), giao tiếp I2C/SPI. https://github.com/adafruit/Adafruit_BME280_Library
- **[17]** **Hướng dẫn BME280 Arduino** — Bài viết hướng dẫn sử dụng BME280 với ESP32/Arduino. https://randomnerdtutorials.com/bme280-sensor-arduino-pressure-temperature-humidity/
- **[18]** **SparkFun MAX3010x Sensor Library** — Thư viện Arduino cho cảm biến MAX30102 (nhịp tim, SpO2). https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library

## 5. Các lưu ý về trích dẫn

- Các tài liệu tham khảo **[A]**, **[B]** là file DOCX từ giảng viên hướng dẫn, nằm tại thư mục gốc `C:\Quan\ĐATN\`.
- Các tài liệu **[1]** đến **[10]** là tài liệu kỹ thuật công khai (NIST, datasheet, thư viện), có thể tra cứu trực tuyến.
- Các tài liệu **[11]** đến **[18]** do giảng viên cung cấp, liên quan đến phần cứng và thư viện sử dụng trong đồ án.
- Mọi thông tin chi tiết về code, giao thức, cấu hình đều được ghi trong các file của repository này (mục 3).
