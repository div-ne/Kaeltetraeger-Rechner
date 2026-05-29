# Kälteträger Rechner

[**Zur Live-Anwendung**](https://kaeltetraeger.streamlit.app/)

## Funktionen

- Umrechnung von **Kälteträger 1** auf **Kälteträger 2**
- Auswahl der Berechnungsbasis über **Volumenstrom** oder **übertragene Leistung**
- Berücksichtigung von **Druckverlust**, **mittlerer Temperatur**, **Temperaturdifferenz**, **Rohrinnendurchmesser** und **Rohrrauheit**
- Berechnung relevanter hydraulischer Größen wie **Volumenstrom**, **Strömungsgeschwindigkeit** und **Druckverlust**
- Berechnung thermodynamischer Eigenschaften wie **Dichte**, **spezifische Wärmekapazität** und **Gefrierpunkt**
- Ausgabe der Ergebnisse in einer übersichtlichen Tabelle
- Export der Ergebnisse als **CSV-Datei**
- Zusätzliche Hilfebereiche für **Anleitung**, **Rohrrauheitswerte** und **Grenzen der Kälteträger**

## Einsatzbereich

Das Tool richtet sich an Anwenderinnen und Anwender aus den Bereichen:

- Kälte- und Klimatechnik
- TGA und Gebäudetechnik
- Energie- und Versorgungstechnik
- Planung, Auslegung und Vergleich von Kälteträgerkreisläufen

Ein typischer Anwendungsfall ist die Abschätzung, wie sich ein Wechsel von Wasser auf einen anderen Kälteträger auf hydraulische und thermodynamische Kennwerte auswirkt.

## So funktioniert die Berechnung

Für die Berechnung wird zunächst **Kälteträger 1** mit seiner Konzentration definiert. Anschließend wird festgelegt, ob die Rechnung auf dem **Volumenstrom** oder auf der **übertragenen Leistung** basiert. Danach werden der **Druckverlust mit Kälteträger 1** sowie die allgemeinen Randbedingungen wie mittlere Temperatur, Temperaturdifferenz, Rohrinnendurchmesser und Rohrrauheit eingegeben. Abschließend wird **Kälteträger 2** mit seiner Konzentration ausgewählt, um die entsprechenden Zielwerte zu berechnen.

Ein besonderer Nutzen des Rechners liegt darin, dass nicht nur hydraulische Auswirkungen des Medienwechsels sichtbar werden, sondern auch thermodynamische Eigenschaften direkt berechnet und verglichen werden. Dazu zählen insbesondere **Dichte**, **spezifische Wärmekapazität** und **Gefrierpunkt**.

Die Eingaben für **mittlere Temperatur** und **Temperaturdifferenz** eignen sich beispielsweise zur Abbildung eines Vorlauf-/Rücklauf-Szenarios eines Kühlgeräts oder eines vergleichbaren hydraulischen Systems.

## Unterstützte Medien

Aktuell sind in der Anwendung folgende Medien hinterlegt:

- Wasser
- Antifrogen N
- Antifrogen L
- Kaliumformiat

## Konzentrationsgrenzen

Für die Eingabe in diesem Tool gelten aktuell folgende Konzentrationsbereiche:

| Kälteträger | Mögliche Konzentration |
|---|---|
| Wasser | 100 % |
| Antifrogen N | 10 bis 60 % |
| Antifrogen L | 10 bis 60 % |
| Kaliumformiat | 40 bis 100 % |

## Technologie

Dieses Projekt basiert auf:

- **Python**
- **Streamlit** für die Weboberfläche
- **CoolProp** zur Berechnung thermophysikalischer Stoffwerte
- **NumPy** und **Pandas** für numerische Verarbeitung und Ergebnisdarstellung

## Projektziel

Ziel des Projekts ist ein leicht zugängliches, browserbasiertes Fachtool für den schnellen Vergleich von Kälteträgern in praxisnahen Anwendungsfällen. Im Vordergrund stehen eine einfache Bedienung, nachvollziehbare Eingaben und eine schnelle Verfügbarkeit ohne klassische Desktop-Installation.
