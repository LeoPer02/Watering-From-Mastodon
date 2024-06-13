#define POTENTIOMETER_PIN A0
#define WATER_SENSOR_PIN A11 
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

  String toString(){
    String result = String(soil_moisture) + " " +
              String(temperature) + " " +
              String(light) + " " +
              String(humidity);
    return result;
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


};

Actuator yellow(33);
Actuator green(36);
Actuator blue(41);
Actuator red(44);

SensorData d(0,0,0,0);
Threshold t[] = {{150,450},{0,40},{250,450},{0,25}};


