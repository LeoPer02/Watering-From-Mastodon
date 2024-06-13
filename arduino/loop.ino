int light(){
  if(d.light > t[2].high) {
    green.activate();
    return 1;
  }
  else if(d.light < t[2].low) {
    yellow.activate();
    Serial.println("2 2");
    return -1;
  }
  return 0;
}

int water(){
  if(d.soil_moisture > t[0].high){
    blue.activate();
    Serial.println("2 0");
    return 1;
  }
  else if(d.soil_moisture < t[0].low){
    return -1;
  }
  return 0;
}

int read_from_arduino(){
  if (!Serial.available()) {
    return -1;
  }
  while(Serial.available()) {
    int command = Serial.parseInt();
    int a=0;
    switch(command){
      case 1:
        for(int i =0; i < 4; i++){
          t[i].low = Serial.parseInt();
          t[i].high = Serial.parseInt();

          Serial.println("0 "+ String(t[i].low) + " " + String(t[i].high) + " ");
        } 
        break;
      case 2:
        a = Serial.parseInt();
        Serial.println("0 "+ String(a));
        switch(a){
          case 0:
            blue.activate();
            break;
          case 1:
            red.activate();
            break;
          case 2:
            yellow.activate();
            break;
          case 3:
            green.activate();
            break;
          default:
            break;
        }
        //do command here 
        break;
      case 0:
        Serial.readStringUntil('\n');
        break;
    }
  }
  return 0;
}

const long INTERVAL = 1000u;
unsigned long previousMillis = 0;

void loop() {
  d.light = analogRead(LIGHT_SENSOR_PIN);
  d.soil_moisture = analogRead(WATER_SENSOR_PIN)/3;
  d.humidity      = 0;
  d.temperature   = 0;

  //new thresholds
  read_from_arduino();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    light();
    water();

    Serial.println("1 " + d.toString());
    previousMillis = millis();
  }
}