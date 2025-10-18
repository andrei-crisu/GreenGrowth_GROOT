#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <DHT.h>
#include "settings.h"

#define PIN_SENZOR_UMIDITATE_SOL 1
#define PIN_SENZOR_TEMP 2
#define DHT_TYPE DHT11


#define READ_DB 1
#define WRITE_DB 2

uint8_t temperatura_solar = 0;
uint8_t umiditate_solar = 0;
uint8_t umiditate_sol = 0;
bool stare_pompa = false;


// Obiecte Firebase
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

void read_DHT()
{

  umiditate_solar = (uint8_t)dht.readHumidity();
  temperatura_solar = (uint8_t)dht.readTemperature();
}
void debug_log(uint8_t cod)
{
  Serial.println("Temperatura solar: ");
  Serial.println(temperatura_solar);
  Serial.println("Umiditate solar: ");
  Serial.println(umiditate_solar);
  Serial.println("Umiditate sol: ");
  Serial.println(umiditate_sol);
  Serial.print(" Cod debug");
  Serial.println(cod);

}
void read_DB()
{
  if (Firebase.RTDB.getInt(&fbdo, "/test/value")) {
    if (fbdo.dataType() == "int") {
      Serial.print("Valoare citită: ");
      Serial.println(fbdo.intData());
    }
  } else {
    Serial.println(fbdo.errorReason());
  }
  debug_log(READ_DB);
}

void write_DB()
{
  if (Firebase.RTDB.setInt(&fbdo, "/test/value", 123)) {
    Serial.println("Date trimise cu succes!");
  } else {
    Serial.println(fbdo.errorReason());
  }
  debug_log(WRITE_DB);
}

void setup() {
  Serial.begin(115200);

  // Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectare la Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println("\nConectat!");

  // Conf Firebase
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  // Dacă nu folosești autentificare, lasă email și parolă goale
  auth.user.email = "";
  auth.user.password = "";

  // Init
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  read_DB();

  write_DB();
}

void loop() 
{
  read_DHT();


  // Poți actualiza sau citi date periodic aici
}
