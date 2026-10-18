#!/usr/bin/env python3
"""Avantis natives Protokoll (Port 51321), nachgebaut aus Mixing-Station-Mitschnitt 18.10.2026.
python3 avantis-native.py assign KANAL AUX 0|1   ·   python3 avantis-native.py level KANAL AUX HEX4"""
import socket, sys, time

PULT, PORT, TAG = "192.168.1.50", 51321, b"\x01\xf4"


def msgs(buf):
    while (a := buf.find(b"\xf0")) >= 0 and (e := buf.find(b"\xf7", a)) >= 0:
        yield bytes(buf[a:e + 1]); del buf[:e + 1]


def verbinden():
    s = socket.create_connection((PULT, PORT), timeout=5)
    s.sendall(bytes.fromhex("e0 00 04 01 03 c6 0d e7 e0 00 04 04 03 c6 0d e7"))
    name = b"Input Mixer\x00"
    s.sendall(b"\xf0\x00\x01\x00\x00" + TAG + b"\x00\x04" + len(name).to_bytes(2, "big") + name + b"\xf7")
    buf, ende = bytearray(), time.time() + 5
    while time.time() < ende:
        buf += s.recv(65536)
        for m in msgs(buf):
            if m[1] == 0 and m[3:5] == TAG and m[5:11] == b"\x00\x00\x00\x02\x00\x02":
                return s, m[11:13]
    raise RuntimeError("kein Handle für Input Mixer")


def setzen(s, h, param, wert: bytes):
    s.sendall(b"\xf0\x00\x00" + h + TAG + param.to_bytes(2, "big") + len(wert).to_bytes(2, "big") + wert + b"\xf7")


def assign_param(kanal, aux):
    return 0x4550 + (kanal - 1) * 56 + (aux - 1)


if __name__ == "__main__":
    s, h = verbinden()
    print("Handle Input Mixer:", h.hex())
    art, k, a, v = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    p = assign_param(k, a)
    if art == "assign":
        setzen(s, h, p, bytes([int(v)]))
    elif art == "level":
        setzen(s, h, p + 0x2A00, bytes.fromhex(v))
    time.sleep(0.5)
    print("gesendet", art, f"Kanal {k} Aux {a} param {p:04x}", v)
