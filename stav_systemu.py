import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="lenka",
    password="mojesilneheslo",
    database="poit_d1"
)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stav_systemu (
        id INT PRIMARY KEY,
        monitoring BOOL DEFAULT FALSE
    )
""")

cursor.execute("SELECT COUNT(*) FROM stav_systemu WHERE id = 1")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO stav_systemu (id, monitoring) VALUES (1, FALSE)")

conn.commit()
cursor.close()
conn.close()
