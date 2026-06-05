# Testing Workflow

## Standard Test Sequence

### Step 1: Clean state
```powershell
python server/init_db.py  # Reset database
```

### Step 2: Start server
```powershell
python server/app.py
```

### Step 3: Run tests (Terminal 2)
```powershell
python server/main_test.py      # Basic test (2 packets)
python server/verify_wokwi.py   # Verify Wokwi config
```

### Step 4: Dashboard verification
```powershell
streamlit run server/dashboard.py
```
Open `http://localhost:8501` to verify:
- Sensor charts update with new data
- Leaflet map shows correct device positions

## Attack Simulation
```powershell
# Wrong key test
# Edit main_test.py: change NETWORK_KEY
# Expected: 403 Decryption Failed

# Replay test
# Send same packet twice
# Expected: Second request rejected (seq <= last_seq)
```

## Cleanup
```powershell
# Reset database between test runs
python server/init_db.py

# Kill any process on port 5000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
```
