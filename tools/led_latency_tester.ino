/*
 * led_latency_tester.ino
 * 
 * Doel: LED aan/uit sturen voor video-latency tests.
 * Commands via Serial (115200 bps):
 *  '1' -> LED aan
 *  '0' -> LED uit
 *  'B' -> Begin knipperen (500 ms aan/uit)
 *  'S' -> Stop knipperen
 *
 * ESP32-C3: vaak is GPIO2 de onboard LED. Pas LED_PIN aan indien nodig.
 */
#define LED_PIN 8

bool blinkMode = false;
unsigned long lastToggle = 0;
const unsigned long blinkInterval = 500; // ms

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); // active-low: default OFF
  Serial.begin(115200);
  while (!Serial) { ; } // wacht tot USB-serial actief is
  Serial.println("LED Latency Tester ready");
}

void loop() {
  // Serial commando's verwerken
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      digitalWrite(LED_PIN, HIGH); // active-low: OFF
      blinkMode = false;
      Serial.println("LED ON");
    } else if (cmd == '0') {
      digitalWrite(LED_PIN, LOW);  // active-low: ON
      blinkMode = false;
      Serial.println("LED OFF");
    } else if (cmd == 'B') {
      blinkMode = true;
      lastToggle = millis();
      Serial.println("BLINK START");
    } else if (cmd == 'S') {
      blinkMode = false;
      Serial.println("BLINK STOP");
    }
  }

  // Knippermodus
  if (blinkMode) {
    unsigned long now = millis();
    if (now - lastToggle >= blinkInterval) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      lastToggle = now;
    }
  }
}