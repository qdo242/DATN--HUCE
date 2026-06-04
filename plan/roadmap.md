# LỘ TRÌNH 16 TUẦN: GIẢI PHÁP TRUYỀN TIN BẢO MẬT IOT (Xi -> Y -> SERVER)

Tài liệu theo dõi tiến độ phối hợp giữa Tạ Huy Hoàng (Nội dung 1) và Đỗ Anh Quân (Nội dung 2).

---

## GIAI ĐOẠN 1: NGHIÊN CỨU VÀ THIẾT KẾ (Tuần 1 - 4) - HOÀN THÀNH

### Tạ Huy Hoàng (Phần cứng & Truyền thông)
- [x] Tìm hiểu về phần cứng: ESP32, module LoRa SX1278, GPS NEO-6M.
- [x] Nghiên cứu phương thức truyền tin Beacon/ACK trong mạng IoT.
- [x] Thử nghiệm gửi/nhận LoRa cơ bản trên mô phỏng.

### Đỗ Anh Quân (Mã hóa & Hệ thống)
- [x] Phân tích so sánh 2 phương án mã hóa: XOR Cipher và AES-128-CBC.
- [x] Thiết kế kiến trúc hệ thống tổng thể Xi, Y và Server trung tâm.
- [x] Thiết kế cấu trúc gói tin gửi từ Xi -> Y -> Server: `[16-byte IV] + [Ciphertext]`.

---

## GIAI ĐOẠN 2: THỰC THI BEACON VÀ MÃ HÓA (Tuần 5 - 8) - HOÀN THÀNH

### Tạ Huy Hoàng (Phần cứng & Truyền thông)
- [x] Thiết kế chi tiết định dạng gói tin Beacon (Xi) và ACK (Y).
- [x] **Viết code Xi:** Phát tín hiệu Beacon chờ kết nối.
- [x] **Viết code Y:** Quét Beacon và gửi tín hiệu ACK phản hồi.
- [x] Viết code Xi đo cảm biến (nhiệt độ, độ ẩm, CO, CO2, NH3) và GPS.
- [x] Viết code Xi gửi dữ liệu đã mã hóa cho Y.

### Đỗ Anh Quân (Mã hóa & Hệ thống)
- [x] Triển khai module mã hóa AES-128-CBC tại Xi và giải mã tại Server.
- [x] Xây dựng Flask Server tiếp nhận chuỗi Hex từ Gateway.
- [x] Viết module XOR cipher tham khảo (server/xor_cipher.py).

---

## GIAI ĐOẠN 3: TÍCH HỢP HỆ THỐNG VÀ WEB MAP (Tuần 9 - 12) - HOÀN THÀNH

### Tạ Huy Hoàng (Phần cứng & Truyền thông)
- [x] Code Xi đo cảm biến (Nhiệt độ, độ ẩm, CO, CO2, NH3).
- [x] Code Y chuyển tiếp dữ liệu về Server qua WiFi (mô phỏng).
- [x] Kiểm tra tính ổn định của luồng Beacon -> ACK -> Data.

### Đỗ Anh Quân (Mã hóa & Hệ thống)
- [x] Thiết lập Web Map (OpenStreetMap + Leaflet) qua Streamlit dashboard.
- [x] Hiển thị vị trí Xi và Y theo tọa độ GPS trên bản đồ.
- [x] Quản trị Cơ sở dữ liệu SQLite: Lưu trữ lịch sử cảm biến.
- [x] Cơ chế chống tấn công phát lại (Sequence Number).
- [x] Tài liệu so sánh 2 phương án mã hóa (XOR và AES-CBC).

---

## GIAI ĐOẠN 4: THỰC NGHIỆM VÀ HOÀN THIỆN (Tuần 13 - 16)

### Cả hai cùng thực hiện
- [ ] Lắp ráp phần cứng thật và đo đạc thực nghiệm ngoài môi trường.
- [ ] Phân tích kết quả truyền tin, chứng minh AES-CBC chạy nhanh (<20us) và ít tốn tài nguyên.
- [ ] Hoàn thiện cuốn báo cáo tốt nghiệp và Slide thuyết trình.
- [ ] Bảo vệ đồ án.

---
*Trọng tâm: Truyền tin nhanh, đơn giản, ít tài nguyên. Mã hóa dùng AES-128-CBC với Pre-Shared Key. So sánh với XOR Cipher trong thuyết minh.*
