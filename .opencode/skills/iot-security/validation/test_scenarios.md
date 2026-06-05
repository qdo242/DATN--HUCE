# Test Scenarios

## Prerequisites
```powershell
pip install -r requirements.txt
python server/init_db.py
```

## Scenario 1: Valid Data Transmission
```powershell
# Terminal 1: Server
python server/app.py

# Terminal 2: Test
python server/main_test.py
```
**Expected:** Server returns HTTP 200, data saved to SQLite.

## Scenario 2: Wokwi Simulation
1. Copy 3 file to https://wokwi.com (sketch.ino, diagram.json, wokwi.toml)
2. Start simulation
3. Observe serial output for HTTP 200

**Expected:** Beacon -> ACK -> AES encrypt -> HTTP POST 200

## Scenario 3: Verification Script
```powershell
python server/verify_wokwi.py
```
**Expected:** Confirms server and Wokwi config match.

## Attack Scenarios

### Wrong Key Test
Modify `NETWORK_KEY` in `server/app.py` -> Server returns 403 "Decryption Failed"

### Tampered Data Test
Flip a bit in the hex payload -> Decryption fails (padding error)

### Replay Test
Send same packet twice -> Server rejects second attempt (seq <= last_seq -> 403)
