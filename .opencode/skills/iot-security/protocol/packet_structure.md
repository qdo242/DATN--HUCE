# Packet Structure

## Current (AES-128-CBC)

| Offset | Field | Length | Description |
|--------|-------|--------|-------------|
| 0 | **IV** | 16 bytes | Random initialization vector |
| 16 | **Ciphertext** | Variable | AES-128-CBC encrypted JSON payload |

Payload sent as hex string: `(iv + ciphertext).hex()`

## Tham khao (AES-128-GCM + HMAC — Khong ap dung trong do an)

| Offset | Field | Length | Description |
|--------|-------|--------|-------------|
| 0 | **Gateway ID** | 4 bytes | e.g. `b"GW01"` |
| 4 | **Nonce** | 12 bytes | Random for AES-GCM |
| 16 | **Ciphertext** | Variable | AES-128-GCM encrypted data |
| End-48 | **Auth Tag** | 16 bytes | GCM authentication tag |
| End-32 | **Gateway HMAC** | 32 bytes | HMAC-SHA256 signature |

Ghi chu: Day la phuong an tham khao mo rong. Trong do an nay chi su dung AES-128-CBC, khong dung GCM hay HMAC.

## Plaintext JSON Format
```json
{
  "id": "Xi_01",
  "t": 28.5,
  "h": 65.2,
  "co2": 420,
  "co": 5.1,
  "nh3": 2.3,
  "lat": 21.00355,
  "lon": 105.84255,
  "seq": 1
}
```

## Encryption (AES-128-CBC)
```python
iv = secrets.token_bytes(16)
cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
padded = plaintext.ljust(padded_len, b'\0')
ciphertext = cipher.encrypt(padded)
# Send: (iv + ciphertext).hex()
```

## Decryption (Server)
```python
iv = raw_data[:16]
ciphertext = raw_data[16:]
cipher = AES.new(NETWORK_KEY, AES.MODE_CBC, iv=iv)
plaintext = cipher.decrypt(ciphertext).rstrip(b'\0')
data = json.loads(plaintext.decode('utf-8'))
```
