# Testing Workflow

## Standard Test Sequence
Run in order:

### Step 1: Clean state
```powershell
# Stop all server processes
python server/init_db.py  # Reset database
```

### Step 2: Start server
```powershell
python server/app.py
```

### Step 3: Run verification suite
```powershell
# Terminal 2: Basic test
python server/main_test.py

# Terminal 2: Full simulation
python server/simulator.py

# Terminal 2: Self-test logic
python server/self_test_logic.py

# Terminal 2: Wokwi verification
python server/verify_wokwi.py

# Terminal 2: Final check
python server/final_check.py
```

### Step 4: Visual verification
```powershell
streamlit run server/dashboard.py
```
Open `http://localhost:8501` to verify:
- Sensor charts update with new data
- Leaflet map shows correct device positions
- Device table lists all 3 devices

## Attack Simulation
```powershell
# Run with invalid key
# Edit main_test.py: change NETWORK_KEY
# Expected: 403 Decryption Failed

# Run replay test
# Send same packet twice
# Expected: Second request rejected (seq check)
```

## Cleanup
```powershell
# Reset database between test runs
python server/init_db.py

# Kill any process on port 5000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
```
