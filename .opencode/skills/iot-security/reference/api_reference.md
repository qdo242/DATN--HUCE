# API Reference

## Endpoint: `/receive-data`
- **Method:** POST
- **Content-Type:** `application/json`
- **Server:** `http://127.0.0.1:5000`
- **Wokwi:** `http://10.0.0.2:5000`

### Request
```json
{
  "payload": "<hex_encoded_iv_plus_ciphertext>"
}
```

### Success Response (200)
```json
{
  "status": "success",
  "device": "Xi_01"
}
```

### Error Responses
```json
// 400 - Missing payload
{ "status": "error", "message": "Missing payload" }

// 403 - Decryption failed
{ "status": "error", "reason": "Decryption Failed: ..." }

// 400 - Invalid hex
{ "status": "error", "message": "..." }
```

## Server Files
| File | Endpoint/Usage |
|------|---------------|
| `app.py` | `/receive-data` POST handler |
| `init_db.py` | `python server/init_db.py` |
| `dashboard.py` | `streamlit run server/dashboard.py` (port 8501) |
| `main_test.py` | Sends 2 test packets |
| `check_my_server.py` | Independent connectivity test |
