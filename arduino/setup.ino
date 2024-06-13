void setup() {
    //actuators
    blue.setup();
    yellow.setup();
    red.setup();
    green.setup();

    //sensors
    pinMode(LIGHT_SENSOR_PIN, INPUT);
    pinMode(WATER_SENSOR_PIN, INPUT);

    //set serial port for communication
    Serial.begin(9600);
}
