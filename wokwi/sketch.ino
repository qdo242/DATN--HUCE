#include <WiFi.h>
#include <HTTPClient.h>
#include <mbedtls/aes.h>

#define PIN_X 4

const uint8_t NETWORK_KEY[16] = {
  0x6B, 0x65, 0x79, 0x5F, 0x78, 0x5F, 0x31, 0x32,
  0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30
};

char device_id[20];
bool is_xi = false, is_gateway = false;
float lat = 21.00355, lon = 105.84255;
int seq = 1;
char json_buf[512];

static size_t aes_encrypt(uint8_t* pt, size_t len, uint8_t* ct, uint8_t* iv) {
  mbedtls_aes_context ctx;
  mbedtls_aes_init(&ctx);
  mbedtls_aes_setkey_enc(&ctx, NETWORK_KEY, 128);
  for (int i = 0; i < 16; i++) iv[i] = random(256);
  size_t pl = ((len + 15) / 16) * 16;
  uint8_t* pad = (uint8_t*)calloc(pl, 1);
  if (!pad) { mbedtls_aes_free(&ctx); return 0; }
  memcpy(pad, pt, len);
  mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT, pl, iv, pad, ct);
  mbedtls_aes_free(&ctx);
  free(pad);
  return pl;
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n========== BOOT ==========");

  pinMode(PIN_X, INPUT_PULLUP);
  delay(50);

  if (digitalRead(PIN_X) == LOW) {
    strcpy(device_id, "Xi_01");
    is_xi = true;
    Serial.println("MODE: XI (Sensor Node)");
  } else {
    strcpy(device_id, "Y_GW");
    is_gateway = true;
    Serial.println("MODE: GATEWAY");
  }

  if (is_gateway) {
    WiFi.begin("Wokwi-GUEST", "");
    Serial.print("WiFi");
    int w = 0;
    while (WiFi.status() != WL_CONNECTED && w < 30) {
      delay(500); Serial.print(".");
      w++;
    }
    Serial.println(w < 30 ? " OK" : " FAIL");
    if (WiFi.status() == WL_CONNECTED)
      Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
  }

  if (is_xi) delay(2000);
  Serial.println("========== READY ==========\n");
}

void loop() {
  if (is_xi) {
    // === GIAI DOAN 1: BEACON ===
    Serial.println("\n=== BEACON ===");
    Serial.printf("[%s] => Phat Beacon (LoRa simulated)\n", device_id);
    delay(2000);

    // === GIAI DOAN 2: NHAN ACK ===
    Serial.printf("[Y_GW] => Nhan Beacon, gui ACK\n");
    Serial.printf("[%s] => Nhan ACK, bat dau truyen\n", device_id);
    delay(1000);

    // === GIAI DOAN 3: DOC CAM BIEN ===
    float t = 28.0 + random(-30, 30) / 10.0;
    float h = 60.0 + random(-20, 20) / 10.0;
    float c2 = 400 + random(50);
    lat += 0.0001; lon += 0.0001;
    Serial.printf("[%s] Temp=%.1f Humi=%.1f CO2=%.0f GPS=%.5f,%.5f\n",
      device_id, t, h, c2, lat, lon);

    // === GIAI DOAN 4: MA HOA ===
    snprintf(json_buf, sizeof(json_buf),
      "{\"id\":\"%s\",\"t\":%.1f,\"h\":%.1f,\"co2\":%.0f,\"lat\":%.5f,\"lon\":%.5f,\"seq\":%d}",
      device_id, t, h, c2, lat, lon, seq++);

    uint8_t iv[16], ct[256];
    size_t el = aes_encrypt((uint8_t*)json_buf, strlen(json_buf), ct, iv);
    if (el == 0) { Serial.println("ENCRYPT FAIL"); delay(10000); return; }
    Serial.printf("[%s] Encrypted (%d bytes)\n", device_id, el);

    // === GIAI DOAN 5: GUI QUA LoRa ===
    Serial.printf("[%s] => Gui du lieu ma hoa qua LoRa\n", device_id);
    delay(1500);

    // === GIAI DOAN 6: GATEWAY NHAN & FORWARD ===
    char hex[512]; hex[0] = 0; char b[4];
    for (size_t i = 0; i < 16 + el; i++) {
      uint8_t v = i < 16 ? iv[i] : ct[i - 16];
      sprintf(b, "%02x", v); strcat(hex, b);
    }
    Serial.printf("[Y_GW] Nhan %d bytes ma hoa\n", 16 + el);
    Serial.println("[Y_GW] Them HMAC... (simulated)");
    Serial.printf("[Y_GW] Forward len Server: payload=%s...\n", String(hex).substring(0, 40).c_str());

    if (WiFi.status() == WL_CONNECTED) {
      char body[580];
      snprintf(body, sizeof(body), "{\"payload\":\"%s\"}", hex);
      HTTPClient http;
      http.begin("http://10.0.0.2:5000/receive-data");
      http.addHeader("Content-Type", "application/json");
      int r = http.POST((uint8_t*)body, strlen(body));
      Serial.printf("[SERVER] Response: %d\n", r);
      http.end();
    } else {
      Serial.println("[GW] No WiFi, skip forward");
    }

    delay(8000);
  }

  else if (is_gateway) {
    Serial.println("[GW] Listening for LoRa packets... (simulated)");
    delay(10000);
  }
}
