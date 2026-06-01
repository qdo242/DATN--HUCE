# LỘ TRÌNH 16 TUẦN: GIẢI PHÁP TRUYỀN TIN BẢO MẬT IOT (Xi -> Y -> SERVER)

Tài liệu theo dõi tiến độ phối hợp giữa Tạ Huy Hoàng (Nội dung 1) và Đỗ Anh Quân (Nội dung 2).

---

## 🟢 GIAI ĐOẠN 1: NGHIÊN CỨU VÀ THIẾT KẾ (Tuần 1 - 4) - HOÀN THÀNH

### Tạ Huy Hoàng (Phần cứng & Truyền thông)
- [x] Tìm hiểu về phần cứng: ESP32, module LoRa SX1278, GPS NEO-6M.
- [x] Nghiên cứu phương thức truyền tin Beacon/ACK trong mạng IoT.
- [x] Thử nghiệm gửi/nhận LoRa cơ bản trên mô phỏng.

### Đỗ Anh Quân (Mã hóa & Hệ thống)
- [x] Phân tích so sánh 2 phương án mã hóa nhẹ: XOR Cipher và AES-128-CBC.
- [x] Thiết kế kiến trúc hệ thống tổng thể Xi, Y và Server trung tâm.
- [x] Thiết kế cấu trúc gói tin gửi từ Xi -> Y -> Server: `[16-byte IV] + [Ciphertext]`.

---

## 🔵 GIAI ĐOẠN 2: THỰC THI BEACON VÀ MÃ HÓA (Tuần 5 - 8) - ĐANG THỰC HIỆN

### Tạ Huy Hoàng (Phần cứng & Truyền thông)
- [x] Thiết kế chi tiết định dạng gói tin Beacon (Xi) và ACK (Y).
- [x] **Viết code Xi:** Phát tín hiệu Beacon chờ kết nối.
- [x] **Viết code Y:** Quét Beacon và gửi tín hiệu ACK phản hồi.
- [ ] Tích hợp đọc dữ liệu GPS từ module thực tế.

### Đỗ Anh Quân (Mã hóa & Hệ thống)
- [x] Lựa chọn thuật toán AES-128-CBC để tận dụng Hardware Accelerator của ESP32.
- [x] Triển khai module mã hóa tại Xi và giải mã tại Server bằng Python.
- [x] Xây dựng Flask Server tiếp nhận chuỗi Hex từ Gateway.

---

## 🟡 GIAI ĐOẠN 3: TÍCH HỢP HỆ THỐNG VÀ WEB MAP (Tuần 9 - 12)

### Tạ Huy Hoàng (Phần cứng & Truyền thông)
- [ ] Hoàn thiện Code Xi: Đo cảm biến (Nhiệt độ, độ ẩm, CO, CO2, NH3).
- [ ] Hoàn thiện Code Y: Chuyển tiếp dữ liệu về Server qua Wi-Fi/4G/5G.
- [ ] Kiểm tra tính ổn định của luồng Beacon -> ACK -> Data.

### Đỗ Anh Quân (Mã hóa & Hệ thống)
- [ ] Thiết lập Web Map chuyên nghiệp (OpenStreetMap + Leaflet).
- [ ] Hiển thị vị trí Xi theo đúng tọa độ gốc, không để nhảy ngẫu nhiên phi lý.
- [ ] Quản trị Cơ sở dữ liệu SQLite: Lưu trữ lịch sử cảm biến.

---

## 🔴 GIAI ĐOẠN 4: THỰC NGHIỆM VÀ HOÀN THIỆN (Tuần 13 - 16)

### Cả hai cùng thực hiện
- [ ] Lắp ráp phần cứng thật và đo đạc thực nghiệm ngoài môi trường.
- [ ] Phân tích kết quả truyền tin, chứng minh AES-CBC chạy nhanh (<20us) và ít tốn tài nguyên.
- [ ] Hoàn thiện cuốn báo cáo tốt nghiệp và Slide thuyết trình.
- [ ] Bảo vệ đồ án.

---
*Lưu ý: Không đi sâu vào mật mã nâng cao, tập trung vào quy trình truyền tin nhanh, gọn nhẹ theo sát tài liệu tham khảo.*
