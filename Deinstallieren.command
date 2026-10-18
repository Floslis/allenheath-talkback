#!/bin/bash
launchctl bootout "gui/$(id -u)/de.flotech.talkback" 2>/dev/null
rm -f "$HOME/Library/LaunchAgents/de.flotech.talkback.plist" && echo "Talkback-Autostart entfernt."
read -n1 -p "Taste drücken …"
