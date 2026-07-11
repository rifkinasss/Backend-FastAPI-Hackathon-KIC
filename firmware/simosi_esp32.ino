/*
 * ============================================================
 *  SIMOSI — Smart IoT Monitoring System
 *  Firmware ESP32 v1.1 (Includes Remote Maintenance Control)
 * ============================================================
 *  Sensors:
 *    DHT22   → GPIO4  (temperature, humidity)
 *    MQ4     → GPIO34 (CH4 / methane)
 *    MQ7     → GPIO35 (CO / carbon monoxide)
 *    MQ135   → GPIO32 (CO2 estimated)
 *    DS3231  → I2C    (RTC — optional)
 *
 *  Flow:
 *    1. Baca semua sensor
 *    2. Bangun JSON payload
 *    3. POST ke /api/v1/readings
 *    4. Polling target perintah remote (restart, sleep, turn_off)
 *    5. Tunggu interval → ulangi
 * ============================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// =============================================================
// KONFIGURASI — SESUAIKAN DENGAN ENVIRONMENT KAMU
// =============================================================

// WiFi
const char* WIFI_SSID     = "Ameera01";
const char* WIFI_PASSWORD = "ameera01";

// SIMOSI API
const char* API_URL = "https://api.rifkinasss.my.id/api/v1/readings";

// Device
const char* DEVICE_CODE = "ESP32-MINE-001";

// Interval pembacaan sensor (ms)
const unsigned long READING_INTERVAL = 30000; // 30 detik

// =============================================================
// PIN DEFINITIONS
// =============================================================

#define DHTPIN     4
#define DHTTYPE    DHT22
#define MQ4_PIN    34
#define MQ7_PIN    35
#define MQ135_PIN  32

// =============================================================
// KONSTANTA ADC & KALIBRASI MQ
// =============================================================

const float ADC_MAX = 4095.0;
const float ADC_REF = 3.3;

// Resistor load pada modul MQ (RL) — biasanya 10kΩ atau 20kΩ
const float RL_MQ4   = 20.0; // kΩ
const float RL_MQ7   = 10.0; // kΩ
const float RL_MQ135 = 20.0; // kΩ

// R0 — resistansi sensor di udara bersih (harus dikalibrasi!)
// Nilai default, ganti setelah kalibrasi di udara bersih
float R0_MQ4   = 10.0; // kΩ
float R0_MQ7   =  4.0; // kΩ
float R0_MQ135 = 76.63; // kΩ (dari seed data calibration_profiles)

// =============================================================
// OBJECTS
// =============================================================

DHT dht(DHTPIN, DHTTYPE);

// =============================================================
// HELPER FUNCTIONS
// =============================================================

/**
 * Hitung Rs (resistansi sensor) dari pembacaan ADC.
 * Rs = RL * (Vcc - Vout) / Vout
 */
float calculateRs(int adcValue, float rl)
{
  if (adcValue == 0) return 999999.0; // hindari division by zero
  float voltage = (adcValue * ADC_REF) / ADC_MAX;
  return rl * (ADC_REF - voltage) / voltage;
}

/**
 * MQ4 — Estimasi CH4 (ppm) dari rasio Rs/R0.
 */
float readCH4_ppm()
{
  int adc = analogRead(MQ4_PIN);
  float rs = calculateRs(adc, RL_MQ4);
  float ratio = rs / R0_MQ4;

  float ppm = pow(10, ((log10(ratio) - 1.18) / -0.36));

  if (ppm < 300)   ppm = 300;
  if (ppm > 10000)  ppm = 10000;

  return ppm;
}

/**
 * MQ7 — Estimasi CO (ppm) dari rasio Rs/R0.
 */
float readCO_ppm()
{
  int adc = analogRead(MQ7_PIN);
  float rs = calculateRs(adc, RL_MQ7);
  float ratio = rs / R0_MQ7;

  float ppm = pow(10, ((log10(ratio) - 1.41) / -0.77));

  if (ppm < 20)   ppm = 20;
  if (ppm > 2000) ppm = 2000;

  return ppm;
}

/**
 * MQ135 — Estimasi CO2 (ppm) dari rasio Rs/R0.
 */
float readCO2_ppm()
{
  int adc = analogRead(MQ135_PIN);
  float rs = calculateRs(adc, RL_MQ135);
  float ratio = rs / R0_MQ135;

  float ppm = pow(10, ((log10(ratio) - 1.20) / -0.42));

  if (ppm < 400)   ppm = 400;
  if (ppm > 5000)  ppm = 5000;

  return ppm;
}

// =============================================================
// WiFi
// =============================================================

