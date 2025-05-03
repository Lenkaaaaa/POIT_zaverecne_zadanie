from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)

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
    return result[::-1]  # otočíme poradie z najstarších po najnovšie

@app.route("/")
def index():
    data = fetch_data()
    return render_template("index.html", data=data)

@app.route("/data")
def data():
    return jsonify(data=fetch_data())

if __name__ == "__main__":
    # Spúšťa Flask server na všetkých adresách (vrátane 192.168.x.x)
    app.run(debug=True, host="0.0.0.0", port=5000)
