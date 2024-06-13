SensorData d(0,0,0,0);
const char* actions[4]= {"water","heat","light","humidity"};

//set interval for sending messages (milliseconds)
const long INTERVAL = 5000u;
unsigned long previousMillis = 0;

int read_from_arduino() {
  if (!Serial.available()) {
    return -1;
  }

  while(Serial.available()) {
    int command = Serial.parseInt();
    int a;
    switch(command){
      case 1:
        d.light = Serial.parseInt();
        d.soil_moisture = Serial.parseInt();
        d.humidity = Serial.parseInt();
        d.temperature = Serial.parseInt();
        break;
      case 2:
        a = Serial.parseInt();

        mqttClient.beginMessage(TOPIC_ACTIONS);
        mqttClient.print(MQTT_ID);
        mqttClient.print(" ");
        mqttClient.print(actions[a]);
        mqttClient.endMessage();
        break;
      case 0:
        Serial.readStringUntil('\n');
        break;
      default:
        break;
    }

  }
  
  return 1;
}

void loop() {
  // call poll() regularly to allow the library to send MQTT keep alives which
  // avoids being disconnected by the broker
  mqttClient.poll();
  read_from_arduino();
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    // save the last time a message was sent
      mqttClient.beginMessage(TOPIC_POOL);
      mqttClient.print(MQTT_ID);
      mqttClient.print("*");
      mqttClient.print(d.toString());
      mqttClient.endMessage();
      previousMillis = millis();
    }
}