# Interaktive QM-Übungen

Eine webbasierte Anwendung für interaktive Gruppenübungen im Qualitätsmanagement. Entwickelt mit Python und Streamlit; Supabase speichert Gruppen, Sitzungen und Versuchsergebnisse.

## Übungen

- **Farbmischung:** Zwei Farben auswählen und die Übereinstimmung der Mischfarbe mit einer Zielfarbe bewerten.
- **3D-Druckoptimierung:** Druckmaterial, Düsentemperatur, Druckgeschwindigkeit und Schichthöhe einstellen. Die Anwendung berechnet einen vereinfachten Qualitätswert, Warping, Layer Shifting und Schichtanzahl und visualisiert den Würfel in 3D.

Pro Gruppe sind **drei Versuche je Übung und Sitzung** möglich.

## Funktionen

- Anmeldung der Studierendengruppen mit individuellem Gruppencode
- Administrationsbereich zur Gruppen- und Übungsverwaltung
- Zeitbegrenzte Übungen und Vorbereitung neuer Sitzungen
- Vergleich der Gruppenergebnisse mit Rangliste, Diagramm und Versuchdetails
- Speicherung der Ergebnisse in Supabase; frühere Sitzungen bleiben erhalten

## Technologien

Python, Streamlit, Supabase, Plotly, Altair, Pandas und NumPy.

## Lokaler Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Für die Verbindung mit Supabase werden die benötigten Zugangsdaten lokal in `.streamlit/secrets.toml` hinterlegt. **Diese Datei darf nicht in Git veröffentlicht werden.**

## Bereitstellung

Die Veröffentlichung über GitHub und Streamlit Community Cloud ist vorgesehen. Nach dem Deployment sollen Studierende die Anwendung über einen Link bzw. QR-Code auf ihren eigenen Geräten öffnen können.

## Hinweis

Die 3D-Drucksimulation verwendet ein vereinfachtes Modell für Lehrzwecke und ist keine physikalisch genaue Prozesssimulation.
