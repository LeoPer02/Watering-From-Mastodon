#define POTENTIOMETER_PIN A0
#define TEMPERATURE_PIN A1 
#define LIGHT_SENSOR_PIN A14

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

  void toSerial(HardwareSerial S){
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
class Actuator {
    int pin;

    public:
    Actuator(int p){
        pin = p;
    }

    void setup(){
        pinMode(pin,OUTPUT);
    }
    bool activate(){
        digitalWrite(pin, HIGH);
        delay(1000);
        digitalWrite(pin,LOW);
        return true;
    }
};

Actuator blue(35);
Actuator yellow(31);
Actuator green(39);
SensorData d(0,0,0,0);

void setup() {
    //actuators
    blue.setup();
    yellow.setup();

    //sensors
    pinMode(LIGHT_SENSOR_PIN, INPUT);

    //set serial port for communication
    Serial.begin(9600);
    //Serial3.begin(9600);
}

int light(int high, int low){
  int light_value = analogRead(LIGHT_SENSOR_PIN);
  if(light_value > high) {
      blue.activate();
  }
  else if(light_value < low) {
    yellow.activate();
  }
  return light_value;
}

void loop() {
  d.light         = light(400,200);
  d.soil_moisture = 0;
  d.humidity      = 0;
  d.temperature   = 0;
  d.toSerial(Serial);
  //d.toSerial(Serial3);  
  delay(100);
}
