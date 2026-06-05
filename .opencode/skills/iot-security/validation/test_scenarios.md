# Test Scenarios

## Prerequisites
```powershell
pip install pycryptodomex flask streamlit pandas plotly requests python-dotenv
python server/init_db.py
```

## Scenario 1: Valid Data Transmission
```powershell
# Terminal 1: Server
python server/app.py

# Terminal 2: Test
python server/main_test.py
```
**Expected:** Server returns 200, Dashboard shows green data points.

## Scenario 2: Full Simulation (5 cycles)
```powershell
python server/simulator.py
```
**Expected:** Each device sends 5 data cycles, all stored in SQLite.

## Scenario 3: Independent Connectivity Test
```powershell
# Start server first, then:
python server/check_my_server.py
```
**Expected:** "THANH CONG! Server da giai ma duoc du lieu."

## Scenario 4: Wokwi-Server Matching
```powershell
python server/verify_wokwi.py
```
**Expected:** "CHUC MUNG: Cau hinh Wokwi va Server da khớp nối hoàn hảo!"

## Scenario 5: Internal Logic Test (GCM + HMAC)
```powershell
python server/self_test_logic.py
```
**Expected:** "Code Wokwi va Server da khớp nối thành công!"

## Scenario 6: Final Pre-Delivery Check
```powershell
python server/final_check.py
```
**Expected:** "He thong da san sang 100%."

## Attack Scenarios (Manual)

### Wrong Key Test
Modify `NETWORK_KEY` in test script → Server returns 403 with "Decryption Failed"

### Tampered Data Test
Flip a bit in the hex payload → Decryption fails (padding error or GCM tag mismatch)

### Replay Test
Send same packet twice → Server should reject second attempt (seq check)
