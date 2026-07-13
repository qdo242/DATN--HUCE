#include <WiFi.h>
#include <HTTPClient.h>
#include <mbedtls/aes.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

const uint8_t NETWORK_KEY[16] = {
  0x6B, 0x65, 0x79, 0x5F, 0x78, 0x5F, 0x31, 0x32,
  0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30
};
const char* XI_ID = "Xi_02";
const char* Y_ID  = "Y_01";
const char* SERVER_URL = "https://tasty-roses-unite.loca.lt/receive-data";

#define OLED_RESET -1
Adafruit_SSD1306 oled(128, 64, &Wire, OLED_RESET);

char json_buf[512];
uint32_t seq;
uint32_t cycles = 0;
float lat = 21.84550, lon = 104.09820;

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

void hien_thi(const char* line1, const char* line2,
              const char* line3, const char* line4) {
  oled.clearDisplay();
  oled.setTextColor(WHITE);
  oled.setTextSize(1);
  oled.setCursor(0, 0);
  oled.println(line1 ? line1 : "");
  oled.setCursor(0, 14);
  oled.println(line2 ? line2 : "");
  oled.setCursor(0, 28);
  oled.println(line3 ? line3 : "");
  oled.setCursor(0, 42);
  oled.println(line4 ? line4 : "");
  oled.display();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n==========================================");
  Serial.println(" XI_02 - IoT DATN Simulation");
  Serial.println(" (ESP32 + BME280 + OLED + AES + WiFi)");
  Serial.println("==========================================");

  Wire.begin(21, 22);
  delay(500);
  if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("[!] OLED init FAIL");
  } else {
    Serial.println("[+] OLED OK");
  }
  oled.clearDisplay();
  oled.display();
  hien_thi("Xi_02 dang khoi dong...", "", "", "");

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
  seq = 5000 + random(9000);
  delay(1000);
}

void loop() {
  char buf[32];

  // ===== PHASE 1: BEACON =====
  Serial.printf("\n--- LAN %d: %s ---\n", cycles + 1, XI_ID);
  hien_thi("Xi_02: Phat Beacon", "B|Xi_02", "", "Cho ACK...");
  Serial.printf("[%s] Phat Beacon (LoRa): B|%s\n", XI_ID, XI_ID);
  delay(1500);

  // ===== PHASE 2: ACK =====
  hien_thi("Y: Nhan Beacon", "Tu Xi_02", "Gui ACK...", "A|Xi_02|Y_01");
  Serial.printf("[Y]  Nhan Beacon tu %s, gui ACK\n", XI_ID);
  delay(1000);
  hien_thi("Xi_02: Nhan ACK", "Tu Y_01", "", "Dang doc sensor...");
  Serial.printf("[%s] Nhan ACK tu %s\n", XI_ID, Y_ID);

  // ===== PHASE 3: SENSOR + AES =====
  float t = 26.5 + random(-30, 30) / 10.0;
  float h = 65.0 + random(-20, 20) / 10.0;
  float p = 1008.0 + random(30);
  float c2 = 420 + random(50);
  float co = 4.5 + random(30) / 10.0;
  float nh3 = 2.5 + random(20) / 10.0;
  lat += 0.00003; lon += 0.00003;
  int sats = 5 + random(4);

  snprintf(buf, sizeof(buf), "T:%.1fC H:%.0f%% P:%.0f", t, h, p);
  char buf3[32];
  snprintf(buf3, sizeof(buf3), "GPS:%.5fN %.5fE", lat, lon);
  hien_thi("Xi_02: Doc cam bien", buf, buf3, "");

  Serial.printf("  T=%.1fC H=%.0f%% P=%.0f\n", t, h, p);
  Serial.printf("  GPS=%.5fN %.5fE\n", lat, lon);
  Serial.printf("  CO2=%.0f CO=%.1f NH3=%.1f\n", c2, co, nh3);

  snprintf(json_buf, sizeof(json_buf),
    "{\"id\":\"%s\",\"t\":%.1f,\"h\":%.1f,\"p\":%.1f,"
    "\"co2\":%.0f,\"co\":%.1f,\"nh3\":%.1f,"
    "\"lat\":%.5f,\"lon\":%.5f,\"alt\":%.0f,\"sats\":%d,"
    "\"gw\":\"%s\",\"seq\":%u}",
    XI_ID, t, h, p, c2, co, nh3,
    lat, lon, 10.0, sats, Y_ID, seq++);

  uint8_t iv[16], ct[256];
  size_t el = aes_encrypt((uint8_t*)json_buf, strlen(json_buf), ct, iv);

  char hex[512]; hex[0] = 0; char b[4];
  for (size_t i = 0; i < 16 + el; i++) {
    uint8_t v = i < 16 ? iv[i] : ct[i - 16];
    sprintf(b, "%02x", v); strcat(hex, b);
  }

  Serial.printf("[%s] AES-CBC: %d bytes Hex: %.32s...\n", XI_ID, 16 + el, hex);
  hien_thi("Xi_02: AES xong", "Gui data...", "", "");

  // ===== PHASE 4: FORWARD =====
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
    Serial.printf("[SERVER] HTTP %d\n", http_code);
    http.end();
  }

  char status_line[32];
  snprintf(status_line, sizeof(status_line), "HTTP %d", http_code);
  hien_thi("Server:", status_line,
    http_code == 200 ? "THANH CONG!" : "THAT BAI", "");

  Serial.printf("=== HOAN THANH LAN %d (%s) ===\n\n", cycles + 1, XI_ID);

  cycles++;
  if (cycles >= 6) {
    hien_thi("Hoan thanh!", "6 chu ky mo phong", "Xem Dashboard", "localhost:8501");
    Serial.printf("=== DA HOAN THANH %d CHU KY (%s) ===\n", cycles, XI_ID);
    while (1) delay(10000);
  }
  delay(4000);
}