void connectWiFi()
{
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("[WiFi] Menghubungkan ke ");
  Serial.print(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30)
  {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println(" OK!");
    Serial.print("[WiFi] IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("[WiFi] RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  }
  else
  {
    Serial.println(" GAGAL!");
  }
}

// =============================================================
// Kirim Status Acknowledgement Perintah ke API
// =============================================================

void sendAck(int commandId, String status, String errMsg)
{
  String baseUrl = String(API_URL);
  int lastSlash = baseUrl.lastIndexOf("/readings");
  if (lastSlash == -1) return;
  String ackUrl = baseUrl.substring(0, lastSlash) + "/devices/" + String(DEVICE_CODE) + "/commands/" + String(commandId) + "/ack";

  HTTPClient http;
  http.begin(ackUrl);
  http.addHeader("Content-Type", "application/json");

  String payload = "{\"status\":\"" + status + "\"";
  if (errMsg.length() > 0)
  {
    payload += ",\"error_message\":\"" + errMsg + "\"";
  }
  payload += "}";

  Serial.println("[ACK] Mengirim status: " + status + " untuk Command ID: " + String(commandId));
  int httpCode = http.POST(payload);
  Serial.print("[ACK] HTTP Code: ");
  Serial.println(httpCode);
  http.end();
}

// =============================================================
// Polling Perintah Remote dari API
// =============================================================

void checkAndExecuteCommands()
{
  if (WiFi.status() != WL_CONNECTED) return;

  String baseUrl = String(API_URL);
  int lastSlash = baseUrl.lastIndexOf("/readings");
  if (lastSlash == -1) return;
  String commandUrl = baseUrl.substring(0, lastSlash) + "/devices/" + String(DEVICE_CODE) + "/commands/next";

  HTTPClient http;
  http.begin(commandUrl);
  http.setTimeout(5000);

  Serial.println("[POLL] Memeriksa perintah maintenance dari dashboard...");
  int httpCode = http.GET();
  if (httpCode == 200)
  {
    String payload = http.getString();
    http.end();

    // Jika payload kosong atau bernilai null
    if (payload.indexOf("\"data\":null") != -1 || payload.indexOf("\"data\": null") != -1)
    {
      Serial.println("[POLL] Tidak ada perintah pending.");
      return;
    }

    // Parsing Command ID
    int idIndex = payload.indexOf("\"id\":");
    if (idIndex == -1) return;
    int idStart = idIndex + 5;
    int idEnd = payload.indexOf(",", idStart);
    if (idEnd == -1) idEnd = payload.indexOf("}", idStart);
    String idStr = payload.substring(idStart, idEnd);
    idStr.trim();
    int commandId = idStr.toInt();

    // Parsing Command Verb
    int cmdIndex = payload.indexOf("\"command\":\"");
    if (cmdIndex == -1) return;
    int cmdStart = cmdIndex + 11;
    int cmdEnd = payload.indexOf("\"", cmdStart);
    String command = payload.substring(cmdStart, cmdEnd);
    command.trim();

    Serial.print("[POLL] Menerima instruksi: ");
    Serial.println(command);

    // Eksekusi aksi
    if (command == "restart")
    {
      Serial.println("[EXEC] Mengirim ACK lalu melakukan reboot...");
      sendAck(commandId, "executed", "");
      delay(1000);
      ESP.restart();
    }
    else if (command == "turn_off")
    {
      Serial.println("[EXEC] Mengirim ACK lalu mematikan node (Deep Sleep Permanent)...");
      sendAck(commandId, "executed", "");
      delay(1000);
      ESP.deepSleep(0); // Tidur selamanya sampai reset fisik / tombol dipicu
    }
    else if (command == "sleep")
    {
      Serial.println("[EXEC] Mengirim ACK lalu tidur 10 menit...");
      sendAck(commandId, "executed", "");
      delay(1000);
      ESP.deepSleep(600000000); // 10 menit (dalam mikrodetik)
    }
    else if (command == "turn_on")
    {
      Serial.println("[EXEC] Node sudah hidup. Mengirim ACK...");
      sendAck(commandId, "executed", "");
    }
    else
    {
      Serial.print("[EXEC] Perintah tidak didukung: ");
      Serial.println(command);
      sendAck(commandId, "failed", "Command not supported by this firmware version");
    }
  }
  else
  {
    Serial.print("[POLL] Error HTTP: ");
    Serial.println(httpCode);
    http.end();
  }
}

// =============================================================
// Kirim Data Sensor ke API
// =============================================================

bool sendToAPI(float temp, float hum, float ch4, float co, float co2)
{
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("[API] WiFi tidak terhubung, skip pengiriman.");
    return false;
  }

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000);

  // Bangun JSON payload
  String json = "{";
  json += "\"device_code\":\"" + String(DEVICE_CODE) + "\"";

  if (!isnan(temp))
  {
    json += ",\"temperature\":" + String(temp, 2);
  }
  if (!isnan(hum))
  {
    json += ",\"humidity\":" + String(hum, 2);
  }

  json += ",\"ch4\":" + String(ch4, 2);
  json += ",\"co\":" + String(co, 2);
  json += ",\"co2_estimated\":" + String(co2, 2);
  json += ",\"wifi_rssi\":" + String(WiFi.RSSI());
  json += ",\"rtc_synced\":false";
  json += "}";

  Serial.println();
  Serial.println("[API] Mengirim data...");
  Serial.println("[API] URL: " + String(API_URL));
  Serial.println("[API] Payload: " + json);

  int httpCode = http.POST(json);

  if (httpCode > 0)
  {
    String response = http.getString();
    Serial.print("[API] HTTP Code: ");
    Serial.println(httpCode);
    Serial.print("[API] Response: ");
    Serial.println(response);
    http.end();
    return (httpCode == 201);
  }
  else
  {
    Serial.print("[API] Error: ");
    Serial.println(http.errorToString(httpCode));
    http.end();
    return false;
  }
}

