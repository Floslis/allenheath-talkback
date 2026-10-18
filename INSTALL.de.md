# Installation

[English](INSTALL.md) · **Deutsch**

Dauert etwa 10 Minuten: 5 am Mac, 5 am Pult.

## Was du brauchst

- Einen **Mac**, der im **selben Netz wie das Pult** hängt (z. B. der Technik-Laptop)
- Ein **Allen & Heath Avantis** mit Firmware V2.01
- Ein Talkback-Mikro auf einem **freien Eingangskanal**

## 1. Am Pult vorbereiten

1. **Talkback-Mikro** auf einen freien Eingangskanal patchen. Merk dir die Kanalnummer
2. **Netzwerk-MIDI** einschalten: Setup → Control → MIDI. Den **Basiskanal** merken (Standard 12)
3. **Für jede Gruppe eine leere Mute-Gruppe** wählen (z. B. 6, 7, 8 für Band, MD, Vicom). Leer heißt: kein Kanal ist ihr zugewiesen
4. Je einen **Softkey** auf diese Mute-Gruppen legen

> Ohne Softkeys geht es auch, dann schaltest du nur im Browser.

## 2. Am Mac installieren

1. **[Talkback.zip herunterladen](https://github.com/Floslis/avantis-talkback/releases/latest/download/Talkback.zip)** (immer die neueste Version)
2. Entpacken und den Ordner **`Talkback` direkt in deinen Benutzerordner** ziehen (Finder → Gehe zu → Benutzerordner, das Haus-Symbol)

   > ⚠️ **Nicht** auf den Schreibtisch, in „Dokumente“, „Downloads“ oder iCloud. Dort darf ein Autostart-Dienst unter macOS keine Dateien lesen, und das Tool startet nicht. Das Installationsskript prüft das und warnt dich.

3. Im Ordner **Rechtsklick auf `Installieren.command` → Öffnen → Öffnen**

   Ein Doppelklick reicht bei heruntergeladenen Dateien nicht, macOS blockt sie sonst.

4. Fehlt Python 3, fragt macOS, ob die **Entwicklerwerkzeuge** installiert werden sollen: Ja klicken, warten, dann Schritt 3 wiederholen
5. Der Browser öffnet **http://localhost:8787**. Ab jetzt startet das Tool bei jeder Anmeldung von selbst und nach einem Absturz neu

## 3. Einrichten

Im Tool oben rechts auf **Einstellungen**:

1. **Pult suchen** klicken. Das Tool lauscht auf das Pult und zeigt es mit Modell und Firmware an. Antippen übernimmt die IP
2. **Talkback-Kanal** und **MIDI-Basiskanal** aus Schritt 1 eintragen
3. **Mixe** wählen, die im Tool erscheinen sollen
4. **Gruppen** anlegen: Name, Softkey (Mute-Gruppe) und welche Mixe dazugehören. Eine Gruppe kann **„alle übrigen“** sein, sie enthält dann jeden Mix, der in keiner anderen Gruppe steckt
5. **Speichern**

Oben auf der Hauptseite steht jetzt **„Pult verbunden“**.

## 4. Testen

**Teste zuerst außerhalb von Gottesdienst oder Show**, mit jemandem am Pult:

- Im Tool eine Gruppe antippen → am Pult ändern sich die Assigns vom Talkback-Kanal
- Softkey drücken → im Tool ändert sich die Gruppe, die LED leuchtet grün
- Am Pult ein Assign von Hand ändern → das Tool zeigt es nach spätestens einer Sekunde

## Updates

Das Tool schaut alle 6 Stunden auf GitHub nach und installiert neue Versionen **um 4 Uhr nachts**, also nie mitten im Gottesdienst. Steht oben ein blauer Hinweis, kannst du auch sofort installieren. Einstellungen und eigenes Branding bleiben dabei erhalten. Abschalten: Einstellungen → Updates.

## Wenn etwas nicht geht

| Problem | Lösung |
|---|---|
| Browser zeigt „Seite nicht erreichbar“ | Liegt der Ordner im Benutzerordner? Dann `Installieren.command` nochmal ausführen. Fehler stehen in `talkback.log` im Ordner |
| „Pult … nicht erreichbar“ | Einstellungen → Pult suchen. Mac und Pult müssen im selben Netz sein |
| Pult suchen findet nichts | Hängen Mac und Pult in verschiedenen Netzen (VLANs)? Dann die IP von Hand eintragen (Setup → Network am Pult) |
| Softkey macht nichts | Netzwerk-MIDI am Pult an? Stimmt der Basiskanal? Ist die Mute-Gruppe in den Einstellungen eingetragen? |
| Ordner verschoben | `Installieren.command` am neuen Ort nochmal ausführen |

## Entfernen

`Deinstallieren.command` ausführen (Rechtsklick → Öffnen), dann den Ordner löschen.
