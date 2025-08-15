/*
 * ESP32-C3 Serial Echo
 * Werkt met serial_ping.py voor latency-metingen.
 *
 * Sluit de ESP32-C3 via USB aan, zet dezelfde baudrate als in serial_ping.py
 * (standaard 1.000.000 baud).
 */

void setup() {
  Serial.begin(1000000);   // Zet hier de baudrate gelijk aan je meetscript
  while (!Serial) {
    ; // Wacht tot USB-serial actief is
  }
}

void loop() {
  // Als er data beschikbaar is, lees alles en stuur exact terug
  while (Serial.available() > 0) {
    uint8_t b = Serial.read();
    Serial.write(b);
  }
}
