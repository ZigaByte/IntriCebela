#include <Wire.h>

const int buttonPinA = 2;
const int buttonPinB = 3;
const int buttonPinC = 4;
const int buttonPinD = 5;
const int buttonPinE = 6;
const int buttonPinF = 7;
const int buttonPinG = 8;
const int buttonPinH = 9;
const int buttonPinI = 10;
const int buttonPinJ = 11;
const int buttonPinK = 12;
const int buttonPinL = 13;

const int i2cAddress = 0x08;

void setup() {
  pinMode(buttonPinA, INPUT);
  pinMode(buttonPinB, INPUT);
  pinMode(buttonPinC, INPUT);
  pinMode(buttonPinD, INPUT);
  pinMode(buttonPinE, INPUT);
  pinMode(buttonPinF, INPUT);
  pinMode(buttonPinG, INPUT);
  pinMode(buttonPinH, INPUT);
  pinMode(buttonPinI, INPUT);
  pinMode(buttonPinJ, INPUT);
  pinMode(buttonPinK, INPUT);
  pinMode(buttonPinL, INPUT);
  
  Wire.begin(i2cAddress);
  Wire.onRequest(requestEvent); 
}

char lastButton = '0';
int timeSinceLastButtonPress = 0;
const int timePerLoop = 10;
void loop() {
  delay(timePerLoop);

  if(digitalRead(buttonPinA) == HIGH){
      lastButton = 'A';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinB) == HIGH){
      lastButton = 'B';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinC) == HIGH){
      lastButton = 'C';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinD) == HIGH){
      lastButton = 'D';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinE) == HIGH){
      lastButton = 'E';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinF) == HIGH){
      lastButton = 'F';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinG) == HIGH){
      lastButton = 'G';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinH) == HIGH){
      lastButton = 'H';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinI) == HIGH){
      lastButton = 'I';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinJ) == HIGH){
      lastButton = 'J';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinK) == HIGH){
      lastButton = 'K';
      timeSinceLastButtonPress = 0;
  }
  else if(digitalRead(buttonPinL) == HIGH){
      lastButton = 'L';
      timeSinceLastButtonPress = 0;
  }else{
    timeSinceLastButtonPress += timePerLoop;

    if(timeSinceLastButtonPress >= 3000){
      lastButton = '0';
      timeSinceLastButtonPress = 0;
    }
  } 
}

void requestEvent() {
  Wire.write(lastButton);
}
