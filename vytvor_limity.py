import mysql.connector

# Pripojenie k databáze
db = mysql.connector.connect(
    host="localhost",
    user="lenka",
    password="mojesilneheslo",
    database="poit_d1"
)
cursor = db.cursor()

# Vytvorenie tabuľky ak neexistuje
cursor.execute("""
    CREATE TABLE IF NOT EXISTS limity (
        id INT PRIMARY KEY,
        min_teplota FLOAT,
        min_vlhkost FLOAT
    )
""")

# Vloženie alebo aktualizácia počiatočných hodnôt
cursor.execute("""
    INSERT INTO limity (id, min_teplota, min_vlhkost)
    VALUES (1, 0, 0)
    ON DUPLICATE KEY UPDATE
        min_teplota = VALUES(min_teplota),
        min_vlhkost = VALUES(min_vlhkost)
""")

# Uloženie a zatvorenie spojenia
db.commit()
cursor.close()
db.close()

print("Tabuľka 'limity' vytvorená alebo aktualizovaná.")
