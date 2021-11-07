#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <EMailSender.h>
#include "DHTesp.h"

DHTesp dht;
const char* ssid = "TP-LINK_516E";
const char* password = "21757969";
const char* mqtt_server = "192.168.0.107";

int desired_temperature = 40;
bool email_sent = false;

bool light_is_on = false;
int desired_light = 900;

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
  messagein.trim();
  
  if(topic=="IoTlab/light"){
    if (messagein == "ON") {
      Serial.println("Light is ON");
      digitalWrite(D1, HIGH);
    } else{
      Serial.println("Light is OFF");
      digitalWrite(D1, LOW);
    }
  }else if(topic=="IoTlab/temperature_desired"){
    desired_temperature = messagein.toInt();
    Serial.println("Received a new desired temperature " + messagein);
  }else if(topic=="IoTlab/light_desired"){
    desired_light = messagein.toInt();
    Serial.println("Received a new desired light intensity " + messagein);
  }
}


void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("vanieriot")) {
      Serial.println("connected");  
      client.subscribe("IoTlab/light");
      client.subscribe("IoTlab/temperature_desired");
      client.subscribe("IoTlab/light_desired");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void send_email(String message_to_send){
  EMailSender emailSend("waterisnoticecream@gmail.com", "Banana123!");
  EMailSender::EMailMessage message;
  message.subject = "Subject";
  message.message = message_to_send;
  EMailSender::Response resp = emailSend.send("waterisnoticecream@gmail.com", message);
  Serial.print("Message is being sent... ");
  Serial.println(resp.desc);
}

void turn_on_lights(){
  digitalWrite(D3, HIGH);
  digitalWrite(D4, HIGH);
  send_email("The light intensity is lower than threshold. Lights are ON!");
}

void turn_off_lights(){
  digitalWrite(D3, LOW);
  digitalWrite(D4, LOW);
  send_email("The light intensity is higher than threshold. Lights are OFF!");
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  dht.setup(4, DHTesp::DHT11);
  pinMode(D1, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);
  digitalWrite(D1, HIGH);
  digitalWrite(D3, LOW);
  digitalWrite(D4, LOW);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  if(!client.loop())
    client.connect("vanieriot");

  float temp= dht.getTemperature();
  float hum= dht.getHumidity();
  float light_intensity= analogRead(D0);
  
  char tempArr [8];
  dtostrf(temp,6,2,tempArr);
  char humArr [8];
  dtostrf(hum,6,2,humArr);
  char lightArr [8];
  dtostrf(light_intensity,6,2,lightArr);
  
  client.publish("IoTlab/temperature", tempArr);
  client.publish("IoTlab/humidity", humArr);
  client.publish("IoTlab/light_intensity", lightArr);

  if(temp > desired_temperature && !email_sent){
    send_email("Would you like to turn on the fan? (YES or NO)");
    email_sent = true;
  }

  //Turn on or off the light depending on the situation
  if(light_intensity < desired_light && !light_is_on){
    turn_on_lights();
    light_is_on = true;
  } else if(light_intensity > desired_light && light_is_on){
    turn_off_lights();
    light_is_on = false;
  }

  delay(10000);
}
