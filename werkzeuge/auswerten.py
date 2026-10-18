#!/usr/bin/env python3
"""Mitschnitt lesbar machen: zeigt jede Nachricht zwischen Mac und Pult mit Uhrzeit, Richtung, Port und Hex.
Aufruf: python3 auswerten.py mitschnitt.pcap PULT-IP [Notizdatei]
Notizen aus mitschnitt.command werden an der passenden Stelle eingefügt."""
import struct, sys, time

pcap, pult = sys.argv[1], sys.argv[2]
notizen = []
if len(sys.argv) > 3:
    for zeile in open(sys.argv[3], encoding="utf-8"):
        if zeile[:8].count(":") == 2:
            notizen.append((zeile[:8], zeile[9:].rstrip()))
pult_b = bytes(int(x) for x in pult.split("."))
d = open(pcap, "rb").read()
o, link = 24, struct.unpack("<I", d[20:24])[0]
kopf = {1: 14, 0: 4, 113: 16, 12: 0, 276: 20}.get(link, 14)  # Ethernet, Loopback, Linux-cooked, roh
gesehen = set()
while o < len(d):
    ts, us, cl, _ = struct.unpack("<IIII", d[o:o + 16])
    p = d[o + 16:o + 16 + cl]
    o += 16 + cl
    ip = p[kopf:]
    if len(ip) < 20 or ip[0] >> 4 != 4:
        continue
    ihl = (ip[0] & 15) * 4
    proto, src, dst, l4 = ip[9], ip[12:16], ip[16:20], ip[ihl:]
    if pult_b not in (src, dst):
        continue
    t = time.strftime("%H:%M:%S", time.localtime(ts))
    while notizen and notizen[0][0] <= t:
        print(f"\n=== {notizen[0][0]} {notizen[0][1]} ===")
        notizen.pop(0)
    sp, dp = struct.unpack(">HH", l4[:4])
    if proto == 6:
        nutz = l4[(l4[12] >> 4) * 4:]
        seq = l4[4:8]
        if not nutz or (src, seq) in gesehen:
            continue
        gesehen.add((src, seq))
        art = "TCP"
    elif proto == 17:
        nutz, art = l4[8:], "UDP"
    else:
        continue
    richtung = "Pult→Mac" if src == pult_b else "Mac→Pult"
    port = sp if src == pult_b else dp
    print(f"{t}.{us // 1000:03d} {art} {richtung} :{port:<5} {nutz[:64].hex(' ')}{' …' if len(nutz) > 64 else ''}")
