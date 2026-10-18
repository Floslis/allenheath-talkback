#!/usr/bin/env python3
"""Avantis-Test: verbindet sich per TCP 51325 mit dem Pult, zeigt alles, was es sendet,
und schickt Testbefehle. Start: python3 avantis-test.py [PULT-IP]  → http://localhost:8765"""
import json, socket, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PULT = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.50"
PORT = 51325
WEB = 8765

log, lock = [], threading.Lock()
sock = None
status = "getrennt"

TYP = {0: "Eingang", 1: "Gruppe", 2: "Aux", 3: "Matrix", 4: "FX/Main/DCA"}


def add(richtung, data, info=""):
    with lock:
        log.append({"n": len(log), "t": time.strftime("%H:%M:%S"), "r": richtung,
                    "hex": " ".join(f"{b:02X}" for b in data), "info": info})


def deuten(m, basis):
    s = m[0]
    if s == 0xF0:
        if m[1:8] == bytes([0, 0, 0x1A, 0x50, 0x10, 0x01, 0x00]) and len(m) > 10:
            ch, cmd = m[8], m[9]
            name = {0x01: "Name abfragen", 0x02: "Name", 0x03: "Name setzen", 0x04: "Farbe abfragen",
                    0x05: "Farbe", 0x06: "Farbe setzen", 0x0D: "Send-Pegel", 0x0E: "Assign(?)",
                    0x0F: "Send-Pegel abfragen"}.get(cmd, f"SysEx-Befehl {cmd:02X}")
            rest = m[10:-1]
            txt = ""
            if cmd == 0x02:
                txt = " „" + bytes(rest[1:]).decode("ascii", "replace") + "“"
            return f"{name} · MIDI-Kanal {ch + 1} · Daten {' '.join(f'{b:02X}' for b in rest)}{txt}"
        return "SysEx (fremd)"
    k = s & 0x0F
    off = k - basis
    wo = f"{TYP.get(off, f'Offset {off}')} " if 0 <= off <= 4 else f"MIDI-Kanal {k + 1} "
    t = s & 0xF0
    if t == 0x90:
        return f"{wo}Kanal {m[1] + 1}: Note vel {m[2]:02X}" + (" (Mute an)" if m[2] >= 0x40 else " (Mute aus)" if m[2] else "")
    if t == 0xB0:
        return f"{wo}CC {m[1]:02X} = {m[2]:02X}" + {0x63: " (NRPN Kanal)", 0x62: " (NRPN Parameter)", 0x06: " (Wert)"}.get(m[1], "")
    if t == 0xC0:
        return f"{wo}Program Change {m[1]} (Szene)"
    return ""


def empfangen():
    global sock, status
    while True:
        try:
            s = socket.create_connection((PULT, PORT), timeout=5)
            s.settimeout(None)
            sock, status = s, f"verbunden mit {PULT}"
            add("--", b"", status)
            buf, run = bytearray(), None
            while True:
                d = s.recv(4096)
                if not d:
                    raise ConnectionError("Pult hat getrennt")
                for b in d:
                    if b == 0xFE:  # Active Sensing ignorieren
                        continue
                    if b & 0x80 and b != 0xF7:
                        if buf:
                            fertig(buf)
                        buf = bytearray([b])
                        if b < 0xF0:
                            run = b
                        continue
                    if not buf and run:
                        buf = bytearray([run])
                    buf.append(b)
                    if buf[0] == 0xF0:
                        if b == 0xF7:
                            fertig(buf); buf = bytearray()
                    elif len(buf) >= (2 if buf[0] & 0xF0 in (0xC0, 0xD0) else 3):
                        fertig(buf); buf = bytearray()
        except Exception as e:
            sock, status = None, f"getrennt: {e}"
            add("--", b"", status)
            time.sleep(3)


def fertig(buf):
    add("◀ Pult", bytes(buf), deuten(bytes(buf), basis))


basis = 11  # MIDI-Basiskanal 12 → 0B, im Browser änderbar


def senden(data):
    if not sock:
        return "nicht verbunden"
    sock.sendall(data)
    add("▶ Tool", data, deuten(data, basis))
    return "ok"


