#define MAX_CHAR 30

int mqtt_read_int(){
  int acumulator = 0;
  while (mqttClient.available()) {
    char ch = mqttClient.read();

    if (ch == '\n' || ch == ' '){
      break;
    }
    acumulator *=10;
    acumulator += ch - '0';
  }
  return acumulator;
}

int mqtt_read_word(){
  char temp[] = {'\0','\0','\0','\0','\0','\0','\0','\0','\0','\0'};
  int i = 0;
  while (mqttClient.available()) {
    char ch = mqttClient.read();
    if (ch == '\n'){
      break;
    }
    temp[i] = ch;
    i++;
    if(i >= 10){return -1;}
  }
  //Serial.println(temp);
  switch(temp[0]){
    case 'w':
      return 0;
    case 'h':
      return 1;
    case 'l':
      return 2;
    default:
      return 3;
  }
}

void mqtt_clean(){
  while (mqttClient.available()) {
    char ch = mqttClient.read();

    if (ch == '\n'){
      break;
    }
  }
  return;
}

void onMqttMessage(int messageSize) {
  if(mqttClient.messageTopic() == TOPIC_THRESHOLDS){
    // id t1 t2 t3 t4 t5 t6 t7 t8
    int id = mqtt_read_int();
    if(id != MQTT_ID){mqtt_clean();return;}
    for(int i = 0; i < 4; i++){
      t[i].low = mqtt_read_int();
      t[i].high = mqtt_read_int();
    }
    String res ="1 " + 
              t[1].toString() + " " + 
              t[3].toString() + " " + 
              t[0].toString() + " " + 
              t[2].toString();
    Serial.println(res);
    mqtt_clean();
  }
  else{
    //id action(str)
    int id = mqtt_read_int();
    if(id != MQTT_ID){mqtt_clean();return;}
    
    int c = mqtt_read_word();
    if (c != -1) {
      Serial.println("2 " + String(c));
    }
    mqtt_clean();
  }
}