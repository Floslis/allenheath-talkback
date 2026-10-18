# Talkback für Allen & Heath Avantis

[English](README.md) · **Deutsch**

> [!WARNING]
> **Frühe Entwicklung. Nutzung auf eigene Gefahr.**
> Das Tool spricht mit dem Pult über ein Netzwerkprotokoll, das Allen & Heath nicht dokumentiert. Bei unserem Avantis (Firmware V2.01 Rev. 97241) läuft es, an anderen Aufbauten oder nach einem Firmware-Update kann es sich falsch verhalten. **Teste es zuerst außerhalb von Gottesdienst oder Show**, mit jemandem am Pult. Keine Gewährleistung, siehe [LICENSE](LICENSE).

**Wer hört mich, wenn ich ins Talkback-Mikro spreche?** Dieses Tool legt das fest, mit einem Klick im Browser oder einem Softkey am Pult. Statt das eingebaute Talkback des Pults zu nutzen, schaltet es das **Assign eines normalen Eingangskanals** auf die In-Ear-Mixe. Gruppen wie „Band“, „MD“ oder „Vicom“ lassen sich kombinieren.

<p align="center">
  <img src="docs/talkback-hell.png" alt="Talkback-Oberfläche, helles Design" width="49%">
  <img src="docs/talkback-dunkel.png" alt="Talkback-Oberfläche, dunkles Design" width="49%">
</p>

