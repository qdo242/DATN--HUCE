#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "MAX30105.h"
#include <mbedtls/aes.h>
#include <mbedtls/gcm.h>
#include <mbedtls/md.h>

const char* serverUrl = "http://192.168.1.169:5000/receive-data";
const char* NODE_ID = "IOT_NODE_01";
const char* NODE_KEY = "1234567890123456";
const char* GATEWAY_KEY = "gateway_secret_k";

Adafruit_SSD1306 display(128, 64, &Wire, -1);
MAX30105 max30102;
int seq = 1;
float lat = 21.0045, lon = 105.8433;

void setup() {
    Serial.begin(115200);
    Wire.begin();
    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
    max30102.begin();
    WiFi.begin("Wokwi-GUEST", "");
    while (WiFi.status() != WL_CONNECTED) delay(500);
    Serial.println("NODE 01 Connected!");
}

void loop() {
    int bpm = random(72, 85);
    lat += (random(-5, 5) / 10000.0);
    String json = "{\"id\":\"" + String(NODE_ID) + "\",\"temp\":36.5,\"bpm\":" + String(bpm) + ",\"lat\":" + String(lat,6) + ",\"lon\":" + String(lon,6) + ",\"seq\":" + String(seq++) + "}";
    
    uint8_t iv[12], tag[16], ciphertext[json.length()];
    for(int i=0; i<12; i++) iv[i] = random(0, 255);
    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);
    mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, (const uint8_t*)NODE_KEY, 128);
    mbedtls_gcm_crypt_and_tag(&gcm, MBEDTLS_GCM_ENCRYPT, json.length(), iv, 12, NULL, 0, (const uint8_t*)json.c_str(), ciphertext, 16, tag);
    mbedtls_gcm_free(&gcm);

    size_t p_len = 4 + 12 + json.length() + 16;
    uint8_t packet[p_len];
    memcpy(packet, "GW01", 4); memcpy(packet+4, iv, 12);
    memcpy(packet+16, ciphertext, json.length()); memcpy(packet+16+json.length(), tag, 16);
    uint8_t hmac[32];
    mbedtls_md_context_t md_ctx;
    mbedtls_md_init(&md_ctx);
    mbedtls_md_setup(&md_ctx, mbedtls_md_info_from_type(MBEDTLS_MD_SHA256), 1);
    mbedtls_md_hmac_starts(&md_ctx, (const unsigned char *)GATEWAY_KEY, strlen(GATEWAY_KEY));
    mbedtls_md_hmac_update(&md_ctx, packet, p_len);
    mbedtls_md_hmac_finish(&md_ctx, hmac);
    mbedtls_md_free(&md_ctx);

    String hex = ""; char b[3];
    for(int i=0; i<p_len; i++) { sprintf(b, "%02x", packet[i]); hex += b; }
    for(int i=0; i<32; i++) { sprintf(b, "%02x", hmac[i]); hex += b; }

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    int res = http.POST("{\"payload\":\"" + hex + "\"}");
    
    display.clearDisplay(); display.setCursor(0,0); display.setTextColor(WHITE);
    display.printf("NODE 01: HEALTH\nBPM: %d\nRes: %d", bpm, res);
    display.display();
    http.end();
    delay(15000);
}
