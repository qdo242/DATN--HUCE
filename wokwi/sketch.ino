#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include "MAX30105.h"
#include <mbedtls/aes.h>
#include <mbedtls/gcm.h>
#include <mbedtls/md.h>

// --- LUA CHON CHE DO THIET BI ---
#define MODE_NODE_X_HEALTH 1
#define MODE_NODE_Y_ENV    2

// CHON CHE DO TAI DAY
#define DEVICE_MODE MODE_NODE_X_HEALTH 

// --- CAU HINH HE THONG ---
const char* serverUrl = "http://192.168.1.214:5000/receive-data"; // THAY IP MAY TINH
const char* GATEWAY_ID = "GW01";
const char* GATEWAY_KEY = "gw_secret_000001";

#if DEVICE_MODE == MODE_NODE_X_HEALTH
  const char* DEVICE_ID = "NODE_X_HEALTH";
  const char* NODE_KEY = "key_x_1234567890";
#else
  const char* DEVICE_ID = "NODE_Y_ENV";
  const char* NODE_KEY = "key_y_0987654321";
#endif

Adafruit_SSD1306 display(128, 64, &Wire, -1);
Adafruit_BME280 bme;
MAX30105 heartSensor;
int seq = 1;

void setup() {
    Serial.begin(115200);
    Wire.begin();
    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
    
    if(DEVICE_MODE == MODE_NODE_X_HEALTH) heartSensor.begin();
    else bme.begin(0x76);

    WiFi.begin("Wokwi-GUEST", "");
    while (WiFi.status() != WL_CONNECTED) delay(500);
    Serial.println("WiFi Connected!");
}

void loop() {
    float t=0, h=0, p=0, lat=21.0045, lon=105.8433;
    int bpm=0, spo2=0;

    // Doc du lieu theo loai thiet bi
    if(DEVICE_MODE == MODE_NODE_X_HEALTH) {
        bpm = random(70, 90); spo2 = random(95, 99);
        lat += (random(-10, 10) / 1000.0);
    } else {
        t = 25.0 + (random(0, 50)/10.0); h = 60.0; p = 1013.25;
    }

    // 1. Tao Payload JSON day du cac truong
    String json = "{\"id\":\"" + String(DEVICE_ID) + "\"" +
                  ",\"temp\":" + String(t) + 
                  ",\"humi\":" + String(h) + 
                  ",\"press\":" + String(p) + 
                  ",\"bpm\":" + String(bpm) + 
                  ",\"spo2\":" + String(spo2) + 
                  ",\"lat\":" + String(lat,6) + 
                  ",\"lon\":" + String(lon,6) + 
                  ",\"seq\":" + String(seq++) + "}";
    
    // 2. Ma hoa AES-128-GCM
    uint8_t iv[12], tag[16], ciphertext[json.length()];
    for(int i=0; i<12; i++) iv[i] = random(0, 255);
    
    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);
    mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, (const uint8_t*)NODE_KEY, 128);
    mbedtls_gcm_crypt_and_tag(&gcm, MBEDTLS_GCM_ENCRYPT, json.length(), iv, 12, NULL, 0, (const uint8_t*)json.c_str(), ciphertext, 16, tag);
    mbedtls_gcm_free(&gcm);

    // 3. Gateway Layer (HMAC)
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

    // 4. Send Hex
    String hex = "";
    char b[3];
    for(int i=0; i<p_len; i++) { sprintf(b, "%02x", packet[i]); hex += b; }
    for(int i=0; i<32; i++) { sprintf(b, "%02x", hmac[i]); hex += b; }

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    int res = http.POST("{\"payload\":\"" + hex + "\"}");
    
    display.clearDisplay(); display.setCursor(0,0); display.setTextColor(WHITE);
    display.printf("ID: %s\nRes: %d\nSECURE ACTIVE", DEVICE_ID, res);
    display.display();
    
    delay(15000);
}
