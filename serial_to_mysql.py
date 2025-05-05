import serial 
import mysql.connector
import time

# Nastavenia sériového portu
SERIAL_PORT = "COM3"
BAUD_RATE = 9600

print("📡 Čítam dáta zo senzora...")

# Pripojenie na sériový port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Počkaj na Arduino reset

try:
    while True:
        # ⬇ Znovu sa pripoj na DB v každom cykle
        db = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = db.cursor()

        # Zisti, či je systém aktívny a monitoring zapnutý
        cursor.execute("SELECT aktivny, monitoring FROM stav_systemu WHERE id = 1")
        result = cursor.fetchone()
        aktivny, monitoring_enabled = result if result else (False, False)

        if not aktivny:
            print("🔌 Systém nie je aktívny – dáta sa neukladajú.")
            cursor.close()
            db.close()
            time.sleep(2)
            continue

        if not monitoring_enabled:
            print("⏸️ Monitoring je pozastavený – dáta sa neukladajú.")
            cursor.close()
            db.close()
            time.sleep(2)
            continue

        # Získaj aktuálne limity z tabuľky
        cursor.execute("""
            SELECT min_teplota, min_vlhkost
            FROM limity
            ORDER BY cas DESC
            LIMIT 1
        """)

        limit_row = cursor.fetchone()
        min_temp_limit, min_hum_limit = limit_row if limit_row else (0, 0)

        raw = ser.readline()
        print(f"RAW: {raw}")
        try:
            line = raw.decode('utf-8').strip()
            print(f"DECODED: {line}")

            if "," in line:
                temp_str, hum_str = line.split(",")
                temperature = float(temp_str)
                humidity = float(hum_str)
                print(f"🌡️ Teplota: {temperature} °C | 💧 Vlhkosť: {humidity} %")

                if temperature >= min_temp_limit and humidity >= min_hum_limit:
                    cursor.execute("INSERT INTO monitorovanie (teplota, vlhkost) VALUES (%s, %s)", (temperature, humidity))
                    db.commit()
                    print("✅ Hodnoty uložené do databázy.")
                else:
                    print("⚠️ Hodnoty pod limitom – nezapísané.")
            else:
                print("⚠️ Nesprávny formát")

        except Exception as e:
            print(f"❌ Chyba pri spracovaní: {e}")

        cursor.close()
        db.close()
        time.sleep(2)

except KeyboardInterrupt:
    print("🛑 Ukončené používateľom.")
    ser.close()
