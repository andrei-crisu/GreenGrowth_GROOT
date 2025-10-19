#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <time.h>
//Provide the token generation process info.
#include "addons/TokenHelper.h"
//Provide the RTDB payload printing info and other helper functions.
#include "addons/RTDBHelper.h"
#include <DHT.h>

// WiFi credentials
#define WIFI_SSID "CRAIOVA HACKATON"
#define WIFI_PASSWORD "20252025"

// Firebase configuration
#define API_KEY "AIzaSyBj3A2B8LSgEA1_OUOZlU8sQp4njnxXOis"
#define DATABASE_URL "https://groot-f61e8-default-rtdb.europe-west1.firebasedatabase.app/"

#define UPDATE_INTERVAL_MS          15000
#define SENSOR_AIR_TEMP_HUMID_PIN   9
#define SENSOR_SOIL_HUMID_PIN       10
#define SENSOR_LIGHT_PIN            11


DHT dht11(SENSOR_AIR_TEMP_HUMID_PIN, DHT11);

// NTP Server for time sync
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 7200;      // GMT+1 for Romania (adjust if needed)
const int daylightOffset_sec = 3600;  // Daylight saving time

// Firebase objects
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// Device UID based on MAC address
String DEVICE_UID = "";
String DEVICE_NAME = "";  // User-customizable device name
bool deviceRegistered = false;

unsigned long sendDataPrevMillis = 0;
unsigned long checkNamePrevMillis = 0;
bool signupOK = false;

// Function to get current timestamp as ISO 8601 string
String getCurrentTimestamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return String(millis()); // Fallback to millis if time not synced
  }
  char timeString[30];
  strftime(timeString, sizeof(timeString), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(timeString);
}

// Register device in Firebase with default name
void registerDevice() {
  if (!Firebase.ready() || !signupOK) return;
  
  String deviceInfoPath;
  deviceInfoPath = String("/devices/");
  deviceInfoPath += DEVICE_UID;
  deviceInfoPath += "/info";
  
  String deviceNamePath = deviceInfoPath;
  deviceNamePath += "/name";
  
  // Check if device already exists
  if (Firebase.RTDB.getString(&fbdo, deviceNamePath.c_str())) {
    // Device exists, get current name
    DEVICE_NAME = fbdo.stringData();
    Serial.print("✅ Device found. Name: ");
    Serial.println(DEVICE_NAME);
    deviceRegistered = true;
  } else {
    // Device doesn't exist, create with default name
    String lastSixChars = DEVICE_UID.substring(6);
    DEVICE_NAME = String("ESP32_");
    DEVICE_NAME += lastSixChars;
    
    FirebaseJson deviceInfo;
    deviceInfo.set("name", DEVICE_NAME);
    deviceInfo.set("mac_address", DEVICE_UID);
    deviceInfo.set("registered_at", getCurrentTimestamp());
    deviceInfo.set("status", "online");
    
    if (Firebase.RTDB.setJSON(&fbdo, deviceInfoPath.c_str(), &deviceInfo)) {
      Serial.print("📝 Device registered with name: ");
      Serial.println(DEVICE_NAME);
      deviceRegistered = true;
    } else {
      Serial.print("❌ Device registration failed: ");
      Serial.println(fbdo.errorReason());
    }
  }
}

// Check for device name updates from Firebase
void checkDeviceNameUpdate() {
  if (!Firebase.ready() || !signupOK) return;
  
  String deviceNamePath;
  deviceNamePath = String("/devices/");
  deviceNamePath += DEVICE_UID;
  deviceNamePath += "/info/name";
  
  if (Firebase.RTDB.getString(&fbdo, deviceNamePath.c_str())) {
    String newName = fbdo.stringData();
    if (newName != DEVICE_NAME) {
      DEVICE_NAME = newName;
      Serial.print("🔄 Device name updated to: ");
      Serial.println(DEVICE_NAME);
    }
  }
}

