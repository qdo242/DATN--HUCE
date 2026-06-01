#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <mbedtls/aes.h>

#define PIN_X 4
#define PIN_Y 5

char current_id[20];
bool is_node_xi = false;
bool is_node_y = false;
bool is_handshake_done = false;

const char* serverUrl = "https://4e24905eecc3de.lhr.life/receive-data"; // Public Tunnel

const uint8_t NETWORK_KEY[16] = {
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

Adafruit_SSD1306 display(128, 64, &Wire, -1);
float lat = 21.00355; 
float lon = 105.84255;
int seq = 1;

void setup() {
    Serial.begin(115200);
    delay(100); // Cho on dinh dien ap

    pinMode(PIN_X, INPUT_PULLUP);
    pinMode(PIN_Y, INPUT_PULLUP);
    delay(50); // Cho pin pullup on dinh

    if (digitalRead(PIN_X) == LOW) {
        strcpy(current_id, "IOT_NODE_01"); // Xi
        is_node_xi = true;
    } else if (digitalRead(PIN_Y) == LOW) {
        strcpy(current_id, "IOT_NODE_02"); // Xj hoac Y phu
        is_node_y = true;
    } else {
        strcpy(current_id, "GATEWAY_01"); // Y
    }

    Serial.printf("\n[SYSTEM] Booting %s...\n", current_id);

    Wire.begin();
    if (is_node_xi) {
        display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
        display.setTextColor(WHITE);
        display.clearDisplay();
        display.println("Xi: READY");
        display.display();
        Serial.println("[Xi] He thong san sang. Bat dau phat Beacon (LoRa)...");
    } else if (is_node_y) {
        Serial.println("[Y] Node Y (Moi truong) san sang...");
    } else {
        Serial.println("[GW] Gateway san sang. Dang quet Beacon (LoRa)...");
    }

    WiFi.begin("Wokwi-GUEST", "");
    while (WiFi.status() != WL_CONNECTED) { delay(500); }
    Serial.println("WiFi Connected!");
    
    // De Gateway khoi dong xong truoc
    if(is_node_xi) delay(3000);
}

void do_handshake() {
    if (is_node_xi) {
        Serial.println("\n--- GIAI DOAN 1: HANDSHAKE ---");
        Serial.println("[Xi] LoRa TX: <BEACON_XI_01>");
        display.clearDisplay(); display.setCursor(0,0);
        display.println("Xi: SENDING BEACON"); display.display();
        
        delay(3000); 
        
        Serial.println("[Xi] LoRa RX: <ACK_OK_FROM_Y>");
        Serial.println("[Xi] => Handshake thanh cong! Chuyen sang che do truyen tin bao mat.");
        is_handshake_done = true;
    } 
    else if (!is_node_xi && !is_node_y) {
        Serial.println("\n--- GIAI DOAN 1: HANDSHAKE ---");
        Serial.println("[Y] LoRa RX: <BEACON_XI_01>");
        delay(1000);
        
        Serial.println("[Y] LoRa TX: <ACK_OK_FROM_Y>");
        is_handshake_done = true;
        delay(5000);
    } else {
        is_handshake_done = true; // Node phu bo qua
    }
}

size_t aes_encrypt(uint8_t* plaintext, size_t length, uint8_t* ciphertext, uint8_t* iv) {        
    mbedtls_aes_context aes_ctx;
    mbedtls_aes_init(&aes_ctx);
    mbedtls_aes_setkey_enc(&aes_ctx, NETWORK_KEY, 128); 
    for(int i = 0; i < 16; i++) iv[i] = random(0, 255);
    size_t padded_len = length;
    if (padded_len % 16 != 0) padded_len = ((padded_len / 16) + 1) * 16;
    uint8_t padded_pt[padded_len] = {0};
    memcpy(padded_pt, plaintext, length);
    mbedtls_aes_crypt_cbc(&aes_ctx, MBEDTLS_AES_ENCRYPT, padded_len, iv, padded_pt, ciphertext);
    mbedtls_aes_free(&aes_ctx);
    return padded_len;
}

void encrypt_and_send_to_server() {
    float t = 28.5 + (random(-5, 5) / 10.0);
    float h = 60.0;
    float co2 = random(400, 450);
    lat += 0.0001; 
    lon += 0.0001;

    String json = "{\"id\":\"" + String(current_id) + "\",\"t\":" + String(t, 1) + ",\"h\":" + String(h, 1) + ",\"co2\":" + String(co2, 0) + ",\"lat\":" + String(lat, 5) + ",\"lon\":" + String(lon, 5) + ",\"seq\":" + String(seq++) + "}";
    
    Serial.println("\n--- GIAI DOAN 2: DATA TRANSMISSION ---");
    Serial.println("[" + String(current_id) + "] Du lieu tho: " + json);

    uint8_t iv[16];
    uint8_t ciphertext[128] = {0}; 
    size_t enc_len = aes_encrypt((uint8_t*)json.c_str(), json.length(), ciphertext, iv);

    uint8_t packet_to_send[16 + enc_len];
    memcpy(packet_to_send, iv, 16);
    memcpy(packet_to_send + 16, ciphertext, enc_len);

    String hex = ""; char b[3];
    for(size_t i=0; i < 16 + enc_len; i++) { sprintf(b, "%02x", packet_to_send[i]); hex += b; }

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    int res = http.POST("{\"payload\":\"" + hex + "\"}");
    
    if (is_node_xi) {
        display.clearDisplay(); display.setCursor(0,0);
        display.printf("Xi -> Y -> Server\nRes: %d\nCO2: %.0f\nLat: %.5f", res, co2, lat);
        display.display();
    }
    Serial.printf("[Server] Phan hoi: Code %d\n", res);
}

void loop() {
    if (!is_handshake_done) {
        do_handshake();
    } else {
        if (is_node_xi || is_node_y) {
            encrypt_and_send_to_server();
            delay(10000); 
        } else {
            Serial.println("[Y] Dang lam nhiem vu Gateway (Chuyen tiep cac goi tin khac)...");
            delay(10000);
        }
    }
}
