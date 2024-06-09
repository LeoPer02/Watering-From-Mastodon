SensorData d(0,0,0,0);
Threshold t[] = {{100,200},{100,200},{},{}};
const char* actions[4]= {"light","water","heat","temperature"};

//set interval for sending messages (milliseconds)
const long INTERVAL = 5000u;
unsigned long previousMillis = 0;

int read_from_arduino() {
  if (!Serial.available()) {
    return -1;
  }

  while(Serial.available()) {
    int command = Serial.parseInt();
    if (command == 1){
      d.light = Serial.parseInt();
      d.soil_moisture = Serial.parseInt();
      d.humidity = Serial.parseInt();
      d.temperature = Serial.parseInt();

    } else if (command == 2) {
      int a = Serial.parseInt();

      mqttClient.beginMessage(TOPIC_ACTIONS);
      mqttClient.print(MQTT_ID);
      mqttClient.print(" ");
      mqttClient.print(actions[a]);
      mqttClient.endMessage();
    }
  }
  
  mqttClient.beginMessage(TOPIC_POOL);
  mqttClient.print(MQTT_ID);
  mqttClient.print("*");
  mqttClient.print(d.toString());
  mqttClient.endMessage();
  return 1;
}

void loop() {
  // call poll() regularly to allow the library to send MQTT keep alives which
  // avoids being disconnected by the broker
  mqttClient.poll();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= INTERVAL) {
    // save the last time a message was sent
    previousMillis = currentMillis;
    read_from_arduino();
    }
}