// =============================================================
// Serial Monitor Output (Debug)
// =============================================================

void printReadings(float temp, float hum, float ch4, float co, float co2)
{
  Serial.println();
  Serial.println("==============================================================");
  Serial.println("               SIMOSI AIR QUALITY MONITOR");
  Serial.println("==============================================================");

  // DEBU TAMBANG
  Serial.println();
  Serial.println("============== DEBU TAMBANG =================");
  Serial.println("PM2.5       : -- (sensor belum terpasang)");
  Serial.println("PM10        : -- (sensor belum terpasang)");

  if (!isnan(temp))
  {
    Serial.print("Temperature : ");
    Serial.print(temp, 1);
    Serial.println(" °C");
  }
  if (!isnan(hum))
  {
    Serial.print("Humidity    : ");
    Serial.print(hum, 1);
    Serial.println(" %");
  }

  // GAS TAMBANG
  Serial.println();
  Serial.println("============== GAS TAMBANG ==================");
  Serial.print("CH4         : ");
  Serial.print(ch4, 2);
  Serial.println(" ppm");
  Serial.println("H2S         : -- (MQ136 belum terpasang)");

  // EMISI ALAT BERAT
  Serial.println();
  Serial.println("=========== EMISI ALAT BERAT ================");
  Serial.print("CO          : ");
  Serial.print(co, 2);
  Serial.println(" ppm");
  Serial.print("CO2 (est)   : ");
  Serial.print(co2, 2);
  Serial.println(" ppm");

  // DEVICE INFO
  Serial.println();
  Serial.println("============== DEVICE INFO ==================");
  Serial.print("WiFi RSSI   : ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
  Serial.print("WiFi Status : ");
  Serial.println(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
  Serial.print("Free Heap   : ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");
  Serial.println("==============================================================");
}

// =============================================================
// SETUP
// =============================================================

void setup()
{
  Serial.begin(115200);

  Serial.println();
  Serial.println("==============================================================");
  Serial.println("          SIMOSI - SMART AIR MONITORING SYSTEM");
  Serial.println("          Firmware v1.1");
  Serial.println("==============================================================");

  // Init sensor
  dht.begin();
  analogReadResolution(12);

  // Init WiFi
  connectWiFi();

  Serial.println("[INIT] Device code: " + String(DEVICE_CODE));
  Serial.println("[INIT] API URL: " + String(API_URL));
  Serial.println("[INIT] Interval: " + String(READING_INTERVAL / 1000) + " detik");
  Serial.println("[INIT] Setup selesai. Mulai monitoring...");
  Serial.println();
}

// =============================================================
// LOOP
// =============================================================

void loop()
{
  // Pastikan WiFi terhubung
  connectWiFi();

  // 1. Baca semua sensor
  float temperature = dht.readTemperature();
  float humidity    = dht.readHumidity();
  float ch4_ppm     = readCH4_ppm();
  float co_ppm      = readCO_ppm();
  float co2_ppm     = readCO2_ppm();

  // 2. Print ke Serial Monitor (debug)
  printReadings(temperature, humidity, ch4_ppm, co_ppm, co2_ppm);

  // 3. Kirim ke SIMOSI API
  bool success = sendToAPI(temperature, humidity, ch4_ppm, co_ppm, co2_ppm);
  if (success)
  {
    Serial.println("[OK] Data berhasil dikirim ke server!");
  }
  else
  {
    Serial.println("[WARN] Gagal kirim data.");
  }

  // 4. Periksa apakah ada perintah remote control dari server
  checkAndExecuteCommands();

  // 5. Tunggu interval
  Serial.println();
  Serial.print("[WAIT] Pembacaan berikutnya dalam ");
  Serial.print(READING_INTERVAL / 1000);
  Serial.println(" detik...");

  delay(READING_INTERVAL);
}
