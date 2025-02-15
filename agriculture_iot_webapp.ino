#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "Vishal";
const char* password = "Vishal123";

// MQTT Broker details
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_password = "";

// MQTT Topics for Mobile
const char* rain_topic = "sensor/rain";
const char* dht_topic = "sensor/dht";
const char* soil_topic = "sensor/soil";



// Pin Definitions
#define RAIN_SENSOR_PIN D6
#define DHT_PIN D4
#define SOIL_MOISTURE_PIN D5

// Initialize DHT sensor
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);

// Initialize WiFi and MQTT client
WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("NodeMCUClient", mqtt_user, mqtt_password)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RAIN_SENSOR_PIN, INPUT);
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read rain sensor value (Digital)
  int rainValue = digitalRead(RAIN_SENSOR_PIN);
  Serial.print("Rain Value: ");
  Serial.println(rainValue);
  if(rainValue == 1)
  {
  client.publish(rain_topic, String(rainValue).c_str());
  
  }
  if(rainValue == 0)
  {
  client.publish(rain_topic, String(rainValue).c_str());
  
  }

  // Read DHT sensor values
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.print(" %\t");
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" *C");
   client.publish(dht_topic, ("Temperature: " + String(temperature) + " *C, Humidity: " + String(humidity) + " %").c_str());
    
  }

  // Read soil moisture sensor value (Digital)
  int soilMoistureValue = digitalRead(SOIL_MOISTURE_PIN);
  Serial.print("Soil Moisture Value: ");
  Serial.println(soilMoistureValue);
  if(soilMoistureValue==1)
  {
 client.publish(soil_topic, String(soilMoistureValue).c_str());
  
  }
  if(soilMoistureValue==0)
  {
  client.publish(soil_topic, String(soilMoistureValue).c_str());
  
  delay(10000); // Wait for 10 seconds before next reading
}
}