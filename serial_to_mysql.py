import serial
import mysql.connector
import time

# Nastavenia sériového portu
SERIAL_PORT = "COM3"
BAUD_RATE = 9600

print("Citam data zo senzora...")

# Pripojenie na sériový port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Počkaj na Arduino reset

# Pripojenie do MySQL databázy
db = mysql.connector.connect(
    host="localhost",
    user="lenka",
    password="mojesilneheslo",
    database="poit_d1"
)
cursor = db.cursor()

try:
    while True:
        # Získaj aktuálne limity z tabuľky
        cursor.execute("SELECT min_teplota, min_vlhkost FROM limity WHERE id = 1")
        limit_row = cursor.fetchone()
        if limit_row:
            min_temp_limit, min_hum_limit = limit_row
        else:
            min_temp_limit, min_hum_limit = 0, 0  # predvolené hodnoty

        raw = ser.readline()
        print(f"RAW: {raw}")
        try:
            line = raw.decode('utf-8').strip()
            print(f"DECODED: {line}")

            if "," in line:
                temp_str, hum_str = line.split(",")
                temperature = float(temp_str)
                humidity = float(hum_str)
                print(f"Teplota: {temperature} °C | Vlhkosť: {humidity} %")

                # Zápis len ak sú hodnoty nad minimálnymi limitmi
                if temperature >= min_temp_limit and humidity >= min_hum_limit:
                    query = "INSERT INTO monitorovanie (teplota, vlhkost) VALUES (%s, %s)"
                    cursor.execute(query, (temperature, humidity))
                    db.commit()
                    print("Hodnoty uložené do databázy.")
                else:
                    print("Hodnoty pod limitom – nezapísané.")
            else:
                print("Nesprávny formát")

        except Exception as e:
            print(f"Chyba pri spracovaní: {e}")

        time.sleep(2)

except KeyboardInterrupt:
    print("Ukončené používateľom.")
    ser.close()
    cursor.close()
    db.close()
