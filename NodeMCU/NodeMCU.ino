#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <EMailSender.h>
#include "DHTesp.h"


// Set up the MQTT  and WiFi connection
WiFiClient vanieriot;
PubSubClient client(vanieriot);
const char* ssid = "TP-LINK_516E";
const char* password = "21757969";
const char* mqtt_server = "192.168.0.107";

// Set up the variables used with the sensors
DHTesp dht;
int desired_temperature = 40;
bool light_is_on = false;
int desired_light = 900;
bool email_sent = false;


// Set up the WiFi connection
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


// Function called whenever a messaged is received from the MQTT connection
void callback(String topic, byte* message, unsigned int length) {
  // Gets the received message and transfers it into a string
  Serial.print("Message arrived on topic: ");
  Serial.print(topic + ". ");
  Serial.print("Message: ");
  String messagein;
  for (int i = 0; i < length; i++) {
    messagein += (char)message[i];
  }
  Serial.println(messagein);
  messagein.trim();

  // Now verifies from which topic it came from
  if (topic=="IoTlab/light") {
    if (messagein == "ON") {
      Serial.println("Light is ON");
      digitalWrite(D1, HIGH);
    } else {
      Serial.println("Light is OFF");
      digitalWrite(D1, LOW);
    }
  } else if(topic=="IoTlab/temperature_desired") {
    desired_temperature = messagein.toInt();
    Serial.println("Received a new desired temperature " + messagein);
  } else if(topic=="IoTlab/light_desired") {
    desired_light = messagein.toInt();
    Serial.println("Received a new desired light intensity " + messagein);
  } else if(topic=="IoTlab/received_email") {
    Serial.println("We have received a response: " + messagein);
    email_sent = false;
    if (messagein == "a") {
      turn_motor_on();
    } else if (messagein == "b") {
      turn_motor_off();
    }
  }
}


// Creates the connection with the MQTT server and subscribes to the topics
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("vanieriot")) {
      Serial.println("connected");  
      client.subscribe("IoTlab/light");
      client.subscribe("IoTlab/temperature_desired");
      client.subscribe("IoTlab/light_desired");
      client.subscribe("IoTlab/received_email");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}


// Turns the motor on
void turn_motor_on(){
  //add code to turn on the motor
  Serial.println("Turn on the motor!");
}


// Turns the motor off
void turn_motor_off(){
  //add code to turn off the motor
  Serial.println("Turn off the motor!");
}


// Turns the blue and green lights on
void turn_on_lights(){
  digitalWrite(D3, HIGH);
  digitalWrite(D4, HIGH);
  send_email("The light intensity is lower than threshold. Lights are now ON!");
}


// Turns the blue and green lights off
void turn_off_lights(){
  digitalWrite(D3, LOW);
  digitalWrite(D4, LOW);
  send_email("The light intensity is higher than threshold. Lights are now OFF!");
}


// Sends an email containing the desired message
void send_email(String message_to_send){
  EMailSender emailSend("waterisnoticecream@gmail.com", "Banana123!");
  EMailSender::EMailMessage message;
  message.subject = "Subject";
  message.message = message_to_send;
  EMailSender::Response resp = emailSend.send("waterisnoticecream@gmail.com", message);
  Serial.print("Message is sending... ");
  Serial.println(resp.desc);
}


// Sets up the NodeMCU functionalities
void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  dht.setup(4, DHTesp::DHT11);

  // Puts the lights in their default position
  pinMode(D1, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);
  digitalWrite(D1, HIGH);
  digitalWrite(D3, LOW);
  digitalWrite(D4, LOW);
}


// Function called repeatedly during the lifetime of the NodeMCU
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  if (!client.loop()) {
    client.connect("vanieriot");
  }

  // Gets the current Temperature, Humidity, and Light Intentisity
  float temp= dht.getTemperature();
  float hum= dht.getHumidity();
  float light_intensity= analogRead(D0);

  // Converts the previous values into char arrays
  char tempArr [8];
  dtostrf(temp,6,2,tempArr);
  char humArr [8];
  dtostrf(hum,6,2,humArr);
  char lightArr [8];
  dtostrf(light_intensity,6,2,lightArr);

  // Publishes the char arrays into their respected topics
  client.publish("IoTlab/temperature", tempArr);
  client.publish("IoTlab/humidity", humArr);
  client.publish("IoTlab/light_intensity", lightArr);

  // Sends an email to the user if temperature is below desired threshold
  if (temp > desired_temperature && !email_sent) {
    double send_email= 1;
    
    char tempSend [8];
    dtostrf(send_email,6,2,tempSend);
    
    client.publish("IoTlab/send_email", tempSend);
    email_sent = true;
  }

  // Sends an email to the user if temperature is below desired threshold
  if (light_intensity < desired_light && !light_is_on) {
    turn_on_lights();
    light_is_on = true;
  } else if (light_intensity > desired_light && light_is_on) {
    turn_off_lights();
    light_is_on = false;
  }

  delay(10000);
}
