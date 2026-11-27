# Interaktive QM-Übungen

Eine webbasierte Anwendung für interaktive Gruppenübungen im Qualitätsmanagement. Entwickelt mit Python und Streamlit; Supabase speichert Gruppen, Sitzungen und Versuchsergebnisse.

## Übungen

- **Farbmischung:** Zwei Farben auswählen und die Übereinstimmung der Mischfarbe mit einer Zielfarbe bewerten.
- **3D-Druckoptimierung:** Druckmaterial, Düsentemperatur, Druckgeschwindigkeit und Schichthöhe einstellen. Die Anwendung berechnet einen vereinfachten Qualitätswert, Warping, Layer Shifting und Schichtanzahl und visualisiert den Würfel in 3D.

Jede Übung besteht aus zwei Runden mit jeweils 10 Minuten. Pro Gruppe sind **drei Versuche je Runde** möglich. Bei der Farbmischung werden in der zweiten Runde zusätzlich die RGB-Werte der Zielfarbe angezeigt.

## Funktionen

- Anmeldung der Studierendengruppen mit individuellem Gruppencode
- Administrationsbereich zur Gruppen- und Übungsverwaltung
- Steuerung beider Runden und Vorbereitung neuer Sitzungen
- Vergleich der besten Gruppenergebnisse beider Runden mit Diagrammen, Differenzen in Prozentpunkten und Versuchsdetails
- Speicherung der Ergebnisse in Supabase; frühere Sitzungen bleiben erhalten

## Technologien

Python, Streamlit, Supabase, Plotly,  Pandas und NumPy.

## Lokaler Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Für die Verbindung mit Supabase werden die benötigten Zugangsdaten lokal in `.streamlit/secrets.toml` hinterlegt. **Diese Datei darf nicht in Git veröffentlicht werden.**

## Bereitstellung

Die Anwendung wird über GitHub und Streamlit Community Cloud bereitgestellt. Studierende können sie über einen Link bzw. QR-Code auf ihren eigenen Geräten öffnen.

[Anwendung öffnen](https://interactive-qm-exercises.streamlit.app/)

## Hinweis

Die 3D-Drucksimulation verwendet ein vereinfachtes Modell für Lehrzwecke und ist keine physikalisch genaue Prozesssimulation.