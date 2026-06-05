# Verification and Validation

## 1. Test Flow

### 1.1. Unit Test
- **Objective:** Verify AES-128-CBC encryption (ESP32) and decryption (Server) produce correct results.
- **Method:** Use `server/main_test.py` to send sample encrypted packets and check HTTP 200 response.

### 1.2. Integration Test
- **Objective:** Ensure full flow works: Xi → LoRa (simulated) → Y → HTTP POST → Server.
- **Method:** Run `main_test.py` — it sends 2 test packets and verifies server response.

### 1.3. Security Tests
- **Replay Attack:** Server checks `seq > last_seq`. Resending same packet returns HTTP 403.
- **Wrong Key:** Decryption fails → HTTP 403 "Decryption Failed".
- **Wrong Device ID:** Server checks device exists in DB → HTTP 403 "Device not found".

## 2. Wokwi Simulation

Copy 3 files to https://wokwi.com, start simulation. Observe serial output for:
- WiFi connection
- Beacon → ACK handshake
- AES encryption
- HTTP POST result (expect 200)

## 3. Cleanup

Delete `iot_security.db` and run `python server/init_db.py` to reset.
