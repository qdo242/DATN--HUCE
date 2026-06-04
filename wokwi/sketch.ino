#include <WiFi.h>
#include <HTTPClient.h>
#include <mbedtls/aes.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <SSD1306Wire.h>

const uint8_t NETWORK_KEY[16] = {
  0x6B, 0x65, 0x79, 0x5F, 0x78, 0x5F, 0x31, 0x32,
  0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30
};
const char* XI_ID = "Xi_01";
const char* Y_ID  = "Y_01";
const char* SERVER_URL = "https://dirty-dingos-serve.loca.lt/receive-data";

Adafruit_BME280 bme;
SSD1306Wire oled(0x3c, 21, 22);

char json_buf[512];
uint32_t seq = 1;
float lat = 21.00355, lon = 105.84255;

static size_t aes_encrypt(uint8_t* pt, size_t len, uint8_t* ct, uint8_t* iv) {
  mbedtls_aes_context ctx;
  mbedtls_aes_init(&ctx);
  mbedtls_aes_setkey_enc(&ctx, NETWORK_KEY, 128);
  uint8_t iv_copy[16];
  for (int i = 0; i < 16; i++) iv_copy[i] = random(256);
  size_t pl = ((len + 15) / 16) * 16;
  uint8_t pad[256];
  memset(pad, 0, pl);
  memcpy(pad, pt, len);
  memcpy(iv, iv_copy, 16);
  mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT, pl, iv, pad, ct);
  memcpy(iv, iv_copy, 16);
  mbedtls_aes_free(&ctx);
  return pl;
}

void hien_thi(const char* line1, const char* line2, const char* line3, const char* line4) {
  oled.clear();
  oled.setFont(ArialMT_Plain_10);
  oled.drawString(0, 0,  line1 ? line1 : "");
  oled.drawString(0, 14, line2 ? line2 : "");
  oled.drawString(0, 28, line3 ? line3 : "");
  oled.drawString(0, 42, line4 ? line4 : "");
  oled.display();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n==========================================");
  Serial.println(" MO PHONG HE THONG XI -> Y -> SERVER");
  Serial.println(" (ESP32 + BME280 + OLED + AES + WiFi)");
  Serial.println("==========================================");

  Wire.begin(21, 22);

  oled.init();
  oled.flipScreenVertically();
  oled.setFont(ArialMT_Plain_10);
  hien_thi("Dang khoi dong...", "", "", "");

  if (!bme.begin(0x76))
    Serial.println("[!] Loi BME280");
  else
    Serial.println("[+] BME280 OK");

  WiFi.mode(WIFI_STA);
  WiFi.begin("Wokwi-GUEST");
  Serial.print("[WiFi] Ket noi...");
  hien_thi("Dang ket noi WiFi...", "Wokwi-GUEST", "", "");
  int w = 0;
  while (WiFi.status() != WL_CONNECTED && w < 80) {
    delay(500); Serial.print(".");
    w++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
    hien_thi("WiFi OK", WiFi.localIP().toString().c_str(), "", "");
  } else {
    Serial.println("\n[WiFi] FAIL");
    hien_thi("WiFi FAIL", "Van tiep tuc...", "", "");
  }

  randomSeed(analogRead(0));
  delay(1000);
}

