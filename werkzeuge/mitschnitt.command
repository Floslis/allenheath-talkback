#!/bin/bash
# Schneidet den Netzwerkverkehr zwischen diesem Mac und einem Pult mit (TCP und UDP).
# Nebenbei Notizen tippen („Assign Aux 1 aus“), die mit Uhrzeit in eine Datei gehen.
# Danach liegen auf dem Schreibtisch: mitschnitt-<Zeit>.pcap und mitschnitt-<Zeit>.txt
cd "$(dirname "$0")"
read -p "IP-Adresse des Pults: " IP
ZEIT=$(date +%Y-%m-%d_%H-%M)
PCAP="$HOME/Desktop/mitschnitt-$ZEIT.pcap"
NOTIZ="$HOME/Desktop/mitschnitt-$ZEIT.txt"
echo "Für den Mitschnitt fragt macOS gleich nach deinem Passwort."
sudo -v || exit 1
sudo /usr/sbin/tcpdump -i any -U -s0 -w "$PCAP" host "$IP" 2>/dev/null &
PID=$!
sleep 1
echo
echo "Mitschnitt läuft. Tippe vor jeder Aktion kurz, was du gleich machst, dann Enter."
echo "Beispiel: „Kanal 64 Assign Aux 1 aus“. Mit „fertig“ beenden."
echo "$(date +%H:%M:%S) Start, Pult $IP" > "$NOTIZ"
while read -p "> " ZEILE; do
  [ "$ZEILE" = "fertig" ] && break
  echo "$(date +%H:%M:%S) $ZEILE" >> "$NOTIZ"
done
sudo kill $PID 2>/dev/null
sudo chown "$USER" "$PCAP"
echo "Gespeichert: $PCAP und $NOTIZ"
read -n1 -p "Taste drücken zum Schließen …"
