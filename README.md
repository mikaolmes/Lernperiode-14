# Lernperiode-14

Mika Olmes, Mateo Muic, Alexander Paucar, Robin Taing

In dieser Lernperiode werden wir ein fiktives Startup führen. Unsere Konkurrenten sind unsere Klassenkameraden.

<img height="200" alt="image" src="https://github.com/user-attachments/assets/aba0faad-29da-4d34-b701-444ea54c24a6" />

## 20.02.2026

Um es zum laufen zu bringen müssen Sie customkinter installieren

```pip install customtkinter```

Für die Kamera installieren sie opencv

```pip install customtkinter opencv-python pillow mediapipe```

## Finger Counting Feature

**Neu hinzugefügt**: Fingerzählung von 1-5!

- Starte `SignLanguage.py` und halte 1-5 Finger in die Kamera
- Die Anzahl wird live auf dem Bildschirm angezeigt
- Funktioniert mit mehreren Händen gleichzeitig

📄 Siehe [FINGER_COUNTING.md](FINGER_COUNTING.md) für Details und wie Teammitglieder es nutzen können!

## 27.02

## Arbeitspakete Mateo

- [x] MediaPipe für 21 Hand-Landmarks im Live-Video aufsetzen.
- [x] Finger-Counting Logik (1-5 Finger erkennen) implementieren.
- [ ] Koordinaten-Daten für die Gesten als CSV-Datei aufnehmen.
- [ ] Machine Learning Modell zur Gestenerkennung trainieren und speichern.
- [ ] Erkennungslogik in die Benutzeroberfläche der Desktop-App integrieren.


## Arbeitspakete Mika
- [ ] Startfenster mit Buttons erstellen um zwischen Morse Code und Sign Language auswählen zu können.
- [ ] Kamera input hinzufügen womit dann die Gebärdensprache aufgenommen wird (noch ohne aufnahme der Zeichen).
- [ ] Laoyut für Gebärdensprache erstellen, mit Output
- [ ] Layout für Eingabe und Ausgabe für Morse Code

## Arbeitspakete Robin
- [ ] morse code lösung -> licht
- [ ] morse code lösung -> ton
- [ ] implementierung übersetzer
- [ ] wöchentlicher Pitch/Bericht

## Arbeitspakete Alexander
- [ ] Mapping-Logik für Text-zu-Morse und Morse-zu-Text entwickeln.
- [ ] Logik zur Bereinigung von User-Inputs schreiben.
- [ ] Funktion implementieren, um übersetzte Texte mit Zeitstempel in einer `history.txt` zu speichern.
- [ ] Schnittstellen-Funktionen definieren, damit Mikas UI die Übersetzungs-Logik einfach aufrufen kann.
