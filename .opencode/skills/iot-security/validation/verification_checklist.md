# Verification Checklist

## Unit Tests
- [ ] AES-128-CBC encrypt/decrypt roundtrip works
- [ ] Padding (NULL bytes) is correctly stripped on decrypt
- [ ] IV is random and different each encryption
- [ ] JSON parsing succeeds after decryption

## Integration Tests
- [ ] Flask server starts on port 5000
- [ ] `/receive-data` accepts POST with JSON payload
- [ ] SQLite database creates tables on init
- [ ] Data is persisted in `telemetry` table
- [ ] Streamlit dashboard renders at port 8501

## Security Tests
- [ ] Wrong key → "Decryption Failed" error
- [ ] Hex decode error → proper error response
- [ ] Empty payload → 400 "Missing payload"
- [ ] Packet too short → "Packet too short" error

## Wokwi Tests
- [ ] ESP32 boots in correct mode (Xi vs Gateway)
- [ ] AES encryption produces correct hex output
- [ ] WiFi connects to Wokwi-GUEST
- [ ] HTTP POST reaches server at 10.0.0.2:5000

## Performance Targets
- [ ] Server decryption < 50ms per packet
- [ ] Database write < 10ms per record
- [ ] ESP32 encryption < 20us (with hardware accelerator)

## Pre-Delivery
- [ ] `python server/verify_wokwi.py` confirms Wokwi-Server matching
- [ ] Dashboard shows correct device positions on Leaflet map
