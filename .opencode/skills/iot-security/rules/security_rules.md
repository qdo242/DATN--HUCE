# Security Rules

## Threat Model
| Attack | Defense | Status |
|--------|---------|--------|
| Nghe len (Eavesdropping) | AES-128-CBC ma hoa payload | Implemented |
| Tan cong phat lai (Replay) | Sequence Number trong payload ma hoa | Implemented |
| Gia mao (Impersonation) | Can bi key moi ma hoa duoc | Implemented |
| Sua doi du lieu (Tampering) | CBC decryption se fail neu du lieu bi sua | Implemented |

## Critical Rules

### 1. IV MUST be random per transmission
```python
# Correct
iv = random_bytes(16)

# Wrong - Static IV breaks CBC security
iv = b'\x00' * 16
```

### 2. Sequence Number MUST be inside encrypted payload
- If seq is outside ciphertext, attacker can modify it
- Inside ciphertext -> any change causes decryption to fail

### 3. Server processing order
```
1. Decrypt payload with AES-128-CBC
2. Parse JSON
3. Check sequence number > last_seq (reject replay)
4. Store in database
```

### 4. Key configuration
```python
# Single Pre-Shared Key for whole network
NETWORK_KEY = b'key_x_1234567890'
```
