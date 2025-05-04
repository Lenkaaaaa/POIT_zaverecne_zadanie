from flask import Flask, render_template, jsonify, redirect, url_for
import mysql.connector
import threading
import serial
import time

app = Flask(__name__)

SERIAL_PORT = "COM3"
BAUD_RATE = 9600
serial_thread = None
stop_thread = threading.Event()
serial_conn = None

def fetch_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="lenka",
        password="mojesilneheslo",
        database="poit_d1"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT teplota, vlhkost, cas FROM monitorovanie ORDER BY id DESC LIMIT 20")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def read_serial():
    global serial_conn
    try:
        serial_conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
    except Exception as e:
        print(f"Chyba pri otváraní portu: {e}")
        return

    db = mysql.connector.connect(
        host="localhost",
        user="lenka",
        password="mojesilneheslo",
        database="poit_d1"
    )
    cursor = db.cursor()

    print("Senzor pripravený. Čítam dáta...")

    while not stop_thread.is_set():
        raw = serial_conn.readline()
        try:
            line = raw.decode('utf-8').strip()
            if "," in line:
                temp, hum = map(float, line.split(","))
                print(f"Teplota: {temp}, Vlhkosť: {hum}")
                cursor.execute("INSERT INTO monitorovanie (teplota, vlhkost) VALUES (%s, %s)", (temp, hum))
                db.commit()
            else:
                print("Neplatný formát")
        except Exception as e:
            print(f"Chyba pri spracovaní: {e}")
        time.sleep(2)

    serial_conn.close()
    cursor.close()
    db.close()
    print("Čítanie zastavené.")

@app.route("/")
def index():
    data = fetch_data()
    return render_template("index.html", data=data)

@app.route("/data")
def data():
    return jsonify(data=fetch_data())

@app.route("/open")
def open_system():
    print("Systém inicializovaný (Open).")
    return redirect(url_for("index"))

@app.route("/start")
def start_system():
    global serial_thread, stop_thread

    if serial_thread and serial_thread.is_alive():
        print("Monitoring už beží.")
    else:
        print("▶Spúšťam monitoring...")
        stop_thread.clear()
        serial_thread = threading.Thread(target=read_serial)
        serial_thread.start()

    return redirect(url_for("index"))

@app.route("/stop")
def stop_system():
    global stop_thread

    if serial_thread and serial_thread.is_alive():
        stop_thread.set()
        print("⏸ Monitoring pozastavený.")
    else:
        print("Nie je čo zastaviť.")
    return redirect(url_for("index"))

@app.route("/close")
def close_system():
    global stop_thread

    if serial_thread and serial_thread.is_alive():
        stop_thread.set()
        print("Monitoring ukončený.")
    else:
        print("Nie je aktívny monitoring.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")
