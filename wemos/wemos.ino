#include <ArduinoMqttClient.h>
#include <ESP8266WiFi.h>

#define BUF_SIZE 50

char ssid[] = "";        // your network SSID (name)
char pass[] = "";    // your network password (use for WPA, or use as key for WEP)

class SensorData {
  public:
  int light;
  int soil_moisture;
  int humidity;
  int temperature;

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

  void toSerial(){
    Serial.print(this->light);
    Serial.write(",");
    Serial.print(this->soil_moisture);
    Serial.write(",");
    Serial.print(this->humidity);
    Serial.write(",");
    Serial.print(this->temperature);
    Serial.println();
  }
};

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = "test.mosquitto.org";
int        port     = 1883;
const char pool[]  = "arduino/pool";
const char commands[]  = "arduino/commands";
char buf[BUF_SIZE];

//set interval for sending messages (milliseconds)
const long interval = 100;
unsigned long previousMillis = 0;

int count = 0;

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  while (!Serial1) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // attempt to connect to Wifi network:
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  //while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    // failed, retry
  //  Serial.print(".");
  //  delay(5000);
  //}

  Serial.println("You're connected to the network");
  Serial.println();

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  //if (!mqttClient.connect(broker, port)) {
  //  Serial.print("MQTT connection failed! Error code = ");
  //  Serial.println(mqttClient.connectError());

//    while (1);
  //}

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
}

bool read_from_serial(SensorData &d) {
  char ch;
  int nums[4] = {0,0,0,0};
  int numIndex = 0;
  int sign = 1; // To handle negative numbers
  bool read = false;

  if (Serial.available()) {
    read = true;
    delay(100); //allows all serial sent to be received together
    while(Serial.available()) {
      char ch = Serial.read();
      if (ch == '-') {
          sign = -1;
      } else if (isdigit(ch)) {
          nums[numIndex] = nums[numIndex] * 10 + (ch - '0');
      } else if (ch == ',') {
          nums[numIndex] *= sign;
          numIndex++;
          sign = 1; // Reset sign for the next number
      }
    }
    d.light = nums[0];
    d.soil_moisture = nums[1];
    d.humidity = nums[2];
    d.temperature = nums[3];
    Serial.write("VALUE READ IN WESMOS\n");
    d.toSerial();
    return true;
  }
  return false;
}

void loop() {
  // call poll() regularly to allow the library to send MQTT keep alives which
  // avoids being disconnected by the broker
  //mqttClient.poll();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time a message was sent
    previousMillis = currentMillis;

  SensorData d (0,0,0,0);
  bool r = read_from_serial(d);
    // send message, the Print interface can be used to set the message contents
    //mqttClient.beginMessage(pool);
    //mqttClient.print(read);
    //mqttClient.endMessage();
  }
}