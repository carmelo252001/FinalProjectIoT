uint8_t Pwm1 = D1; //Nodemcu PWM pin 
uint8_t Pwm2 = D2; //Nodemcu PWM pin

void setup() { 
  Serial.begin(115200);
  delay(10);
  pinMode(D7, OUTPUT);   
  pinMode(D8, OUTPUT);
  
  Serial.println("Hello from the setup function");
} 

void loop() { 
  Serial.println("The motor should start now!");
  
  analogWrite(Pwm1, 512);  //Pwm duty cycle 50%  
  analogWrite(Pwm2, 512);  //Pwm duty cycle 50%
  
  analogWrite(D7, LOW);
  analogWrite(D8, HIGH);
  delay(10000);
}
