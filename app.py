from flask import Flask
import mysql.connector

app = Flask(__name__)

@app.route("/")
def index():
    print("🔄 Pokus o pripojenie k databáze...")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="lenka",
            password="mojesilneheslo",
            database="poit_d1"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM monitorovanie")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ Úspešne načítané, počet záznamov: {count}")
        return f"Počet záznamov v tabuľke monitorovanie: {count}"
    except Exception as e:
        print(f"❌ Chyba: {e}")
        return "Chyba pri načítaní údajov."

if __name__ == "__main__":
    app.run(debug=True)
