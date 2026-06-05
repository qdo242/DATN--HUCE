# Wokwi Simulation Reference

## Diagram
File: `wokwi/diagram.json`
- 2x ESP32 DevKit v1 (esp_xi, esp_y)
- Serial monitor connections
- GPIO4 pull-down for mode detection

## Firmware
File: `wokwi/sketch.ino`

### Mode Detection (GPIO4)
```
LOW  → Xi_01 (Sensor Node)
HIGH → Y_GW  (Gateway)
```

### Xi Mode Flow
1. Print "BEACON" via Serial
2. Wait 2s (simulated LoRa)
3. Read "ACK" from Gateway
4. Generate sensor data (t, h, co2, GPS)
5. Encrypt with AES-128-CBC
6. Forward to Y via simulated LoRa

### Gateway Mode Flow
1. Connect to WiFi "Wokwi-GUEST"
2. Listen for LoRa packets (simulated)
3. Convert to hex and forward to server
4. POST to `http://10.0.0.2:5000/receive-data`

### AES Encryption (mbedtls)
```cpp
mbedtls_aes_context ctx;
mbedtls_aes_init(&ctx);
mbedtls_aes_setkey_enc(&ctx, NETWORK_KEY, 128);
mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT, pl, iv, pad, ct);
```

### Key (from ascii to hex array)
`"key_x_1234567890"` → `{0x6B, 0x65, 0x79, 0x5F, 0x78, 0x5F, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30}`

## Wokwi Config
File: `wokwi/wokwi.toml`
```toml
[wokwi]
version = 1
firmware = 'sketch.ino'
diagram = 'diagram.json'
```