void setup() 
{
  Serial.begin(115200);
  
  dht11.begin(); // initialize the DHT11 sensor

  
  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  
  // Get MAC address as device UID (remove colons for clean ID)
  DEVICE_UID = WiFi.macAddress();
  DEVICE_UID.replace(":", "");
  Serial.print("Device UID (MAC): ");
  Serial.println(DEVICE_UID);
  Serial.println();
  
  // Initialize time sync
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.println("Syncing time with NTP server...");
  delay(2000);

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Sign up */
  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("Firebase signup OK");
    signupOK = true;
  }
  else {
    Serial.printf("Signup error: %s\n", config.signer.signupError.message.c_str());
  }

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  
  // Wait for Firebase to be ready
  Serial.println("Waiting for Firebase...");
  int attempts = 0;
  while (!Firebase.ready() && attempts < 50) {
    Serial.print(".");
    delay(200);
    attempts++;
  }
  Serial.println();
  
  // Register device
  if (Firebase.ready() && signupOK) {
    registerDevice();
  }
}

void loop() {
  // Check for device name updates every 30 seconds
  if (Firebase.ready() && signupOK && (millis() - checkNamePrevMillis > 30000 || checkNamePrevMillis == 0)) {
    checkNamePrevMillis = millis();
    checkDeviceNameUpdate();
  }
  
  // Send sensor data every 2 seconds
  if (Firebase.ready() && signupOK && deviceRegistered && (millis() - sendDataPrevMillis > UPDATE_INTERVAL_MS || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();
	
	// Sensor read
    int moisture_val_ADC = analogRead(SENSOR_SOIL_HUMID_PIN);
    int moisture = map(moisture_val_ADC, 0, 4096, 100, 0);
    
    float temperature = 0;
    float humidity = 0;
    temperature = dht11.readTemperature();
    humidity = dht11.readHumidity();
    
    // int light_level_val_ADC = analogRead(SENSOR_LIGHT_PIN);
    // int light_level = map(light_level_val_ADC, 0, 4096, 0, 100);
    int light_level = analogRead(SENSOR_LIGHT_PIN);
    
    // Simulate sensor readings (replace with actual sensor values)
    //float humidity = 45.0 + random(0, 30);        // 45-75%
    //float temperature = 20.0 + random(0, 15);     // 20-35°C
    // int light_level = 300 + random(0, 700);       // 300-1000 lux
    //float moisture = 30.0 + random(0, 40);        // 30-70%
    float pressure = 1010.0 + random(0, 20);      // 1010-1030 hPa
    
    // Get current timestamp
    String timestamp = getCurrentTimestamp();
    
    // Create sensor data JSON
    FirebaseJson json;
    json.set("device_name", DEVICE_NAME);         // Include device name in data
    json.set("mac_address", DEVICE_UID);
    json.set("humidity", humidity);
    json.set("temperature", temperature);
    json.set("light_level", light_level);
    json.set("moisture", moisture);
    json.set("pressure", pressure);
    json.set("timestamp", timestamp);

    // Create path: /devices/[MAC_ADDRESS]/readings/[timestamp_millis]
    String path;
    path = String("/devices/");
    path += DEVICE_UID;
    path += "/readings/";
    path += String(millis());

    // Send JSON to Firebase
    if (Firebase.RTDB.setJSON(&fbdo, path.c_str(), &json)) {
      Serial.print("✅ [");
      Serial.print(DEVICE_NAME);
      Serial.println("] Data sent!");
      Serial.print("Humidity: ");
      Serial.print(humidity);
      Serial.print("% | Temp: ");
      Serial.print(temperature);
      Serial.print("°C | Light: ");
      Serial.print(light_level);
      Serial.print(" | Moisture: ");
      Serial.print(moisture);
      Serial.print("% | Pressure: ");
      Serial.print(pressure);
      Serial.println(" hPa");
    }
    else {
      Serial.println("❌ FAILED");
      Serial.print("REASON: ");
      Serial.println(fbdo.errorReason());
    }
  }
}

