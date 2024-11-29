#include "HX711.h"

const int DOUT_PIN = 2;
const int SCK_PIN = 3;

HX711 scale;
float calibration_factor = -2267.1892;  // Use the value you got from calibration

void setup() {
  Serial.begin(57600);
  scale.begin(DOUT_PIN, SCK_PIN);
  scale.set_scale(calibration_factor);
  scale.tare();
}

void loop() {
  if (scale.is_ready()) {
    float weight = scale.get_units(5);
    Serial.print("W:");  // Prefix for weight data
    Serial.println(weight, 1);
  }
  delay(200);
}