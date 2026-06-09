# Kälteträger Rechner

[**Zur Anwendung**](https://kaeltetraeger.streamlit.app/)

## Funktionen

- Umrechnung von Kälteträger 1 auf Kälteträger 2.
- Berechnung relevanter hydraulischer Größen wie Volumenstrom, Strömungsgeschwindigkeit und Druckverlust.
- Berechnung thermodynamischer Eigenschaften wie Dichte, spezifische Wärmekapazität und Gefrierpunkt.
- Export der Ergebnisse als CSV-Datei.

## Eingabeparameter

Die Berechnung wird mit folgenden Eingaben durchgeführt:

- Projektname
- Fluid 1 & Konzentration
- Basis der Berechnung, Volumenstrom Fluid 1 oder Übertragene Leistung
- Druckverlust Fluid 1
- Mittlere Temperatur, analog zu einer Vor- und Rücklauftemperatur
- Temperaturdifferenz
- Rohrinnendurchmesser
- Rohrrauheit
- Fluid 2 & Konzentration

## Unterstützte Medien

Aktuell sind in der Anwendung folgende Medien hinterlegt:

- Wasser
- Antifrogen N
- Antifrogen L
- Kaliumformiat

## Rohrrauheitswerte & Konzentrationsgrenzen

Die App enthält jeweils Werte für Rohrrauheitswerte verschiedener Rohre und die Konzentrationsgrenzen für die verfügbaren Kälteträger.

## Technologie

Die Anwendung basiert auf Streamlit für die Oberfläche, CoolProp für Stoffdaten und thermodynamische Zustandsgrößen und NumPy sowie Pandas für Berechnung und Datenaufbereitung.