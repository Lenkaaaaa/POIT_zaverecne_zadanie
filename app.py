import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
import mysql.connector
import csv, zipfile, io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tajnykluc'
socketio = SocketIO(app, async_mode="eventlet")

monitoring_active = False

limits = {
    "min_temp": 18,
    "max_temp": 30,
    "min_hum": 30,
    "max_hum": 60
}


@socketio.on("get_current_limits")
def get_current_limits():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT min_teplota, min_vlhkost FROM limity WHERE id = 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            socketio.emit("current_limits", {
                "min_temp": result[0],
                "min_hum": result[1]
            })
        else:
            socketio.emit("current_limits", {
                "min_temp": 0,
                "min_hum": 0
            })
    except Exception as e:
        print("Chyba pri načítaní limitov:", e)
        socketio.emit("current_limits", {
            "min_temp": 0,
            "min_hum": 0
        })


def get_latest_data(limit=1):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT teplota, vlhkost, cas FROM monitorovanie ORDER BY id DESC LIMIT %s", (limit,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        print("❌ Chyba DB:", e)
        return []


def background_thread():
    while True:
        if monitoring_active:
            latest = get_latest_data(limit=1)
            if latest:
                teplota, vlhkost, cas = latest[0]
                socketio.emit("new_data", {
                    "teplota": teplota,
                    "vlhkost": vlhkost,
                    "cas": str(cas)
                })

                # Kontrola limitov pre vizualizáciu
                if teplota < limits["min_temp"] or teplota > limits["max_temp"] or \
                   vlhkost < limits["min_hum"] or vlhkost > limits["max_hum"]:
                    socketio.emit("limit_status", {"message": "⚠️ Mimo rozsahu"})
                else:
                    socketio.emit("limit_status", {"message": "✅ V norme"})
        socketio.sleep(1)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def on_connect():
    print("✅ Klient pripojený")
    socketio.start_background_task(background_thread)


@socketio.on("open_system")
def open_system():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()

        # Vymaž staré dáta monitorovania
        cursor.execute("DELETE FROM monitorovanie")

        # Inicializuj systém
        cursor.execute("UPDATE stav_systemu SET aktivny = TRUE, monitoring = FALSE WHERE id = 1")
        conn.commit()

        cursor.close()
        conn.close()
        print("✅ Systém bol inicializovaný (aktivny = TRUE, monitoring = FALSE)")
        print("🧹 Dáta z predchádzajúceho monitorovania vymazané.")
    except Exception as e:
        print("❌ Chyba pri inicializácii systému:", e)

    emit("status_update", {"status": "🟢 Systém pripravený"}, broadcast=True)


@socketio.on("start_monitoring")
def start_monitoring():
    global monitoring_active
    monitoring_active = True

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()

        # Aktivuj monitoring
        cursor.execute("UPDATE stav_systemu SET monitoring = TRUE WHERE id = 1")
        conn.commit()
        cursor.close()
        conn.close()
        print("▶️ Monitoring bol spustený (stav a dáta v DB aktualizované)")
    except Exception as e:
        print("❌ Chyba pri štarte monitoringu:", e)

    emit("status_update", {"status": "▶️ Monitoring spustený"}, broadcast=True)


@socketio.on("stop_monitoring")
def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE stav_systemu SET monitoring = FALSE WHERE id = 1")
        conn.commit()
        cursor.close()
        conn.close()
        print("⏹️ Monitoring bol zastavený (stav uložený do DB)")
    except Exception as e:
        print("❌ Chyba pri zápise do stav_systemu:", e)

    emit("status_update", {"status": "⏸️ Monitoring pozastavený"}, broadcast=True)


@socketio.on("close_system")
def close_system():
    global monitoring_active
    monitoring_active = False
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE stav_systemu SET aktivny = FALSE, monitoring = FALSE WHERE id = 1")
        conn.commit()
        cursor.close()
        conn.close()
        print("🔌 Systém deaktivovaný (aktivny = FALSE, monitoring = FALSE)")
    except Exception as e:
        print("❌ Chyba pri zatváraní systému:", e)

    emit("status_update", {"status": "🔴 Systém zatvorený"}, broadcast=True)


@socketio.on("set_limits")
def set_limits(data):
    try:
        limits["min_temp"] = float(data.get("min_temp", 18))
        limits["max_temp"] = float(data.get("max_temp", 30))
        limits["min_hum"] = float(data.get("min_hum", 30))
        limits["max_hum"] = float(data.get("max_hum", 60))
        print("Limity nastavené:", limits)
    except Exception as e:
        print("Chyba pri nastavovaní limitov:", e)


@socketio.on("set_min_thresholds")
def set_min_thresholds(data):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE limity 
            SET min_teplota = %s, min_vlhkost = %s
            WHERE id = 1
        """, (data["min_temp"], data["min_hum"]))
        conn.commit()
        cursor.close()
        conn.close()
        emit("limit_status", {"message": "Minimálne limity uložené do databázy"})
    except Exception as e:
        emit("limit_status", {"message": "Chyba pri ukladaní min. limitov"})
        print(f"Chyba pri ukladaní min. limitov: {e}")

@app.route("/export-data")
def export_data():
    try:
        # Pripojenie k DB
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()

        # Získaj dáta z monitorovanie
        cursor.execute("SELECT teplota, vlhkost, cas FROM monitorovanie")
        monitor_data = cursor.fetchall()

        # Získaj dáta z limity
        cursor.execute("SELECT min_teplota, min_vlhkost FROM limity WHERE id = 1")
        limit_data = cursor.fetchone()

        # Zavri pripojenie
        cursor.close()
        conn.close()

        # CSV súbory do pamäte
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Monitorovanie
            monitor_csv = io.StringIO()
            writer = csv.writer(monitor_csv)
            writer.writerow(["Teplota", "Vlhkost", "Cas"])
            writer.writerows(monitor_data)
            zf.writestr("monitorovanie.csv", monitor_csv.getvalue())

            # Limity
            if limit_data:
                limit_csv = io.StringIO()
                writer = csv.writer(limit_csv)
                writer.writerow(["Min_teplota", "Min_vlhkost"])
                writer.writerow(limit_data)
                zf.writestr("limity.csv", limit_csv.getvalue())

        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name="export_senzorovych_dat.zip"
        )
    except Exception as e:
        print("❌ Chyba pri exporte:", e)
        return "Chyba pri exporte", 500


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
