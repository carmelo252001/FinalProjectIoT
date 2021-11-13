#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <EMailSender.h>
#include <SPI.h>
#include <MFRC522.h>
#include "DHTesp.h"
#define D3 0
#define D4 2
constexpr uint8_t RST_PIN = D3;
constexpr uint8_t SS_PIN = D4;


// Set up the variables for RFID
MFRC522 rfid(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;
String tag;
String current_user = "Carmelo";
int prefered_temp_carmelo = 20;
int prefered_light_carmelo = 700;
int prefered_temp_akash = 15;
int prefered_light_akash = 600;

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
bool email_received = false;


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
    if (current_user == "Carmelo") {
      prefered_temp_carmelo = messagein.toInt();
    } else {
      prefered_temp_akash = messagein.toInt();
    }
  } else if(topic=="IoTlab/light_desired") {
    desired_light = messagein.toInt();
    Serial.println("Received a new desired light intensity " + messagein);
    if (current_user == "Carmelo") {
      prefered_light_carmelo = messagein.toInt();
    } else {
      prefered_light_akash = messagein.toInt();
    }
  } else if(topic=="IoTlab/received_email") {
    Serial.println("We have received a response: " + messagein);
    email_received = true;
    email_sent = false;
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


// Turns the blue and green lights on
void turn_on_lights(){
  digitalWrite(D7, HIGH);
  digitalWrite(D8, HIGH);
  send_email("The light intensity is lower than threshold. Lights are now ON!");
}


// Turns the blue and green lights off
void turn_off_lights(){
  digitalWrite(D7, LOW);
  digitalWrite(D8, LOW);
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
  pinMode(D7, OUTPUT);
  pinMode(D8, OUTPUT);
  digitalWrite(D1, HIGH);
  digitalWrite(D7, LOW);
  digitalWrite(D8, LOW);

  // Set up for the RFID
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522
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
  if (temp > desired_temperature && !email_sent && !email_received) {
    double send_email= 1;
    
    char tempSend [8];
    dtostrf(send_email,6,2,tempSend);
    
    client.publish("IoTlab/send_email", tempSend);
    email_sent = true;
  }

  // Verifies if email was received from the user
  if (temp < desired_temperature){
    email_received = false;
  }

  // Sends an email to the user if light is below desired threshold
  if (light_intensity < desired_light && !light_is_on) {
    turn_on_lights();
    light_is_on = true;
  } else if (light_intensity > desired_light && light_is_on) {
    turn_off_lights();
    light_is_on = false;
  }

  // Loops used to read the RFID tags
  if ( ! rfid.PICC_IsNewCardPresent())
    return;
  if (rfid.PICC_ReadCardSerial()) {
    for (byte i = 0; i < 4; i++) {
      tag += rfid.uid.uidByte[i];
    }
    
    Serial.println(tag);
    if (tag == "204173223110" && current_user == "Akash") {
      // Creates a notification on top of the screen
      String message = "Welcome back Carmelo!";
      char tempTag [25];
      message.toCharArray(tempTag, message.length());
      client.publish("IoTlab/current_user_notification", tempTag);

      // Prints out the name of the user on top of the screen
      String message2 = "Hello Carmelo";
      char tempTag2 [25];
      message2.toCharArray(tempTag2, message2.length() + 1);
      client.publish("IoTlab/current_user", tempTag2);

      // Sends the users prefered temperature and light threshold
      char tempTag3 [8];
      dtostrf(prefered_temp_carmelo ,6,2,tempTag3);
      client.publish("IoTlab/user_temperature_threshold", tempTag3);
      char tempTag4 [8];
      dtostrf(prefered_light_carmelo ,6,2,tempTag4);
      client.publish("IoTlab/user_light_threshold", tempTag4);

      // Sends the email to the admin saying that Carmelo was here
      client.publish("IoTlab/message_carmelo", tempTag2);
      current_user = "Carmelo";
    } else if (tag == "9924674" && current_user == "Carmelo") {
      // Creates a notification on top of the screen
      String message = "Welcome back Akash!";
      char tempTag [25];
      message.toCharArray(tempTag, message.length());
      client.publish("IoTlab/current_user_notification", tempTag);

      // Prints out the name of the user on top of the screen
      String message2 = "Hello Akash";
      char tempTag2 [25];
      message2.toCharArray(tempTag2, message2.length() + 1);
      client.publish("IoTlab/current_user", tempTag2);

      // Sends the users prefered temperature and light threshold
      char tempTag3 [8];
      dtostrf(prefered_temp_akash ,6,2,tempTag3);
      client.publish("IoTlab/user_temperature_threshold", tempTag3);
      char tempTag4 [8];
      dtostrf(prefered_light_akash ,6,2,tempTag4);
      client.publish("IoTlab/user_light_threshold", tempTag4);

      // Sends the email to the admin saying that Akash was here
      client.publish("IoTlab/message_akash", tempTag2);
      current_user = "Akash";
    } else if (tag != "204173223110" && tag != "9924674"){
      // Sends an email saying that an invalid user tried entering and sets buzzer
      String message = "Invalid user!!!";
      char tempTag [25];
      message.toCharArray(tempTag, message.length());
      client.publish("IoTlab/current_user_notification", tempTag);
      client.publish("IoTlab/buzzer", tempTag);
    }
    
    tag = "";
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }

  delay(10000);
}
