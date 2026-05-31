# LỘ TRÌNH 16 TUẦN: ĐỒ ÁN MẬT MÃ HÓA IOT PAYLOAD

Tài liệu này dùng để theo dõi tiến độ thực hiện đồ án. Các hạng mục đã hoàn thành được đánh dấu [x].

---

## GIAI ĐOẠN 1: NGHIÊN CỨU VÀ XÂY DỰNG NỀN TẢNG (Tuần 1 - 4) - ĐÃ HOÀN THÀNH

- [x] Nghiên cứu thuyết minh về Mã hóa tầng ứng dụng (AES-GCM) thay thế cho các giải pháp lớp dưới.
- [x] Thiết kế kiến trúc hệ thống tổng thể (Node X, Node Y, Gateway, Server).
- [x] Thiết kế cấu trúc gói tin nhị phân tối ưu băng thông.
- [x] Triển khai module mã hóa và giải mã cốt lõi bằng Python.
- [x] Xây dựng Flask Server hỗ trợ nhận dữ liệu JSON và chuỗi Hex.
<!-- - [x] Triển khai giải pháp bảo mật Node-to-Node và Gateway-to-Server (HMAC).  -->
- [x] Xây dựng Dashboard giám sát cơ bản.

---

## GIAI ĐOẠN 2: CHUYÊN NGHIỆP HÓA VÀ QUẢN LÝ DỮ LIỆU (Tuần 5 - 8) - ĐÃ HOÀN THÀNH

### Tuần 5: Hệ quản trị cơ sở dữ liệu và Quản lý thiết bị
- [x] Chuyển đổi lưu trữ từ file JSON sang SQLite Database.
- [x] Triển khai bảng quản lý thiết bị để cấp khóa riêng cho từng Node IoT.
- [x] Nâng cấp Dashboard với biểu đồ dữ liệu thời gian thực (Line Chart, Pie Chart).
- [x] Xây dựng module đo đạc độ trễ (Latency) từ đầu cuối đến đầu cuối. (Thêm)

### Tuần 6: Phân tích an ninh và Giám sát nâng cao
- [x] Triển khai bảng nhật ký chi tiết các nỗ lực tấn công (loại tấn công, thời điểm).
- [x] Bổ sung tính năng: Tự động chặn thiết bị nếu vi phạm quy tắc an ninh quá số lần quy định.
- [x] Hiển thị trạng thái kết nối và health của từng Node trên Dashboard.

### Tuần 7: Quản trị hệ thống qua giao diện Web
- [x] Xây dựng giao diện quản lý để thao tác danh sách thiết bị và khóa mật mã (CRUD).
- [x] Tích hợp tính năng xuất báo cáo dữ liệu dưới dạng CSV phục vụ phân tích. (Thêm)
- [ ] Triển khai hệ thống cảnh báo qua Email/Telegram khi phát hiện tấn công nghiêm trọng (Chưa cấu hình API Key).(Thêm)
 
### Tuần 8: Kiểm định an ninh và Ổn định hệ thống
- [ ] Kiểm tra khả năng chịu tải của Server Flask khi nhận dữ liệu liên tục.
- [ ] Tối ưu hóa truy vấn cơ sở dữ liệu để đảm bảo tốc độ xử lý.
- [ ] Viết tài liệu mô tả các kịch bản tấn công đã được ngăn chặn thành công.

---

## GIAI ĐOẠN 3: MẬT MÃ HỌC NÂNG CAO (Tuần 9 - 12) (Nâng cao- Tham khảo)

### Tuần 9 - 10: Giao thức trao đổi khóa động (ECDH)
- [ ] Nghiên cứu và triển khai thuật toán Elliptic Curve Diffie-Hellman (X25519).
- [ ] Xây dựng quy trình bắt tay (Handshake) để tự động thỏa thuận khóa phiên (Session Key).
- [ ] Loại bỏ hoàn toàn việc sử dụng khóa tĩnh (Static Key) trong truyền thông.

### Tuần 11 - 12: Xoay vòng khóa và Bảo mật phía trước (Forward Secrecy)
- [ ] Triển khai cơ chế đổi khóa tự động (Key Rotation) theo phiên hoặc theo thời gian.
- [ ] Kiểm chứng tính chất bảo mật phía trước (Perfect Forward Secrecy) của hệ thống.
- [ ] Viết chương trình tự động đánh giá độ an toàn mật mã.

---

## GIAI ĐOẠN 4: TÍCH HỢP PHẦN CỨNG VÀ HOÀN THIỆN (Tuần 13 - 16)

### Tuần 13 - 14: Firmware C++ và Tối ưu hóa ESP32
- [x] Viết mã nguồn C++ mẫu cho ESP32 sử dụng thư viện mbedtls (Chạy trên Wokwi).
- [ ] Tận dụng bộ tăng tốc phần cứng AES trên chip ESP32 để tối ưu tốc độ.
- [ ] Triển khai kịch bản truyền thông thực tế giữa 2 thiết bị ESP32 qua Gateway.

### Tuần 15: Đo đạc và Phân tích thực nghiệm
- [ ] Đo đạc chỉ số RAM, Flash và năng lượng tiêu thụ trên phần cứng thực tế.
- [ ] So sánh thực nghiệm hiệu năng với các giải pháp bảo mật tiêu chuẩn khác.
- [ ] Tổng hợp biểu đồ so sánh dữ liệu để đưa vào báo cáo cuối cùng.

### Tuần 15- 16: Hoàn thiện báo cáo và Bảo vệ đồ án
- [ ] Hoàn thiện nội dung cuốn báo cáo tốt nghiệp.
- [ ] Chuẩn bị slide thuyết trình và video minh họa hệ thống.
- [ ] Kiểm tra cuối cùng toàn bộ hệ thống trước khi hội đồng đánh giá.

---
*Lưu ý: Lộ trình này sẽ được cập nhật liên tục tùy theo tiến độ thực tế.*
