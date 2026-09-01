# Copilot Instructions

## Python

- PEP8 strikt einhalten
- Black Formatter kompatibel
- Maximale Funktionslänge 50 Zeilen
- Maximale Dateigröße 500 Zeilen
- Docstrings für alle öffentlichen Funktionen
- Typannotationen verwenden

## Flask

- Blueprints verwenden
- SQL nicht in Route-Funktionen schreiben
- Services für Datenbankzugriffe nutzen
- API-Antworten immer als JSON

## Projektstruktur

- routes/ für Endpunkte
- services/ für Businesslogik
- database.py für Verbindungen
- config.py für Konfiguration
- models/ für Datenbankmodelle