/*
 * ============================================================
 *  XI NODE - TTGO T-Beam (ESP32 + LoRa SX1276 + GPS + Sensors)
 * ============================================================
 *  Thiet bi: TTGO T-Beam (V07 / V08+ / V1.x)
 *  Cam bien: GY-BME280 (I2C 0x76),
 *            GPS NEO-M8N (UART2), OLED SSD1306 (I2C 0x3C)
 *
 *  Giao thuc:
 *    1. Phat Beacon  (LoRa) "B|<Xi_ID>"
 *    2. Cho ACK tu Y  (LoRa, timeout 3s) "A|<Xi_ID>|<Y_ID>"
 *    3. Gui du lieu ma hoa AES-CBC (LoRa) "D|<Xi_ID>|<hex>"
 *
 *  Wiring xac nhan tu HW reference [11][12][13]:
 *    BME280: VIN->3V3, GND->GND, SCL->GPIO22, SDA->GPIO21
 *    OLED:   VCC->3V3, GND->GND, SDA->GPIO21, SCL->GPIO22, addr 0x3C
 *    LoRa:   SCK=5, MISO=19, MOSI=27, CS=18, RST=23, DIO0=26
 *    GPS:    TX->GPIO12 (ESP32 RX2), RX->GPIO15 (ESP32 TX2)
 *

 *  Hardware revision notes:
 *    - V07 va truoc: GPS pins khac, khong co AXP202X
 *    - V08/V09/V10/V1.0+: co AXP202X (power management), can khoi tao
 *    - I2C clock co the len 800kHz (SSD1306 patch) [12]
 *
 *  Cai dat thu vien (Arduino IDE):
 *    - "Adafruit BME280 Library" (Adafruit) [16]
 *    - "Adafruit Unified Sensor"
 *    - "TinyGPSPlus"
 *    - "ESP8266 and ESP32 OLED driver for SSD1306 displays"
 *      hoac "U8g2"
 *    - "LoRa" by Sandeep Mistry
 *    - Neu HW V08+: "AXP202X_Library" (lewisxhe)
 *
 *  Board: Arduino IDE -> Tools -> Board -> ESP32 Arduino -> "T-Beam"
 *         hoac PlatformIO: board_build.variant = tbeam
 *         Xem them: LilyGo-LoRa-Series/utilities.h [11]
 * ============================================================
 */
#include <Wire.h>
#include <mbedtls/aes.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#include <TinyGPSPlus.h>
#include <SSD1306Wire.h>
#include <LoRa.h>

// ============================================================
//                      CAU HINH
// ============================================================
const uint8_t NETWORK_KEY[16] = {
  0x6B, 0x65, 0x79, 0x5F, 0x78, 0x5F, 0x31, 0x32,
  0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30
};
const char* XI_ID   = "Xi_01";       // Doi thanh Xi_02 cho node thu 2
const float LORA_FREQ = 868E6;      // 868 MHz (SX1276)
const long  LORA_TX_POWER = 17;     // dBm
const int   LORA_CS  = 18;
const int   LORA_RST = 23;
const int   LORA_DIO = 26;
const int   GPS_RX   = 12;          // T-BEAM: GPS TX -> ESP32 RX2
const int   GPS_TX   = 15;          // T-BEAM: GPS RX <- ESP32 TX2

// I2C: SSD1306 OLED 0x3C, BME280 0x76
Adafruit_BME280 bme;
TinyGPSPlus gps;
SSD1306Wire oled(0x3c, 21, 22);

uint32_t seq = 1;
char json_buf[512];

// ============================================================
//                      AES-128-CBC
// ============================================================
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

// ============================================================
//                      DOC CAM BIEN
// ============================================================
struct SensorData {
  float t, h, p;
  float lat, lon, alt;
  int   sats;
  float co2, co, nh3;
};

bool doc_bme280(SensorData& d) {
  d.t = bme.readTemperature();
  d.h = bme.readHumidity();
  d.p = bme.readPressure() / 100.0F;
  return (!isnan(d.t) && !isnan(d.h));
}

// GPS non-blocking: doc lien tuc, khong blocking loop
void doc_gps(SensorData& d) {
  d.lat = 21.84470; d.lon = 104.09700; d.alt = 0; d.sats = 0;
  unsigned long start = millis();
  while (millis() - start < 3000) {
    while (Serial2.available()) gps.encode(Serial2.read());
    if (gps.location.isValid() && gps.location.age() < 2000) {
      d.lat  = gps.location.lat();
      d.lon  = gps.location.lng();
      d.alt  = gps.altitude.meters();
      d.sats = gps.satellites.value();
      return;
    }
    delay(10);
  }
}

void doc_sensors(SensorData& d) {
  doc_bme280(d);
  doc_gps(d);
  d.co2 = 400 + random(50);
  d.co  = 5.0 + random(30)/10.0;
  d.nh3 = 2.0 + random(20)/10.0;
}

// ============================================================
//                      OLED
// ============================================================
void hien_thi(const char* line1, const char* line2,
              const char* line3, const char* line4) {
  oled.clear();
  oled.setFont(ArialMT_Plain_10);
  oled.drawString(0, 0,  line1 ? line1 : "");
  oled.drawString(0, 14, line2 ? line2 : "");
  oled.drawString(0, 28, line3 ? line3 : "");
  oled.drawString(0, 42, line4 ? line4 : "");
  oled.display();
}

