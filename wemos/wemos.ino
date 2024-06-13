#include <ArduinoMqttClient.h>
#include <ESP8266WiFi.h>

#define BUF_SIZE 50

#define MQTT_ID   1

#define TOPIC_ACTIONS   "actions"
#define TOPIC_POOL      "pool"
#define TOPIC_COMMANDS  "commands"
#define TOPIC_THRESHOLDS "thresholds"

class SensorData {
  public:
  int light;
  int soil_moisture;
  int humidity;
  int temperature;
  char s[64];


  SensorData(){
    light = 0;
    soil_moisture = 0;
    humidity = 0;
    temperature = 0;
  }
  SensorData(int l,int sm, int h, int t){
    light = l;
    soil_moisture = sm;
    humidity = h;
    temperature = t;
  }

  char* toString( ){
    snprintf(s, sizeof(s), "%d*%d*%d*%d", this->light, this->soil_moisture, this->humidity, this->temperature);
    return s;
  }
};

class Threshold {
  public:
  int high;
  int low;

  Threshold(){
    high = 0;
    low = 0;
  }
  Threshold(int l, int h) {
    high = h;
    low = l;
   }

  String toString(){
    String res =  String(low) + " " + String(high);
    return res;
  }
};

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

Threshold t[] = {{100,200},{100,200},{},{}};


char buf[BUF_SIZE];


