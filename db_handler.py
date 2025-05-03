import mysql.connector

def get_latest_data(limit=10):
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="lenka",
            password="mojesilneheslo",  # zmeň na svoje skutočné heslo
            database="poit_d1"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT teplota, vlhkost FROM Monitorovanie ORDER BY id DESC LIMIT %s", (limit,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        print("Chyba pri načítaní z databázy:", e)
        return []