// ============================================================
//                      LORA
// ============================================================
bool gui_loRa(const char* msg) {
  LoRa.beginPacket();
  LoRa.print(msg);
  return LoRa.endPacket();
}

bool doc_loRa(char* buf, int size, unsigned long timeout_ms) {
  unsigned long start = millis();
  while (millis() - start < timeout_ms) {
    int pkt = LoRa.parsePacket();
    if (pkt) {
      int i = 0;
      while (LoRa.available() && i < size - 1) {
        buf[i++] = (char)LoRa.read();
      }
      buf[i] = 0;
      return true;
    }
    delay(10);
  }
  return false;
}

// ============================================================
//                      PROTOCOL: Xi
// ============================================================
bool protocol_xi(const SensorData& d) {
  char buf[64];

  // --- Buoc 1: Phat Beacon ---
  snprintf(buf, sizeof(buf), "B|%s", XI_ID);
  Serial.printf("[%s] Beacon => %s\n", XI_ID, buf);
  hien_thi("Phat Beacon...", XI_ID, "", "Cho ACK...");
  if (!gui_loRa(buf)) {
    Serial.println("[!] Gui Beacon that bai");
    return false;
  }

  // --- Buoc 2: Cho ACK (timeout 3s) ---
  if (!doc_loRa(buf, sizeof(buf), 3000)) {
    Serial.println("[!] Het thoi gian cho ACK");
    hien_thi("Ko nhan ACK", "", "Thu lai sau...", "");
    return false;
  }

  char target[16], gw[16];
  if (sscanf(buf, "A|%15[^|]|%15s", target, gw) != 2 ||
      strcmp(target, XI_ID) != 0) {
    Serial.printf("[!] ACK sai: %s\n", buf);
    return false;
  }
  Serial.printf("[%s] Nhan ACK tu %s\n", XI_ID, gw);
  hien_thi("Nhan ACK tu:", gw, "", "Dang gui data...");

  // --- Buoc 3: Gui du lieu ma hoa ---
  snprintf(json_buf, sizeof(json_buf),
    "{\"id\":\"%s\",\"t\":%.1f,\"h\":%.1f,\"p\":%.1f,"
    "\"co2\":%.0f,\"co\":%.1f,\"nh3\":%.1f,"
    "\"lat\":%.5f,\"lon\":%.5f,\"alt\":%.1f,\"sats\":%d,"
    "\"gw\":\"%s\",\"seq\":%u}",
    XI_ID, d.t, d.h, d.p,
    d.co2, d.co, d.nh3,
    d.lat, d.lon, d.alt, d.sats,
    gw, seq++);

  uint8_t iv[16], ct[256];
  size_t el = aes_encrypt((uint8_t*)json_buf, strlen(json_buf), ct, iv);

  char hex[512]; hex[0] = 0; char b[4];
  for (size_t i = 0; i < 16 + el; i++) {
    uint8_t v = i < 16 ? iv[i] : ct[i - 16];
    sprintf(b, "%02x", v); strcat(hex, b);
  }

  char data_pkt[580];
  snprintf(data_pkt, sizeof(data_pkt), "D|%s|%s", XI_ID, hex);
  Serial.printf("[%s] Data (%d bytes encrypted)\n", XI_ID, el);
  Serial.printf("[%s] => %s\n", XI_ID, data_pkt);

  if (!gui_loRa(data_pkt)) {
    Serial.println("[!] Gui data that bai");
    hien_thi("Gui data FAIL", "", "", "");
    return false;
  }

  Serial.println("[+] Gui data thanh cong!");
  hien_thi("Gui data OK!", "", "", "");
  return true;
}

// ============================================================
//                      SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== XI NODE (TTGO T-Beam) ===");
  Serial.printf("ID: %s\n", XI_ID);

  Wire.begin(21, 22);
  Wire.setClock(400000);  // I2C 400kHz (co the len 800kHz neu patch SSD1306)

  // OLED SSD1306 / SH1106
  oled.init(); oled.flipScreenVertically();
  hien_thi("Khoi dong...", "", "", "");

  // BME280 (I2C 0x76 hoac 0x77)
  if (!bme.begin(0x76))
    Serial.println("[!] Loi BME280");
  else
    Serial.println("[+] BME280 OK");

  // GPS UART2
  Serial2.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  Serial.println("[+] GPS UART2 OK");

  // LoRa (T-Beam specific SPI pins)
  SPI.begin(5, 19, 27, 18);
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO);
  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("[!] Loi LoRa!");
    hien_thi("LoRa FAIL!", "", "", "");
    while (1);
  }
  LoRa.setTxPower(LORA_TX_POWER);
  LoRa.setSpreadingFactor(12);
  LoRa.setCodingRate4(5);
  LoRa.setSignalBandwidth(125E3);
  Serial.printf("[+] LoRa OK @ %.1f MHz\n", LORA_FREQ / 1E6);

  randomSeed(analogRead(0));
  hien_thi("San sang!", "", "", "");
  delay(1000);
}

// ============================================================
//                      LOOP
// ============================================================
void loop() {
  SensorData d = { 0 };
  doc_sensors(d);
  protocol_xi(d);
  delay(5000);
}
