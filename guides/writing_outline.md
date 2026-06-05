# BỐ CỤC NỘI DUNG VIẾT (THESIS OUTLINE)

Dưới đây là khung sườn bài viết chi tiết cho Tạ Huy Hoàng và Đỗ Anh Quân.

---

## PHẦN 1: TẠ HUY HOÀNG (Nội dung công việc 1)
**Chủ đề: Thực thi phần cứng và Giao thức truyền tin Beacon/LoRa**

### Chương 1: Nghiên cứu phần cứng IoT
- 1.1. Tổng quan về ESP32 và tập lệnh xử lý.
- 1.2. Module truyền tin LoRa SX1278 (Tần số 433MHz).
- 1.3. Hệ thống định vị toàn cầu GPS NEO-6M.
- 1.4. Tập cảm biến khí (CO, CO2, NH3) và cơ chế đo đạc.

### Chương 2: Thiết kế Giao thức Handshake (Beacon/ACK)
- 2.1. Phân tích gói tin Beacon của thiết bị Xi.
- 2.2. Phân tích gói tin ACK của thiết bị Y (Gateway).
- 2.3. Giải thuật máy trạng thái (State Machine) cho quá trình quét và phản hồi.
- 2.4. Thực thi quy trình gửi dữ liệu sau Handshake thành công.

### Chương 3: Chuyển tiếp dữ liệu (Relay)
- 3.1. Cơ chế nhận dữ liệu từ LoRa và chuyển đổi sang chuẩn Wi-Fi/4G.
- 3.2. Đóng gói dữ liệu định dạng JSON để gửi lên Server trung tâm.

---

## PHẦN 2: ĐỖ ANH QUÂN (Nội dung công việc 2)
**Chủ đề: Giải pháp mã hóa dữ liệu, Server và Hiển thị Web Map**

### Chương 1: Nghiên cứu giải pháp mã hóa dữ liệu IoT
- 1.1. Đặt vấn đề: Tại sao cần mã hóa Payload thay vì dùng TLS cho LoRa?
- 1.2. Lựa chọn thuật toán mã hóa đối xứng AES-128-CBC.
- 1.3. Thiết kế cấu trúc gói tin bảo mật (IV + AES-CBC ciphertext + Sequence Number).

### Chương 2: Xây dựng Hệ thống Backend trung tâm
- 2.1. Triển khai Flask Server tiếp nhận yêu cầu từ Gateway.
- 2.2. Xây dựng bộ giải mã và kiểm tra tính toàn vẹn tại Server.
- 2.3. Thiết kế Cơ sở dữ liệu SQLite lưu trữ lịch sử telemetry và nhật ký an ninh.

### Chương 3: Xây dựng giao diện Web Map và Giám sát
- 3.1. Tích hợp OpenStreetMap và Leaflet.js vào Dashboard.
- 3.2. Thuật toán hiển thị vị trí thiết bị Xi và Y theo tọa độ GPS thời gian thực.
- 3.3. Biểu đồ thống kê các tham số môi trường.

---
*Lưu ý: Các phần lý thuyết sẽ được viết ngắn gọn, tập trung sâu vào phần Thực thi (Implementation) và Hình ảnh minh họa code.*
