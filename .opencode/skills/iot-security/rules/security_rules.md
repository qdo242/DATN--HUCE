# Security Rules

## Threat Model
| Attack | Defense | Status |
|--------|---------|--------|
| Eavesdropping | AES-128 encryption | Implemented |
| Data Tampering | GCM Auth Tag (future) / HMAC (future) | In progress |
| Replay Attack | Sequence Number in encrypted payload | In progress |
| Impersonation | Gateway HMAC signature | In progress |

## Critical Rules

### 1. IV/Nonce MUST be random per transmission
```python
# Correct
iv = secrets.token_bytes(16)

# Wrong
iv = b'\x00' * 16  # Static IV breaks CBC security
```

### 2. Sequence Number MUST be inside encrypted payload
- If seq is outside ciphertext, attacker can modify it
- Inside ciphertext → any change invalidates GCM tag

### 3. Server MUST verify before decrypting (future)
```
1. Check packet length ≥ minimum
2. Verify HMAC signature (reject if invalid)
3. Decrypt payload
4. Check sequence number > last_seq (reject replay)
5. Store in database
```

### 4. No hardcoded secrets in production
```python
# Development only
NETWORK_KEY = b'key_x_1234567890'

# Production: load from environment
import os
NETWORK_KEY = os.environ.get('NODE_KEY', '').encode()
if len(NETWORK_KEY) != 16:
    raise ValueError("Invalid key length")
```
