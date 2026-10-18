# Neues Pult anbinden: Checkliste für den Termin vor Ort

Ziel: in **etwa 30 Minuten** am Pult alles sammeln, was für einen Treiber nötig ist. Gebaut wird danach in Ruhe.
So lief es auch beim Avantis: Mitschnitt von Mixing Station → Protokoll nachgebaut → Treiber.

## Vorher (zu Hause, 5 Minuten)

- [ ] Mac mit diesem Ordner dabei, Ladekabel, LAN-Adapter
- [ ] Auf dem Mac eine Steuer-Software fürs Pult, die **auf dem Mac selbst** läuft (sonst sieht der Mitschnitt nichts):
  - **Mixing Station** (kann Avantis, SQ, dLive) oder die Software des Herstellers (z. B. SQ-MixPad, dLive Director)
- [ ] Firmware-Stand des Pults herausfinden, wenn möglich

## Am Pult

### 1. Grunddaten (5 Minuten)
- [ ] **Firmware** ablesen (Foto vom Info-Bildschirm)
- [ ] **Mix-Konfiguration** fotografieren: wie viele Mono- und Stereo-Aux, Gruppen, Matrizen
- [ ] **Netzwerk-MIDI** einschalten, **Basiskanal** notieren
- [ ] Einen **freien Eingangskanal** als Testkanal wählen (bei uns war das 64), Nummer notieren
- [ ] Zwei **leere Mute-Gruppen** und einen **freien Softkey** suchen

### 2. Pult finden (2 Minuten)
- [ ] Mac ins Netz des Pults
- [ ] `python3 talkback.py`, dann Einstellungen → **Pult suchen**. Taucht das Pult auf? Foto vom Ergebnis
- [ ] Falls nicht: IP am Pult ablesen (Setup → Network)

### 3. Mitschnitt (15 Minuten)
1. Steuer-Software auf dem Mac **mit dem Pult verbinden**
2. Doppelklick auf **`werkzeuge/mitschnitt.command`**, IP eintippen, Passwort eingeben
3. In der Steuer-Software **auf dem Testkanal** nacheinander, mit ein paar Sekunden Pause, und **vor jeder Aktion kurz tippen, was du machst**:
   - [ ] Steuer-Software **trennen und neu verbinden** (zeigt die Anmeldung)
   - [ ] **Assign** Testkanal → **Aux 1** aus, an
   - [ ] **Assign** Testkanal → **Aux 2** aus, an (zeigt, wie der Mix in der Nummer steckt)
   - [ ] **Assign** auf einem **anderen Kanal** → Aux 1 aus, an (zeigt, wie der Kanal in der Nummer steckt)
   - [ ] **Assign** Testkanal → **Stereo-Aux 1** aus, an
   - [ ] **Send-Pegel** Testkanal → Aux 1 einmal hoch und runter
   - [ ] **Mute** Testkanal an, aus
   - [ ] Am **Pult selbst** ein Assign ändern (zeigt, ob das Pult Änderungen von sich aus meldet)
   - [ ] **Softkey** auf eine leere Mute-Gruppe legen und drücken
   - [ ] Gibt es ein eigenes **Talkback** im Pult? Ziele einmal ändern
4. `fertig` tippen. Auf dem Schreibtisch liegen jetzt `mitschnitt-….pcap` und `mitschnitt-….txt`

### 4. MIDI prüfen (5 Minuten)
- [ ] `python3 werkzeuge/midi-monitor.py IP` → Browser öffnet http://localhost:8765
- [ ] Am Pult Fader, Mute und den Softkey drücken: kommen Zeilen „◀ Pult“?
- [ ] Im Monitor „Name abfragen“ für Kanal 1: kommt eine Antwort?

## Danach

- [ ] `.pcap`, `.txt` und die Fotos an Claude geben: „Neues Pult, hier der Mitschnitt“
- [ ] Claude wertet mit `werkzeuge/auswerten.py` aus, baut `pulte/<name>.py` und trägt es in `pulte/__init__.py` ein
- [ ] Beim nächsten Termin: Treiber am Pult testen, **erst nur lesen**, dann schalten

## Was ein Treiber können muss

Siehe `pulte/basis.py`. Kurz:

| Muss | Wofür |
|---|---|
| Verbinden, Verbindung halten | Lebenszeichen, falls das Pult eins erwartet (Avantis: UDP jede Sekunde) |
| Assign Talkback-Kanal → Mix setzen | der eigentliche Zweck |
| Assign-Zustand lesen und Änderungen melden | damit das Tool zeigt, was am Pult los ist |
| Mix-Namen lesen, vorhandene Mixe erkennen | Kacheln mit echten Namen |
| Mute-Gruppen lesen und setzen | Softkeys mit LED |
| Pult im Netz finden | „Pult suchen“ |
