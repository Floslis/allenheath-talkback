# Changelog

Jede Version hat einen deutschen und einen englischen Teil. Die GitHub-Action nimmt den Abschnitt der neuen Version als Text für das Release.
Each version has a German and an English part. The GitHub action uses the section of the new version as release text.

## 0.7.0

**Deutsch**
- **Treiber-Aufbau:** Alles Pult-Spezifische steckt jetzt in `pulte/` (für das Avantis `pulte/avantis.py`). Neue Pulte kommen als eigene Datei dazu, ohne den Rest anzufassen
- Pult-Typ in den Einstellungen wählbar (bisher nur Avantis)
- Lange Texte in Auswahllisten laufen nicht mehr ins Nachbarfeld

**English**
- **Driver architecture:** everything desk-specific now lives in `pulte/` (for the Avantis `pulte/avantis.py`). New desks are added as their own file without touching the rest
- Desk type selectable in the settings (Avantis only for now)
- Long texts in dropdowns no longer run into the next field

## 0.6.1

**Deutsch**
- **Neuer Name:** Das Projekt heißt jetzt `allenheath-talkback`, weil SQ und dLive dazukommen. Updates kommen ab jetzt direkt von der neuen Adresse, alte Links leitet GitHub weiter

**English**
- **New name:** the project is now called `allenheath-talkback`, since SQ and dLive are coming. Updates now come straight from the new address, GitHub redirects old links

## 0.6.0

**Deutsch**
- **Mixe erkennt das Tool selbst:** Es fragt das Pult nach allen Mixen, nur vorhandene antworten. Die Zahl der Mono-Aux muss niemand mehr eintragen
- In den Einstellungen erscheinen nur noch Mixe, die es am Pult wirklich gibt, mit ihren Namen

**English**
- **The tool detects the mixes by itself:** it asks the desk for all mixes, only existing ones answer. Nobody has to enter the number of mono auxes anymore
- The settings only show mixes that really exist on the desk, with their names

## 0.5.1

**Deutsch**
- Auswahllisten sehen jetzt auch in Safari aus wie die übrigen Felder

**English**
- Dropdowns now look like the other fields in Safari too

## 0.5.0

**Deutsch**
- **Neues Design** in der Stream-Design-Sprache: Titelleiste mit rotem Balken, eckige Kästen, gut lesbare Schrift (Atkinson Hyperlegible). **Grün = hört dich**, passend zur grünen Softkey-LED am Pult. Hell und dunkel nach Systemeinstellung
- **Englische Oberfläche:** Sprache automatisch nach Browser oder fest in den Einstellungen
- **Pause und Beenden:** Pause trennt das Tool vom Pult, bis du „Fortsetzen“ drückst (bleibt auch nach einem Neustart). Beenden schaltet es bis zur nächsten Anmeldung aus
- **Nach Updates suchen:** Knopf in den Einstellungen, mit Anzeige der installierten Version
- **Entfernt:** Das automatische Verbinden mit einem unbekannten Pult. Das Pult wird nur noch über „Pult suchen“ gefunden und von Hand übernommen
- Ist das Pult nicht erreichbar, erscheint oben ein deutlicher Hinweis mit Knopf zur Suche

**English**
- **New design:** title bar with red accent, square boxes, highly readable font (Atkinson Hyperlegible). **Green = hears you**, matching the green softkey LED on the desk. Light and dark follow the system
- **English interface:** language follows the browser or can be set in the settings
- **Pause and quit:** pause disconnects the tool from the desk until you press "Resume" (survives a restart). Quit turns it off until the next login
- **Check for updates:** button in the settings, shows the installed version
- **Removed:** automatically connecting to an unknown desk. The desk is only found with "Find desk" and taken by hand
- If the desk can't be reached, a clear notice with a search button appears at the top

## 0.4.0

**Deutsch**
- **Pult suchen:** Knopf in den Einstellungen. Das Tool lauscht auf die Rufe der Pulte im Netz und zeigt Modell und Firmware. Hört es nichts, sucht es das eigene Netz ab
- **Automatisch finden:** Bei einer Neuinstallation übernimmt das Tool die IP selbst, wenn genau ein Avantis im Netz ist. Ein eingerichtetes Tool springt nie auf ein anderes Pult
- **Behoben:** Nach dem Bearbeiten einer Gruppe übers Zahnrad schaltete das Tool bis zum Neustart nichts mehr
- Updates übernehmen jetzt auch neue Dateien. Fehlt eine, repariert sich das Tool einmal selbst
- Fertiges `Talkback.zip` an jedem Release, Installationsanleitung in `INSTALL.md`

**English**
- **Find desk:** button in the settings. The tool listens for the desks' announcements on the network and shows model and firmware. If it hears nothing, it scans the local network
- **Automatic discovery:** on a fresh install the tool takes the IP by itself if exactly one Avantis is on the network. A configured tool never switches to another desk
- **Fixed:** after editing a group with the gear icon, the tool stopped switching until restarted
- Updates now also bring new files. If one is missing, the tool repairs itself once
- Ready-made `Talkback.zip` on every release, installation guide in `INSTALL.md`

## 0.3.2

**Deutsch**
- **Behoben:** Der Update-Hinweis stand immer oben, auch ohne Update
- Ist das Pult nicht erreichbar, zeigt das Tool die IP und verweist auf die Einstellungen

**English**
- **Fixed:** the update banner was always shown, even without an update
- If the desk can't be reached, the tool shows the IP and points to the settings

## 0.3.1

**Deutsch**
- Ko-fi-Knopf neben „Ein Produkt von FLOTECH“, öffnet in neuem Tab

**English**
- Ko-fi button next to "Ein Produkt von FLOTECH", opens in a new tab

## 0.3.0

**Deutsch**
- **Updates von GitHub:** Prüfung alle 6 Stunden, Installation um 4 Uhr nachts oder per Knopf. Einstellungen und eigenes Branding bleiben
- Einstellungsseite, beliebig viele Gruppen, Branding-Profile
- Erste öffentliche Version

**English**
- **Updates from GitHub:** checks every 6 hours, installs at 4 am or with one click. Settings and own branding stay
- Settings page, any number of groups, branding profiles
- First public version
