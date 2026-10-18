# Changelog

Jede Version hat einen deutschen und einen englischen Teil. Die GitHub-Action nimmt den Abschnitt der neuen Version als Text für das Release.
Each version has a German and an English part. The GitHub action uses the section of the new version as release text.

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
