#!/bin/bash
# Richtet Talkback auf diesem Mac ein: startet bei jeder Anmeldung von selbst und nach Absturz neu.
cd "$(dirname "$0")"
ORDNER="$(pwd)"
PLIST="$HOME/Library/LaunchAgents/de.flotech.talkback.plist"
# Schreibtisch, Dokumente, Downloads und iCloud sind für Autostart-Dienste gesperrt (macOS-Datenschutz):
# das Tool würde starten und sofort ohne Meldung sterben
case "$ORDNER" in
  "$HOME/Desktop"*|"$HOME/Documents"*|"$HOME/Downloads"*|"$HOME/Library/Mobile Documents"*)
    echo "⚠️  Der Ordner liegt in einem gesperrten Bereich:"
    echo "    $ORDNER"
    echo "Bitte den Ordner 'Talkback' direkt in den Benutzerordner ($HOME) verschieben und dieses Skript dort nochmal starten."
    open "$HOME"; read -n1 -p "Taste drücken …"; exit 1 ;;
esac
if ! /usr/bin/python3 -c 'import sys; sys.exit(sys.version_info < (3, 8))' 2>/dev/null; then
  echo "Python 3 fehlt. macOS fragt gleich, ob die Entwicklerwerkzeuge installiert werden sollen: Ja klicken, danach dieses Skript nochmal starten."
  xcode-select --install 2>/dev/null; read -n1 -p "Taste drücken …"; exit 1
fi
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>de.flotech.talkback</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$ORDNER/talkback.py</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$ORDNER/talkback.log</string>
  <key>StandardErrorPath</key><string>$ORDNER/talkback.log</string>
</dict></plist>
PL
launchctl bootout "gui/$(id -u)/de.flotech.talkback" 2>/dev/null
launchctl bootstrap "gui/$(id -u)" "$PLIST" && echo "✅ Talkback läuft und startet ab jetzt bei jeder Anmeldung. Seite: http://localhost:8787"
read -n1 -p "Taste drücken zum Schließen …"
