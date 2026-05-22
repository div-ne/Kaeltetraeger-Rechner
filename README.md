# Kälteträger-Rechner

[**Zur Live-Anwendung**](https://kaeltetraeger.streamlit.app/)

Ein webbasiertes Berechnungstool zur Umrechnung thermohydraulischer Kennwerte von einem Kälteträger auf einen anderen. Die Anwendung unterstützt typische Engineering-Anwendungsfälle in der Kälte-, Klima- und Energietechnik und hilft dabei, Auswirkungen eines Medienwechsels auf Volumenstrom, Druckverlust, Strömungsgeschwindigkeit und weitere Stoffwerte schnell abzuschätzen.

## Funktionen

- Umrechnung von **Kälteträger 1** auf **Kälteträger 2**
- Auswahl der Berechnungsbasis über **Volumenstrom** oder **übertragene Leistung**
- Berücksichtigung von **Druckverlust**, **mittlerer Temperatur**, **Temperaturdifferenz**, **Rohrinnendurchmesser** und **Rohrrauheit**
- Berechnung relevanter thermophysikalischer Kennwerte mit **CoolProp**
- Ausgabe der Ergebnisse in einer übersichtlichen Tabelle
- Export der Ergebnisse als **CSV-Datei**
- Zusätzliche Hilfebereiche für **Anleitung** und **Rohrrauheitswerte**

## Einsatzbereich

Das Tool richtet sich an Anwenderinnen und Anwender aus den Bereichen:

- Kälte- und Klimatechnik
- TGA und Gebäudetechnik
- Energie- und Versorgungstechnik
- Planung, Auslegung und Vergleich von Kälteträgerkreisläufen

Ein typischer Anwendungsfall ist die Abschätzung, wie sich der Einsatz von Antifrogen N in einer Kälteanlage auswirkt, die für Wasser ausgelegt und spezifiziert wurde.

## So funktioniert die Berechnung

Für die Berechnung wird zunächst **Kälteträger 1** mit seiner Konzentration definiert. Anschließend wird festgelegt, ob die Rechnung auf dem **Volumenstrom** oder auf der **übertragenen Leistung** basiert. Danach werden der **Druckverlust mit Kälteträger 1** sowie die allgemeinen Randbedingungen wie mittlere Temperatur, Temperaturdifferenz, Rohrinnendurchmesser und Rohrrauheit eingegeben. Abschließend wird **Kälteträger 2** mit seiner Konzentration ausgewählt, um die entsprechenden Zielwerte zu berechnen.

Die Eingaben für **mittlere Temperatur** und **Temperaturdifferenz** eignen sich beispielsweise zur Abbildung eines Vorlauf-/Rücklauf-Szenarios eines Kühlgeräts oder eines vergleichbaren hydraulischen Systems.

## Unterstützte Medien

Aktuell sind in der Anwendung folgende Medien hinterlegt:

- Wasser
- Antifrogen N
- Antifrogen L
- Kaliumformiat

## Technologie

Dieses Projekt basiert auf:

- **Python**
- **Streamlit** für die Weboberfläche
- **CoolProp** zur Berechnung thermophysikalischer Stoffwerte
- **NumPy** und **Pandas** für numerische Verarbeitung und Ergebnisdarstellung
