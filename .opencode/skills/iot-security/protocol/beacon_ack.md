# Beacon/ACK Handshake Protocol

## Overview
3-phase protocol between IoT Nodes (Xi) and Gateway (Y):

```
Xi → (Beacon) → Y
Xi ← (ACK) ← Y
Xi → (Encrypted Data) → Y → Server
```

## Phase 1: Beacon
- **Sender:** Xi (Sensor Node)
- **Medium:** LoRa SX1278 (433 MHz)
- **Content:** Device ID + readiness signal
- **Behavior:** Broadcast periodically until ACK received

## Phase 2: ACK
- **Sender:** Y (Gateway)
- **Trigger:** Upon receiving valid Beacon
- **Content:** Acknowledgment signal
- **Effect:** Confirms connection, triggers data transmission

## Phase 3: Data Transmission
- **Sender:** Xi
- **Content:** AES-128-CBC encrypted JSON payload
- **Format:** `[16-byte IV] + [Ciphertext]` as hex
- **Receiver:** Y forwards to Server via WiFi/4G

## Simulated Flow (server/simulator.py)
```python
# Phase 1
print(f"[{device_id}] Phat Beacon LoRa...")
# Phase 2
print(f"[GATEWAY Y] Nhan Beacon tu {device_id}, gui ACK")
print(f"[{device_id}] Nhan ACK, bat dau truyen tin.")
# Phase 3: Encrypt & send
payload_hex = (iv + ciphertext).hex()
requests.post(SERVER_URL, json={"payload": payload_hex})
```

## Wokwi Implementation (wokwi/sketch.ino)
- GPIO4: LOW = Xi mode, HIGH = Y (Gateway) mode
- Xi: sends Beacon via Serial, waits for ACK
- Xi: reads sensors, encrypts with `aes_encrypt()`
- Y: connects WiFi, forwards hex payload to `10.0.0.2:5000`
