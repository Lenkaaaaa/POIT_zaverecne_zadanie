import serial
import mysql.connector
import time

# Nastavenie COM portu a rýchlosti
ser = serial.Serial('COM3', 9600, timeout=1)

# Pripojenie k databáze
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="lenka",
    password="mojesilneheslo",
    database="poit_d1"
)

cursor = conn.cursor()

print("Citam data zo senzora...")

while True:
    line = ser.readline().decode('utf-8').strip()
    if "Teplota" in line and "Vlhkost" in line:
        try:
            parts = line.split('|')
            temp = float(parts[0].split(':')[1].strip())
            hum = float(parts[1].split(':')[1].replace('%', '').strip())

            print(f"Teplota: {temp} °C, Vlhkost: {hum} %")

            cursor.execute("INSERT INTO Monitorovanie (teplota, vlhkost) VALUES (%s, %s)", (temp, hum))
            conn.commit()
        except Exception as e:
            print("Chyba pri spracovani:", e)

    time.sleep(1)
