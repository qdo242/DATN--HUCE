#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h> 
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <mbedtls/aes.h>

// --- CAU HINH CHE DO ---
#define MODE_XI 1
#define MODE_Y  2
#define CURRENT_MODE MODE_XI // SUA THANH 1 de chay Xi, SUA THANH 2 de chay Y

const char* NODE_ID = "Xi_01";
const char* serverUrl = "http://192.168.1.169:5000/receive-data"; // Sua thanh IP cua ban

// KHOA DUNG CHUNG TOAN MANG (16 byte cho AES-128)
const uint8_t NETWORK_KEY[16] = {
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

Adafruit_SSD1306 display(128, 64, &Wire, -1);
Adafruit_BME280 bme;
bool is_handshake_done = false;

// Toa do ban dau (Dai hoc Xay dung - HUCE) - CO DINH, khong random vo ly
float lat = 21.00355; 
float lon = 105.84255;

void setup() {
    Serial.begin(115200);
    Wire.begin();
    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
    display.setTextColor(WHITE);
    display.clearDisplay();
    
    if (CURRENT_MODE == MODE_XI) {
        bme.begin(0x76);
        Serial.println("\n[Xi] He thong san sang. Bat dau phat Beacon (LoRa)...");
        display.println("Xi: READY");
    } else {
        Serial.println("\n[Y] Gateway san sang. Dang quet Beacon (LoRa)...");
        display.println("Y: READY");
    }
    display.display();

    WiFi.begin("Wokwi-GUEST", "");
    while (WiFi.status() != WL_CONNECTED) { delay(500); }
    Serial.println("WiFi Connected (De gui len Server)!");
}

// ----------------------------------------------------
// PHAN CUA HOANG: GIAO THUC HANDSHAKE (BEACON / ACK)
// ----------------------------------------------------
void do_handshake() {
    if (CURRENT_MODE == MODE_XI) {
        Serial.println("\n--- GIAI DOAN 1: HANDSHAKE ---");
        Serial.println("[Xi] LoRa TX: <BEACON_XI_01>");
        display.clearDisplay(); display.setCursor(0,0);
        display.println("Xi: SENDING BEACON"); display.display();
        
        delay(3000); 
        
        Serial.println("[Xi] LoRa RX: <ACK_OK_FROM_Y>");
        Serial.println("[Xi] => Handshake thanh cong! Chuyen sang che do truyen tin bao mat.");
        is_handshake_done = true;
    } 
    else if (CURRENT_MODE == MODE_Y) {
        Serial.println("\n--- GIAI DOAN 1: HANDSHAKE ---");
        Serial.println("[Y] LoRa RX: <BEACON_XI_01>");
        delay(1000);
        
        Serial.println("[Y] LoRa TX: <ACK_OK_FROM_Y>");
        display.clearDisplay(); display.setCursor(0,0);
        display.println("Y: SENT ACK"); display.display();
        
        is_handshake_done = true;
        delay(5000);
    }
}

// Ham ma hoa AES-128-CBC
size_t aes_encrypt(uint8_t* plaintext, size_t length, uint8_t* ciphertext, uint8_t* iv) {        
    mbedtls_aes_context aes_ctx;
    mbedtls_aes_init(&aes_ctx);
    
    // 1. Thiet lap khoa
    mbedtls_aes_setkey_enc(&aes_ctx, NETWORK_KEY, 128); 
    
    // 2. Tao IV ngau nhien
    for(int i = 0; i < 16; i++) {
        iv[i] = random(0, 255);
    }
    
    // 3. Ma hoa (Chieu dai phai chia het cho 16)
    size_t padded_len = length;
    if (padded_len % 16 != 0) {
        padded_len = ((padded_len / 16) + 1) * 16;
    }
    
    // Pad voi ky tu NULL
    uint8_t padded_pt[padded_len] = {0};
    memcpy(padded_pt, plaintext, length);

    mbedtls_aes_crypt_cbc(&aes_ctx, MBEDTLS_AES_ENCRYPT, padded_len, iv, padded_pt, ciphertext);
    mbedtls_aes_free(&aes_ctx);
    
    return padded_len;
}

// ----------------------------------------------------
// PHAN CUA QUAN: MA HOA VA CHUYEN TIEP DATA
// ----------------------------------------------------
void encrypt_and_send_to_server() {
    // Do cam bien (Nhiet do, Do am, CO2)
    float t = 28.5 + (random(-5, 5) / 10.0);
    float h = 60.0;
    float co2 = random(400, 450);

    // Tao Payload JSON don gian
    String json = "{\"id\":\"" + String(NODE_ID) + "\",\"t\":" + String(t, 1) + ",\"h\":" + String(h, 1) + ",\"co2\":" + String(co2, 0) + ",\"lat\":" + String(lat, 5) + ",\"lon\":" + String(lon, 5) + "}";
    
    Serial.println("\n--- GIAI DOAN 2: DATA TRANSMISSION ---");
    Serial.println("[Xi] Du lieu tho: " + json);

    // Ma hoa AES-128-CBC
    uint8_t iv[16];
    // Chieu dai du phong 128 byte
    uint8_t ciphertext[128] = {0}; 
    
    size_t enc_len = aes_encrypt((uint8_t*)json.c_str(), json.length(), ciphertext, iv);

    // Dong goi de gui: [16 byte IV] + [Ciphertext]
    uint8_t packet_to_send[16 + enc_len];
    memcpy(packet_to_send, iv, 16);
    memcpy(packet_to_send + 16, ciphertext, enc_len);

    // Chuyen sang Hex va gui
    String hex = ""; char b[3];
    for(size_t i=0; i < 16 + enc_len; i++) { 
        sprintf(b, "%02x", packet_to_send[i]); 
        hex += b; 
    }

    Serial.println("[Y] Chuyen tiep Data bao mat ve Server...");
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    int res = http.POST("{\"payload\":\"" + hex + "\"}");
    
    display.clearDisplay(); display.setCursor(0,0);
    display.printf("Xi -> Y -> Server\nRes: %d\nCO2: %.0f\nLat: %.5f", res, co2, lat);
    display.display();
    
    Serial.printf("[Server] Phan hoi: Code %d\n", res);
}

void loop() {
    if (!is_handshake_done) {
        do_handshake();
    } else {
        if (CURRENT_MODE == MODE_XI) {
            encrypt_and_send_to_server();
            delay(10000); 
        } else {
            Serial.println("[Y] Dang lam nhiem vu Gateway (Chuyen tiep cac goi tin khac)...");
            delay(10000);
        }
    }
}
