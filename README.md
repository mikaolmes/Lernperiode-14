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


# 27.02.2026
## Mateo

- [x] MediaPipe für 21 Hand-Landmarks im Live-Video aufsetzen.
- [x] Finger-Counting Logik (1-5 Finger erkennen) implementieren.
- [ ] Koordinaten-Daten für die Gesten als CSV-Datei aufnehmen.
- [ ] Machine Learning Modell zur Gestenerkennung trainieren und speichern.
- [ ] Erkennungslogik in die Benutzeroberfläche der Desktop-App integrieren.

## Zusammenfassung
Heute habe ich die MediaPipe Handerkennung Implementiert und eine Fingerzählung 1 bis 5 pro hand. 

## Mika
- [X] Startfenster mit Buttons erstellen um zwischen Morse Code und Sign Language auswählen zu können.
- [X] Kamera input hinzufügen womit dann die Gebärdensprache aufgenommen wird (noch ohne aufnahme der Zeichen).
- [ ] Laoyut für Gebärdensprache erstellen, mit Output
- [ ] Layout für Eingabe und Ausgabe für Morse Code

## Zusammenfassung
Heute habe ich eine kleine Home Page erstellt, die einen auswählen lässt zwischen Gebärdensprache und Morsecode translation auswählen lässt. Dazu musste ich zusammen mit Mateo einen kleinen Conflict lösen, denn wir haben uns gegenseitig die Namen der Variabeln und Funktionen verändert, schlussendlich haben wir es lösen können und der Code funktioniert.

## Robin
- [ ] morse code lösung -> licht
- [ ] morse code lösung -> ton
- [ ] implementierung übersetzer
- [ ] wöchentlicher Pitch/Bericht

## Alexander
- [X] Mapping-Logik für Text-zu-Morse und Morse-zu-Text entwickeln.
- [ ] Logik zur Bereinigung von User-Inputs schreiben.
- [ ] Funktion implementieren, um übersetzte Texte mit Zeitstempel in einer `history.txt` zu speichern.
- [X] Schnittstellen-Funktionen definieren, damit Mikas UI die Übersetzungs-Logik einfach aufrufen kann.

# 06.03.2026

## Mateo
- [x] Implementierung sign language alphabet recognition (funktioniert so halb. Nicht alles wird erkannt)
- [x] UI änderungen für SignLanguage.py
- [ ] andere sachen keine ahnung noch

## Mika
- [X] Layout für Gebärdensprache erstellen, mit Output
- [X] Layout für Morse Code, mit Input
- [X] HomePage dynamisch anpassbar machen.
- [X] Globales "umstyling" z.b. Farben ändern.

## Zusammenfassung
Heute habe ich zuerst die Homepage dynamisch angepasst, sodass es besser aussieht wenn man das Fenster kleiner bzw. grösser macht. Danach habe ich Input für morsecode und output für die Signlanguage erstellt. Bei der Signlanguage werden auch schon Buchstaben ausgegeben. Zuletzt habe ich noch ein kleines Umstyling vorgenommen. Ich habe die Farben von Blau auf ein Grün gewechselt.


## Robin

## Alexander

# 20.03.2026

## Mateo

- [ ] Implementierung Tracking Absolute Cinema
- [ ] Implementierung middle finger (gorilla)
- [ ] Implementierung bewegungs dings für 67 meme (wenn genug zeit) 

## Mika
- [ ] Logik: Download funktion hinzufügen, sodass man eine .txt Datei mit den Übersetzungen herunterlädt.
- [X] UI: Einbindung einer "Progress-Bar" für die drei Sekunden, damit man sieht wie schnell das funktioniert. Dazu einen "Fast-Mode"
- [X] Hotkeys: Bindung von Tasten (z. B. ESC für Zurück, SPACE für Start/Stop Kamera), damit man die Maus weniger nutzen muss.
- [X] Präsentation vorbereiten


## Robin
Umgehung Fehler -> started nicht in ios Expo app (Time out).
- [x] Neuinstallierung Expo und Versionskontrolle
- [x] Projektes Projekt von 0 wieder starten, dieses Mal mit der Offiziellen Docs
- [ ] Pages Home und About vom alten js Code im neuen React umschreiben
- [ ] Alternativen falls Expo App immer noch nicht funktioniert, finden

<br><br>

<img width="200" alt="image" src="https://github.com/user-attachments/assets/9d293195-3f30-4839-89a7-de862192849b" />
<img width="200" alt="image" src="https://github.com/user-attachments/assets/a8d6e8ba-b100-4710-8361-a1416b74839c" />

<br><br>

**Epilepsie Warnung**<br>
![MorseTool](https://github.com/user-attachments/assets/0a399c92-b41c-4455-895c-1ef78d51473e)


## Alexander
- [ ] Implementierung Reaktion Meme Geste
- [ ] Anti-spam system
