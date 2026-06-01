# Đề tài: Xây dựng giải pháp truyền tin bảo mật giữa các thiết bị IoT

## 1. Mô tả ngữ cảnh bài toán
Hệ thống bao gồm các thiết bị IoT $X_i$ triển khai cố định và thiết bị di động $Y$ (Gateway).

**Quy trình hoạt động:**
- **Giai đoạn 1 (Beacon/ACK):** Các $X_i$ phát tín hiệu Beacon qua LoRa. Khi $Y$ đến gần và nhận được Beacon, $Y$ sẽ gửi lại tín hiệu ACK.
- **Giai đoạn 2 (Truyền tin bảo mật):** Sau khi nhận ACK, $X_i$ thu thập dữ liệu (Nhiệt độ, độ ẩm, CO, CO2, NH3) và tọa độ GPS, mã hóa dữ liệu và gửi về $Y$.
- **Giai đoạn 3 (Chuyển tiếp & Hiển thị):** $Y$ chuyển tiếp dữ liệu bảo mật về Server. Server giải mã, lưu trữ và hiển thị vị trí các thiết bị lên Web Map (OpenStreetMap + Leaflet).

## 2. Phân công nhiệm vụ
- **Nội dung công việc 1 (Tạ Huy Hoàng):**
    - Lắp ráp phần cứng (ESP32, LoRa SX1278, GPS, cảm biến).
    - Thiết kế và lập trình quy trình Beacon/ACK.
    - Chuyển tiếp dữ liệu từ Gateway về Server.
- **Nội dung công việc 2 (Đỗ Anh Quân):**
    - Nghiên cứu giải pháp mã hóa dữ liệu (XOR và AES-128-CBC). Lựa chọn AES-CBC kết hợp tăng tốc phần cứng ESP32.
    - Thiết kế kiến trúc hệ thống và cấu trúc gói tin $X_i \rightarrow Y \rightarrow$ Server.
    - Xây dựng Flask Server, Database và Web Map hiển thị.

## 3. Công nghệ sử dụng
- **Phần cứng:** ESP32, LoRa SX1278, GPS NEO-6M, BME280, cảm biến khí.
- **Mật mã:** AES-128-CBC (Pre-Shared Key toàn mạng).
- **Backend:** Flask, SQLite.
- **Frontend:** Streamlit, Leaflet.js, OpenStreetMap.
