#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 5        // D1 = GPIO 5
#define DHTTYPE DHT11   // Používame DHT11

DHT_Unified dht(DHTPIN, DHTTYPE);
uint32_t delayMS;

void setup() {
  Serial.begin(9600);
//  while (!Serial) ;  // počkaj na pripojenie
  Serial.println("Sketch sa spustil!");
  dht.begin();

  Serial.println("Inicializácia senzora...");


  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  //delayMS = sensor.min_delay / 1000;  // oneskorenie medzi meraniami
}

void loop() {
  delay(1000);

  sensors_event_t tempEvent, humEvent;

  dht.temperature().getEvent(&tempEvent);
  dht.humidity().getEvent(&humEvent);

  if (isnan(tempEvent.temperature)) {
    Serial.println("❌ Nepodarilo sa získať teplotu");
  }
  if (isnan(humEvent.relative_humidity)) {
    Serial.println("❌ Nepodarilo sa získať vlhkosť");
  }

  if (!isnan(tempEvent.temperature) && !isnan(humEvent.relative_humidity)) {
    Serial.print(tempEvent.temperature);
    Serial.print(",");
    Serial.println(humEvent.relative_humidity);
  }

 Serial.println("Meranie prebehlo...");
}


