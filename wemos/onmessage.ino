#DEFINE MAX_CHAR

int mqtt_read_int(){
  char str[10];  
  int acumulator = 0;
  while (true) {
    char ch = mqttCleint.peek();
    if (ch == '\n' || ch == ' '){
      break;
    }
    acumulator *=10;
    char c = mqttClient.read();
    acumulator += c - '0';
  }
  return;
}

int mqtt_clean(){
  while (true) {
    char ch = mqttClient.read();

    if (ch == '\n'){
      break;
    }
  }
  return;
}



void onMqttMessage(int messageSize) {

  // we received a message, print out the topic and contents
  Serial.println("Received a message with topic '");
  Serial.print(mqttClient.messageTopic());
  Serial.print("', length ");
  Serial.print(messageSize);
  Serial.println(" bytes:");


  if(mqttClient.messageTopic() == TOPIC_THRESHOLD){

  }
  else{
    int id = mqtt_read_int();
    if(id != MQTT_ID){
      mqtt_clean();
    }

  }

  Serial.println();
  Serial.println();
}