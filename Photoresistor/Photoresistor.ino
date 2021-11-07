void setup() {
  Serial.begin(115200);
}


void loop() {
  int value = analogRead(D0);
  Serial.println("Analog value : ");
  Serial.println(value);
  delay(10000);
}
