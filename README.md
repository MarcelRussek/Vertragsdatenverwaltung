# Web-Anwendung zur Kunden- und Vertragsdatenverwaltung

## Beschreibung

Dieses Projekt umfasst eine Web-Anwendung, die für die Verwaltung von Kunden- und Vertragsdaten innerhalb einer Versicherungs- oder Finanzorganisation entwickelt wurde. Es ermöglicht Benutzern, Vertragsdaten zu aktualisieren, Risikoinformationen zu verwalten, Angebote und Erneuerungen zu bearbeiten, sowie verschiedene Berichte und Analysen über die Benutzeroberfläche zu generieren.

## Features

- Vertragsdatenaktualisierung
- Risikomanagement und -überwachung
- Ausschreibungsmanagement
- Renewal-Management und Ergebnisverfolgung
- Automatisierte Abarbeitung von Renewals
- Kommentar- und Notizfunktion zu Verträgen
- Datenbankgestützte Speicherung und Abfrage

## Technologien

- **Frontend:** Streamlit
- **Backend:** Python, SQLite
- **Libraries:** Pandas, PIL, sqlite3

## Installation und lokale Einrichtung

1. Klonen Sie das Repository:
   ```bash
   git clone https://github.com/IhrUsername/kunden-vertragsverwaltung.git
2. Wechseln Sie in das Projektverzeichnis:
   ```bash
   cd kunden-vertragsverwaltung
3. Installieren Sie die benötigten Pakete:
   ```bash
   pip install -r requirements.txt
4. Starten Sie die Anwendung:
   ```bash
   streamlit run app.py

   
## Einrichtung der Datenbanken
Bevor Sie die Anwendung starten, stellen Sie sicher, dass die benötigten Datenbanken eingerichtet sind.

1. Manuelle Datenbank (manuelle_daten.db):
   ```bash
   python manuelle_daten_db_erstellen.py
2. Technische Datenbank (technische_daten.db):
   ```bash
   python technische_daten_db_erstellen.py


## Benutzung
Nach dem Start der Anwendung können Sie über Ihren Webbrowser auf die Benutzeroberfläche zugreifen, die üblicherweise unter http://localhost:8501 erreichbar ist. Über die Seitenleiste können Sie verschiedene Module der Anwendung aufrufen und nutzen.

## Beitrag
Pull Requests sind willkommen. Für größere Änderungen, bitte zuerst ein Issue eröffnen, um die Änderung zu diskutieren.

Bitte führen Sie Tests durch, um sicherzustellen, dass keine Regressionen durch Ihre Änderungen entstehen.


