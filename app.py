from flask import Flask, render_template, redirect, url_for
from db_handler import get_latest_data

app = Flask(__name__)

@app.route("/")
def index():
    data = get_latest_data()
    return render_template("index.html", data=data)

@app.route("/open")
def open_system():
    print("Systém otvorený.")
    return redirect(url_for("index"))

@app.route("/start")
def start_monitoring():
    print("Monitoring spustený.")
    return redirect(url_for("index"))

@app.route("/stop")
def stop_monitoring():
    print("Monitoring zastavený.")
    return redirect(url_for("index"))

@app.route("/close")
def close_system():
    print("Systém ukončený.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