[![Unterstütze mich auf Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/floslist)

---

## Warum es das gibt

Das eingebaute Talkback des Pults hat für uns einen großen Haken: **Die Musiker können nicht selbst einstellen, wie laut das Talkback in ihrem In-Ear-Mix ist.** Deshalb liegt unser Talkback-Mikro auf einem normalen Eingangskanal. So stellt jeder die Lautstärke selbst ein, wie bei jedem anderen Kanal auch.

Trotzdem wollen wir **einzeln steuern, wer uns hört**. Und das Pult hat keinen Softkey, der das Assign für mehrere Mixe gleichzeitig an- und ausschaltet. Deshalb habe ich dieses Tool gebaut.

## Was es kann

| | |
|---|---|
| 🎙️ **Echtes Assign** | Schaltet das Assign vom Talkback-Kanal auf Aux- und Stereo-Aux-Mixe an und aus, nicht nur den Send-Pegel |
| 🔄 **Immer synchron** | Mix-Namen und Zustand kommen live vom Pult. Ändert jemand etwas am Pult, sieht man es im Tool sofort |
| 👥 **Gruppen** | Beliebig viele, jede mit eigenem Namen und eigenen Mixen. Eine Gruppe kann „alle übrigen“ sein (z. B. Band). Mehrere gleichzeitig möglich |
| 🎛️ **Softkeys mit LED** | Softkeys am Pult schalten die Gruppen. Die LED leuchtet grün, wenn die Gruppe an ist, egal wo geschaltet wurde |
| ⚙️ **Einstellungsseite** | Pult-IP, Talkback-Kanal, Mixe und Gruppen, alles im Browser änderbar |
| 🎨 **Branding** | Eigenes Logo, eigener Titel und eigene Farben pro Gemeinde oder Veranstaltungsort, aus einem Profil-Ordner |
| 🚀 **Läuft von selbst** | Startet bei der Anmeldung und nach einem Absturz neu. Nur Python 3, keine weiteren Pakete |

## Unterstützte Pulte

| Pult | Firmware | Stand |
|---|---|---|
| Allen & Heath **Avantis** | V2.01 Rev. 97241 | ✅ jeden Sonntag im Einsatz |
| Allen & Heath dLive | – | 🔜 geplant |
| Allen & Heath SQ | – | 🔜 geplant |

Weitere Pulte kommen als eigene Treiber dazu. Du hast ein Pult und willst helfen? Mach ein Issue auf.

## So funktioniert es

```mermaid
flowchart LR
    B["Browser<br/>localhost:8787"] <--> T["talkback.py<br/>auf dem Mac"]
    T <-->|"TCP 51321 + UDP<br/>Assign, Zustand"| P["Avantis"]
    T <-->|"MIDI über TCP 51325<br/>Namen, Mute-Gruppen"| P
    S["Softkeys am Pult"] -->|"schalten leere<br/>Mute-Gruppen"| P
```

- **Assign und Zustand** laufen über das Netzwerkprotokoll, das auch Director und Mixing Station nutzen. Es ist nicht offiziell dokumentiert und wurde aus Mitschnitten nachgebaut
- **Namen und Softkeys** laufen über das offizielle MIDI-über-TCP-Protokoll
- **Softkey-Trick:** Ein Softkey mit „Custom MIDI“ hat keine steuerbare LED. Deshalb schaltet jeder Softkey eine **leere Mute-Gruppe**. Deren Zustand kann das Tool lesen und setzen, so bleibt die LED immer richtig

## Installation

**Voraussetzungen:** ein Mac im selben Netz wie das Pult, Python 3 (fehlt es, bietet macOS die Installation an)

1. [Neueste Version herunterladen](../../archive/refs/heads/main.zip) und entpacken
2. Den Ordner **direkt in deinen Benutzerordner** legen
   > ⚠️ Nicht auf den Schreibtisch, in „Dokumente“ oder „Downloads“. Dort darf ein Autostart-Dienst unter macOS keine Dateien lesen, und das Tool startet nicht. Das Installationsskript prüft das und warnt dich
3. **Rechtsklick auf `Installieren.command` → Öffnen**
4. Der Browser öffnet sich mit http://localhost:8787. Oben steht „Pult · verbunden“

Nur mal ausprobieren, ohne Autostart: `python3 talkback.py`
Wieder entfernen: `Deinstallieren.command`

## Einrichtung am Pult

1. Das **Talkback-Mikro** auf einen freien Eingangskanal legen, Assign auf die In-Ear-Mixe muss möglich sein
2. **Netzwerk-MIDI** einschalten: Setup → Control → MIDI, Basiskanal merken (Standard 12)
3. Pro Gruppe **eine leere Mute-Gruppe** wählen und je einen **Softkey** darauf legen
4. Im Tool **Einstellungen** öffnen und Pult-IP, Talkback-Kanal, Mixe und Gruppen eintragen

<p align="center"><img src="docs/einstellungen.png" alt="Einstellungsseite" width="70%"></p>

## Updates

Das Tool schaut alle 6 Stunden auf GitHub nach. Neue Versionen installieren sich **um 4 Uhr nachts** von selbst, so startet es nie mitten im Gottesdienst neu, oder sofort per Knopf im Hinweis. Getauscht werden nur Code-Dateien, deine Einstellungen und eigenen Branding-Profile bleiben. Die vorige Fassung liegt in `.sicherung/`. Automatische Updates lassen sich in den Einstellungen abschalten.

## Branding

Jedes Profil ist ein Ordner in `branding/` mit einer `profil.json` und optional einer `logo.svg`:

```json
{
  "name": "Meine Gemeinde",
  "titel": "Talkback",
  "logo": "logo.svg",
  "farben": {
    "hell":   { "an": "#c2410c", "an-hell": "#ffedd5" },
    "dunkel": { "an": "#fb923c", "an-hell": "#3b1d0c" }
  }
}
```

Das Profil wählst du unter Einstellungen → Aussehen. Eigene Profile landen nicht im Git und überstehen Updates. Ein Beispiel liegt in `branding/beispiel/`.

## Roadmap

- [x] Einstellungen im Tool: Pult-IP, Kanal, Mixe, beliebig viele Gruppen
- [x] Branding-Profile: Logo, Titel, Farben
- [x] Updates von GitHub: Prüfung alle 6 Stunden, Installation um 4 Uhr nachts (nie im Gottesdienst) oder per Klick
- [ ] **Weitere Pulte** über Treiber: dLive, SQ
- [ ] **Englische Oberfläche**
- [ ] **Bedienung vom Handy oder Tablet** im lokalen Netz, abschaltbar

## Gut zu wissen

- Das Netzwerkprotokoll ist **nicht offiziell dokumentiert**. Ein Firmware-Update am Pult kann es ändern
- Getestet am Avantis mit Firmware V2.01 im laufenden Gottesdienst. Während der Entwicklung meldete das Pult einmal „Internal Error“, ohne Folgen für den Ton. Ursache war ein fehlendes Lebenszeichen, das ist behoben
- Das Tool lauscht nur auf dem eigenen Rechner (`127.0.0.1`), nicht im Netz
- Kein offizielles Produkt von Allen & Heath und nicht mit Allen & Heath verbunden

## Unterstützen

Dir hilft das Tool? Über einen Kaffee freue ich mich sehr. ☕

[![Unterstütze mich auf Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/floslist)

## Lizenz

[MIT](LICENSE) · Ein Projekt von **FLOTECH**, Veranstaltungstechnik und Film
