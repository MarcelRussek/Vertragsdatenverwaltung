import sqlite3

# Verbindung zur SQLite-Datenbank herstellen. Diese Anweisung erstellt die Datei, falls sie noch nicht existiert.
conn = sqlite3.connect('technische_daten.db')

# Erstellen eines Cursor-Objekts mittels der Verbindung
cursor = conn.cursor()

# SQL-Befehl zum Erstellen der Tabelle
cursor.execute('''
CREATE TABLE IF NOT EXISTS technische_daten (
`Company / Office` TEXT,
`Business Unit` TEXT,
`Line of Business` TEXT,
`Konzern Nummer` INTEGER,
`VN Nummer` INTEGER,
`Vertrag` INTEGER PRIMARY KEY,
`Tax/Commission Code - Label` TEXT,
`Advisor` TEXT,
`Account Handler` TEXT,
`Client Executive` TEXT,
`Expiry Date` TEXT,
`Leading Insurer` TEXT,
`EUR Net Premium Amount 2022` REAL,
`EUR Net Revenue 2022` REAL,
`EUR Net Premium Amount 2023` REAL,
`EUR Net Revenue 2023` REAL,
`Kunde` TEXT
);
''')
# Änderungen an der Datenbank bestätigen
conn.commit()

# Verbindung zur Datenbank schließen
conn.close()