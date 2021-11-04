#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

DHTesp dht;
const char* ssid = "TP-LINK_516E";
const char* password = "21757969";
const char* mqtt_server = "192.168.0.104";

WiFiClient vanieriot;
PubSubClient client(vanieriot);


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
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
}


void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic + ". ");
  Serial.print("Message: ");
  String messagein;
  for (int i = 0; i < length; i++) {
    messagein += (char)message[i];
  }
  Serial.println(messagein);

  if(topic=="IoTlab/light"){
    if (messagein == "ON") {
      Serial.println("Light is ON");
      digitalWrite(D1, HIGH);
    } else{
      Serial.println("Light is OFF");
      digitalWrite(D1, LOW);
    }
  }
}


void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("vanieriot")) {
      Serial.println("connected");  
      client.subscribe("IoTlab/light");
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
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  dht.setup(4, DHTesp::DHT11);
  pinMode(D1, OUTPUT);
  digitalWrite(D1, HIGH);
}


void loop() {
  if (!client.connected()) {
    reconnect();
  }
  if(!client.loop())
    client.connect("vanieriot");

  float temp= dht.getTemperature();
  float hum= dht.getHumidity();
    
  char tempArr [8];
  dtostrf(temp,6,2,tempArr);
  char humArr [8];
  dtostrf(hum,6,2,humArr);
      
  client.publish("IoTlab/temperature", tempArr);
  client.publish("IoTlab/humidity", humArr);
  
  delay(10000);
}
