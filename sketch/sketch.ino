#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 5        // D1 = GPIO 5
#define DHTTYPE DHT11   // DHT11 senzor

DHT_Unified dht(DHTPIN, DHTTYPE);

float lastTemp = -1000;
float lastHum = -1000;

void setup() {
  Serial.begin(9600);
  dht.begin();
  delay(2000); // Počkaj na stabilizáciu senzora
  Serial.println("Senzor pripravený.");
}

void loop() {
  sensors_event_t tempEvent, humEvent;
  dht.temperature().getEvent(&tempEvent);
  dht.humidity().getEvent(&humEvent);

  if (!isnan(tempEvent.temperature) && !isnan(humEvent.relative_humidity)) {
    float currentTemp = tempEvent.temperature;
    float currentHum = humEvent.relative_humidity;

    // Posielaj len ak sa hodnoty zmenili
    if (currentTemp != lastTemp || currentHum != lastHum) {
      Serial.print(currentTemp);
      Serial.print(",");
      Serial.println(currentHum);

      lastTemp = currentTemp;
      lastHum = currentHum;
    }
  }

  delay(2000);  // meraj každé 2 sekundy (DHT11 potrebuje čas)
}
