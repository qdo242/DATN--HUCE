/*
 * ============================================================
 *  Y GATEWAY - ESP32 + LoRa SX1278 (433MHz demo)
 * ============================================================
 *  Nhiem vu:
 *    1. Quet Beacon tu Xi qua LoRa
 *    2. Gui ACK cho Xi
 *    3. Nhan du lieu ma hoa tu Xi
 *    4. Chuyen tiep ve Server qua WiFi (HTTP POST)
 *
 *  Phan cung:
 *    - ESP32 DevKit
 *    - Module LoRa SX1278 (SPI)
 *      CS=GPIO5, RST=GPIO14, DIO0=GPIO2
 *      SCK=GPIO18, MISO=GPIO19, MOSI=GPIO23
 *
 *  Cai dat thu vien:
 *    - "LoRa" by Sandeep Mistry
 *
 *  Board: Arduino IDE -> Board -> "ESP32 Dev Module"
 * ============================================================
 */
#include <WiFi.h>
#include <HTTPClient.h>
#include <LoRa.h>

// ============================================================
//                      CAU HINH
// ============================================================
const char* Y_ID = "Y_01";
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
const char* SERVER_URL = "http://192.168.1.100:5000/receive-data";  // thay bang IP server

const float LORA_FREQ = 433E6;       // 433 MHz (SX1278) - demo
const int   LORA_CS  = 5;
const int   LORA_RST = 14;
const int   LORA_DIO = 2;
// SPI mac dinh: SCK=18, MISO=19, MOSI=23

// ============================================================
//                      LO RA
// ============================================================
bool gui_loRa(const char* msg) {
  LoRa.beginPacket();
  LoRa.print(msg);
  return LoRa.endPacket();
}

int doc_loRa(char* buf, int size, unsigned long timeout_ms) {
  unsigned long start = millis();
  while (millis() - start < timeout_ms) {
    int pkt = LoRa.parsePacket();
    if (pkt) {
      int i = 0;
      while (LoRa.available() && i < size - 1)
        buf[i++] = (char)LoRa.read();
      buf[i] = 0;
      return i;
    }
    delay(5);
  }
  return 0;
}

// ============================================================
//                      FORWARD TO SERVER
// ============================================================
bool gui_server(const char* payload_hex) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[!] WiFi not connected");
    return false;
  }
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  char body[580];
  snprintf(body, sizeof(body), "{\"payload\":\"%s\"}", payload_hex);
  int r = http.POST((uint8_t*)body, strlen(body));
  bool ok = (r == 200);
  Serial.printf("[SERVER] HTTP %d -> %s\n", r, ok ? "OK" : "FAIL");
  http.end();
  return ok;
}

// ============================================================
//                      SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== Y GATEWAY ===");
  Serial.printf("ID: %s\n", Y_ID);

  // LoRa
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO);
  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("[!] Loi LoRa!");
    while (1);
  }
  LoRa.setTxPower(17);
  LoRa.setSpreadingFactor(12);
  LoRa.setCodingRate4(5);
  LoRa.setSignalBandwidth(125E3);
  Serial.printf("[+] LoRa OK @ %.1f MHz\n", LORA_FREQ / 1E6);

  // WiFi
  Serial.printf("[WiFi] Ket noi %s...\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int w = 0;
  while (WiFi.status() != WL_CONNECTED && w < 40) {
    delay(500); Serial.print(".");
    w++;
  }
  if (WiFi.status() == WL_CONNECTED)
    Serial.printf("\n[+] WiFi OK IP: %s\n", WiFi.localIP().toString().c_str());
  else
    Serial.println("\n[!] WiFi FAIL (skip http)");

  Serial.println("=== San sang nhan Beacon tu Xi ===\n");
}

// ============================================================
//                      LOOP
// ============================================================
void loop() {
  char buf[256];

  // --- Buoc 1: Cho Beacon tu Xi ---
  int len = doc_loRa(buf, sizeof(buf), 1000);  // timeout 1s
  if (len == 0) return;

  Serial.printf("[LoRa] Nhan: %s\n", buf);

  // Kiem tra Beacon: "B|XI_XX"
  char xi_id[16];
  if (sscanf(buf, "B|%15s", xi_id) != 1) {
    // Khong phai Beacon, bo qua
    return;
  }

  Serial.printf("[Y] Phat hien Beacon tu %s\n", xi_id);

  // --- Buoc 2: Gui ACK ---
  char ack[32];
  snprintf(ack, sizeof(ack), "A|%s|%s", xi_id, Y_ID);
  Serial.printf("[Y] Gui ACK => %s\n", ack);
  if (!gui_loRa(ack)) {
    Serial.println("[!] Gui ACK that bai");
    return;
  }

  // --- Buoc 3: Cho du lieu tu Xi (timeout 5s) ---
  if (doc_loRa(buf, sizeof(buf), 5000) == 0) {
    Serial.println("[!] Het thoi gian cho du lieu");
    return;
  }

  // Kiem tra Data: "D|XI_XX|<hex>"
  char id[16], hex[512];
  if (sscanf(buf, "D|%15[^|]|%511s", id, hex) != 2) {
    Serial.printf("[!] Sai format data: %s\n", buf);
    return;
  }

  Serial.printf("[Y] Nhan du lieu tu %s (%d bytes)\n", id, strlen(hex));

  // --- Buoc 4: Chuyen tiep len Server ---
  gui_server(hex);
  delay(100);
}
