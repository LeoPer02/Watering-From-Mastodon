#include <ArduinoMqttClient.h>
#include <WiFi101.h>

#define POTENTIOMETER_PIN A0
#define TEMPERATURE_PIN A1
#define LIGHT_SENSOR_PIN A15

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

class Treshold{
    public:
    int high;
    int low;

    Treshold(int l, int h){
        high = h;
        low = l;
    }
};

Actuator blue(5);
Actuator yellow(2);
Actuator green(6);

Treshold light(100,300);

void setup() {
    //actuators
    blue.setup();
    yellow.setup();

    //sensors
    pinMode(LIGHT_SENSOR_PIN, INPUT);

    //set serial port for communication
    Serial.begin(9600);
}

void loop() {
    int light_value = analogRead(LIGHT_SENSOR_PIN);
    Serial.println(light_value);
    if(light_value > light.high) {
        blue.activate();
    }
    else if(light_value < light.low) {
      yellow.activate();
    }

    delay(100);
}