HTML = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width">
<title>Avantis-Test</title><style>
body{font:15px system-ui;background:#111;color:#eee;margin:16px}
input,select,button{font:inherit;padding:6px 10px;margin:2px;background:#222;color:#eee;border:1px solid #444;border-radius:6px}
button{background:#2b5;border:0;color:#000;font-weight:600;cursor:pointer}button.aus{background:#c44;color:#fff}
fieldset{border:1px solid #333;border-radius:8px;margin:8px 0}#log{font:13px ui-monospace,monospace;white-space:pre;overflow:auto;height:55vh;background:#000;padding:8px;border-radius:8px}
.p{color:#6cf}.t{color:#fc6}.s{color:#888}</style>
<h2>Avantis-Test <small id=st></small></h2>
<fieldset><legend>Basis</legend>MIDI-Basiskanal <input id=b type=number min=1 max=12 value=12 style=width:4em onchange="fetch('/basis?k='+this.value)">
<button onclick="L.innerHTML='';">Log leeren</button> <button onclick="markiere()">Markierung setzen</button></fieldset>
<fieldset><legend>Send-Pegel (Eingang → Aux/FX/Matrix)</legend>
Eingang <input id=sch type=number value=64 style=width:4em>
Ziel <select id=styp><option value=2>Mono Aux</option><option value=2s>Stereo Aux</option><option value=3>Mono Matrix</option><option value=3s>Stereo Matrix</option><option value=4>Mono FX-Send</option><option value=4s>Stereo FX-Send</option></select>
Nr <input id=snr type=number value=1 style=width:4em>
<button onclick="send(1)">AN 0 dB</button><button class=aus onclick="send(0)">AUS −∞</button><button onclick="abfrage()">Pegel abfragen</button></fieldset>
<fieldset><legend>Eingang</legend>Kanal <input id=mch type=number value=64 style=width:4em>
<button class=aus onclick="mute(1)">Mute an</button><button onclick="mute(0)">Mute aus</button><button onclick="name()">Name abfragen</button></fieldset>
<fieldset><legend>Roh senden (Hex)</legend><input id=raw style=width:70% placeholder="F0 00 00 1A 50 10 01 00 0B 01 00 F7"><button onclick="roh()">Senden</button></fieldset>
<div id=log></div><script>
const L=document.getElementById('log');let n=0;const B=()=>+b.value-1,h=x=>x.toString(16).padStart(2,'0');
const SY=d=>'F0 00 00 1A 50 10 01 00 '+d+' F7';
const post=x=>fetch('/send',{method:'POST',body:x});
function ziel(){let v=styp.value,st=v.endsWith('s'),o=+v[0];let nr=+snr.value-1;
 // Stereo-Mixe liegen im Protokoll hinter den Mono-Mixen (Mono 0x00–0x3F, Stereo ab 0x40)
 return [h(B()+o),h(st?0x40+nr:nr)]}
function send(on){let [k,c]=ziel();post(SY(h(B())+' 0D '+h(+sch.value-1)+' '+k+' '+c+' '+(on?'6B':'00')))}
function abfrage(){let [k,c]=ziel();post(SY(h(B())+' 0F 0D '+h(+sch.value-1)+' '+k+' '+c))}
function mute(on){let s='9'+B().toString(16)+' '+h(+mch.value-1);post(s+' '+(on?'7F':'3F')+' '+s+' 00')}
function name(){post(SY(h(B())+' 01 '+h(+mch.value-1)))}
function roh(){post(raw.value)}
function markiere(){fetch('/mark',{method:'POST',body:prompt('Was drückst du jetzt?')||'---'})}
async function poll(){try{let r=await (await fetch('/log?seit='+n)).json();st.textContent='· '+r.status;
 for(const e of r.log){n=e.n+1;let c=e.r.startsWith('◀')?'p':e.r.startsWith('▶')?'t':'s';
  L.insertAdjacentHTML('beforeend',`<span class=${c}>${e.t} ${e.r.padEnd(7)} ${e.hex.padEnd(48)} ${e.info}</span>\\n`)}
 if(r.log.length)L.scrollTop=1e9}catch(e){st.textContent='· Tool aus?'}setTimeout(poll,300)}poll();
</script>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def antwort(self, body, typ="application/json"):
        b = body.encode()
        self.send_response(200); self.send_header("Content-Type", typ + "; charset=utf-8")
        self.send_header("Content-Length", len(b)); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        global basis
        if self.path.startswith("/log"):
            seit = int(self.path.split("seit=")[1]) if "seit=" in self.path else 0
            with lock:
                self.antwort(json.dumps({"status": status, "log": log[seit:]}))
        elif self.path.startswith("/basis"):
            basis = int(self.path.split("k=")[1]) - 1
            self.antwort('"ok"')
        else:
            self.antwort(HTML, "text/html")

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        if self.path == "/mark":
            add("##", b"", "=== " + body + " ===")
            return self.antwort('"ok"')
        try:
            data = bytes.fromhex(body.replace(",", " "))
        except ValueError:
            return self.antwort('"kein gültiges Hex"')
        self.antwort(json.dumps(senden(data)))


if __name__ == "__main__":
    threading.Thread(target=empfangen, daemon=True).start()
    print(f"Avantis-Test läuft → http://localhost:{WEB}  (Pult {PULT}:{PORT}, Strg+C beendet)")
    ThreadingHTTPServer(("0.0.0.0", WEB), H).serve_forever()