void loop() {
  char buf[32];

  // ===== PHASE 1: BEACON =====
  Serial.println("\n--- BEACON ---");
  hien_thi("XI: Phat Beacon", "B|Xi_01", "", "Cho ACK...");
  Serial.printf("[XI] Phat Beacon (LoRa): B|%s\n", XI_ID);
  delay(1500);

  // ===== PHASE 2: ACK =====
  Serial.println("\n--- ACK ---");
  hien_thi("Y: Nhan Beacon", "Tu Xi_01", "Gui ACK...", "A|Xi_01|Y_01");
  Serial.printf("[Y]  Nhan Beacon tu %s\n", XI_ID);
  Serial.printf("[Y]  Gui ACK (LoRa): A|%s|%s\n", XI_ID, Y_ID);
  delay(1000);
  hien_thi("XI: Nhan ACK", "Tu Y_01", "", "Dang doc sensor...");
  Serial.printf("[XI] Nhan ACK tu %s\n", Y_ID);

  // ===== PHASE 3: SENSOR + AES =====
  Serial.println("\n--- SENSOR + ENCRYPT ---");

  float t = bme.readTemperature();
  float h = bme.readHumidity();
  float p = bme.readPressure() / 100.0F;
  if (isnan(t) || isnan(h) || isnan(p)) {
    t = 28.0 + random(-30, 30) / 10.0;
    h = 60.0 + random(-20, 20) / 10.0;
    p = 1005.0 + random(30);
  }
  float c2 = 400 + random(50);
  float co = 5.0 + random(30) / 10.0;
  float nh3 = 2.0 + random(20) / 10.0;
  int   hr = random(2) ? 65 + random(20) : 0;
  float spo2 = hr ? 95.0 + random(50)/10.0 : 0;
  lat += 0.00005; lon += 0.00005;
  int sats = 6 + random(4);

  snprintf(buf, sizeof(buf), "T:%.1fC H:%.0f%% P:%.0f", t, h, p);
  char buf2[32];
  snprintf(buf2, sizeof(buf2), "HR:%d SpO2:%.0f%%", hr, spo2);
  char buf3[32];
  snprintf(buf3, sizeof(buf3), "GPS:%.5fN %.5fE", lat, lon);
  hien_thi("XI: Doc cam bien", buf, buf2, buf3);

  Serial.printf("  BME280  -> T=%.1fC  H=%.0f%%  P=%.0fhPa\n", t, h, p);
  Serial.printf("  MAX30102-> HR=%d bpm  SpO2=%.0f%%\n", hr, spo2);
  Serial.printf("  GPS     -> lat=%.5f lon=%.5f alt=10m sats=%d\n", lat, lon, sats);
  Serial.printf("  MQ (sim)-> CO2=%.0f CO=%.1f NH3=%.1f\n", c2, co, nh3);

  snprintf(json_buf, sizeof(json_buf),
    "{\"id\":\"%s\",\"t\":%.1f,\"h\":%.1f,\"p\":%.1f,"
    "\"hr\":%d,\"spo2\":%.0f,"
    "\"co2\":%.0f,\"co\":%.1f,\"nh3\":%.1f,"
    "\"lat\":%.5f,\"lon\":%.5f,\"alt\":%.0f,\"sats\":%d,"
    "\"gw\":\"%s\",\"seq\":%u}",
    XI_ID, t, h, p, hr, spo2, c2, co, nh3,
    lat, lon, 10.0, sats, Y_ID, seq++);

  uint8_t iv[16], ct[256];
  size_t el = aes_encrypt((uint8_t*)json_buf, strlen(json_buf), ct, iv);

  char hex[512]; hex[0] = 0; char b[4];
  for (size_t i = 0; i < 16 + el; i++) {
    uint8_t v = i < 16 ? iv[i] : ct[i - 16];
    sprintf(b, "%02x", v); strcat(hex, b);
  }

  Serial.printf("[XI] AES-CBC: %d bytes (IV=16 + CT=%d)\n", 16 + el, el);
  Serial.printf("[XI] Hex: %.32s...\n", hex);

  char data_pkt[580];
  snprintf(data_pkt, sizeof(data_pkt), "D|%s|%s", XI_ID, hex);
  Serial.printf("[XI] Gui data (LoRa): D|%s|<hex> (%d bytes)\n", XI_ID, strlen(hex));
  hien_thi("XI: AES xong", "Gui data...", "", "");

  // ===== PHASE 4: FORWARD =====
  Serial.println("\n--- FORWARD TO SERVER ---");
  hien_thi("Y: Nhan data", "Chuyen tiep len", "Server...", "");
  Serial.printf("[Y]  Nhan data tu %s\n", XI_ID);

  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("[Y]  WiFi mat ket noi, ket noi lai...");
    WiFi.reconnect();
    int r = 0;
    while (WiFi.status() != WL_CONNECTED && r < 30) {
      delay(500); Serial.print(".");
      r++;
    }
    Serial.println(WiFi.status() == WL_CONNECTED ? " OK" : " FAIL");
  }

  int http_code = -1;
  if (WiFi.status() == WL_CONNECTED) {
    char body[580];
    snprintf(body, sizeof(body), "{\"payload\":\"%s\"}", hex);
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    http_code = http.POST((uint8_t*)body, strlen(body));
    Serial.printf("[SERVER] HTTP %d - %s\n", http_code,
      http_code == 200 ? "THANH CONG!" : "THAT BAI");
    http.end();
  } else {
    Serial.println("[Y]  Khong co WiFi, bo qua forward");
  }

  char status_line[32];
  snprintf(status_line, sizeof(status_line), "HTTP %d", http_code);
  hien_thi("Server:", status_line,
    http_code == 200 ? "THANH CONG!" : "THAT BAI", "");

  Serial.println("\n=== HOAN THANH 1 CHU KY ===\n");

  if (seq > 4) {
    Serial.println("=== DA HOAN THANH 4 CHU KY MO PHONG ===");
    hien_thi("Hoan thanh!", "4 chu ky mo phong", "Xem Dashboard", "localhost:8501");
    while (1) delay(10000);
  }
  delay(3000);
}
