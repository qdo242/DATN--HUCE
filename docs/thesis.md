# Đề tài: Xây dựng giải pháp truyền tin bảo mật giữa các thiết bị IoT

## Mô tả ngữ cảnh bài toán

- Các thiết bị IoT Xi đã được rải sẵn ở môi trường dùng các cảm biến để đo các tham số nhiệt độ, độ ẩm, CO, CO2, NH3,…
- Các thiết bị Xi sử dụng module LoRa để liên tục phát tín hiệu Beacon (gói tin rất nhỏ) chờ kết nối với Gateway.
- Một người dùng mang theo 1 thiết bị IoT Y (Gateway) khi đến vùng phủ sóng của các Xi sẽ nhận được tín hiệu Beacon của các Xi. Khi đó Y trả lời bằng 1 tín hiệu ACK báo cho Xi biết tôi đã nhận được Beacon.
- Sau khi nhận được tin báo của Y, các Xi sẽ lần lượt gửi các bản tin kèm dữ liệu có mã hóa từ các cảm biến trên đồng thời tọa độ GPS về Y.
- Thiết bị Y chuyển tiếp dữ liệu có bảo mật về server trung tâm.
- Server trung tâm hiển thị dữ liệu của các Xi và Y lên Web Map.

## Nội dung công việc 1 — Phần cứng & LoRa

1. Lắp ráp phần cứng IoT: chọn ESP32 (Development), mô đun LoRa (chọn tương đương SX1278 tần số 433 MHz), GPS, cảm biến nhiệt độ, độ ẩm, 1 vài cảm biến khí quan trọng.
2. Tìm hiểu LoRa, phương thức truyền tin.
3. Thử nghiệm gửi và nhận tín hiệu LoRa giữa 2 thiết bị IoT (X và Y).
4. Tìm hiểu cách phát Beacon = Thiết kế gói tin Beacon và ACK cho Xi và Y.
5. Viết Code Xi gửi Beacon, chờ ACK từ Y. Viết Code Y quét Beacon phát hiện có nhận được Beacon từ Xi.
6. Viết Code Xi đo cảm biến, dữ liệu GPS.
7. Viết Code Xi gửi dữ liệu cho Y.
8. Viết Code Y chuyển tiếp dữ liệu về Server trung tâm qua kết nối 4G/5G / WiFi.

## Nội dung công việc 2 — Bảo mật & Server

1. Nghiên cứu Tìm hiểu về mã hóa dữ liệu (cách đơn giản dùng Key).
2. Thiết kế kiến trúc hệ thống gồm các Xi, Y và Server trung tâm, các luồng dữ liệu.
3. Thiết kế cấu trúc gói tin gửi từ Xi → Y → Server.
4. Viết Code phần mã hóa bảo mật và giải mã.
5. Tích hợp mã hóa vào Gateway.
6. Dựng Flask Server, nhận dữ liệu kiểu JSON từ Gateway.
7. Viết Code Server trung tâm nhận dữ liệu từ Y (Gateway) và tổng hợp dữ liệu, lưu Cơ sở dữ liệu.
8. Thiết lập Map (OpenStreetMap + Leaflet) – Hiển thị vị trí các Xi và Y lên Map.

## Yêu cầu của thầy

> "Mạng IoT này mục đích chính là truyền tin, yêu cầu nhanh, đơn giản nhất, ít tốn tài nguyên nhất, mức độ bảo mật không quá cao."
