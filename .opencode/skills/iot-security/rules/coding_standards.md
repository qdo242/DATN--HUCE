# Coding Standards

## Python (Server)
- **Style:** PEP 8
- **Imports:** Standard lib → Third-party → Local (grouped)
- **Error handling:** Use try/except with specific exceptions
- **Logging:** Use `print()` for server logging
- **Secrets:** Use `secrets.token_bytes()` for IV/Nonce generation
- **DB:** Use parameterized queries, never f-strings

## C++ (ESP32/Wokwi)
- **Style:** Arduino convention
- **Serial:** Use `Serial.printf()` for formatted output
- **Encryption:** Use mbedtls library (built-in ESP32)
- **Memory:** Always `free()` after `calloc()`
- **WiFi:** Use `WiFi.begin()` with Wokwi-GUEST network

## Crypto Rules
- Never reuse (Key, IV/Nonce) pair
- Use `secrets` module for randomness (not `random`)
- Pad plaintext with NULL bytes (`\0`) for CBC mode
- Verify ciphertext length before decryption (`len < 32` → reject)
- Do an nay dung 1 Pre-Shared Key hardcode cho ca mang (thuan tien cho nghien cuu)

## Git
- Don't commit `__pycache__/`
- Don't commit `iot_security.db` (auto-generated)
