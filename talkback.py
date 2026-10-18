#!/usr/bin/env python3
"""Avantis-Talkback: schaltet das Assign vom Talkback-Kanal auf die In-Ear-Mixe.
Natives Protokoll (TCP 51321 + UDP) für Assign und Zustand, MIDI/TCP (51325) für Namen und Mute-Gruppen.
Einstellungen in einstellungen.json, änderbar unter http://localhost:8787/einstellungen
Start: python3 talkback.py  → http://localhost:8787"""
import datetime, ipaddress, json, re, socket, sys, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VERSION = "0.6.1"  # erhöhen → die GitHub-Action baut daraus ein Release, die Tools holen es sich
WEB = 8787
ORDNER = Path(__file__).resolve().parent
EINSTELLUNGEN = ORDNER / "einstellungen.json"
ALT_GRUPPEN = ORDNER / "gruppen.json"
BRANDING = ORDNER / "branding"  # je Profil ein Ordner mit profil.json und optional logo.svg  # Format bis 18.10.2026, wird einmalig übernommen
TAG = b"\x01\xf4"

STANDARD = {
    "branding": "standard",
    "auto_update": True,       # nachts um 4 Uhr installieren, nie während eines Gottesdienstes
    "pausiert": False,         # Pause: keine Verbindung zum Pult, bis jemand „Fortsetzen“ drückt
    "sprache": "auto",         # auto (folgt dem Browser), de, en
    "pult_ip": "192.168.1.50",
    "talkback_kanal": 87,
    "midi_kanal": 12,          # MIDI-Basiskanal am Pult (Setup → Control → MIDI)
    "mono_aux_anzahl": 12,     # Stereo-Aux liegen im Input Mixer hinter den Mono-Aux
    "ziele": [f"aux{i}" for i in range(1, 10)] + [f"staux{i}" for i in range(1, 6)],
    "gruppen": [
        {"name": "Band", "rest": True, "mixe": [], "mutegruppe": 6},
        {"name": "MD", "rest": False, "mixe": [], "mutegruppe": 7},
        {"name": "Vicom", "rest": False, "mixe": [], "mutegruppe": 8},
    ],
}


# ---------- Einstellungen ----------

def ziel_info(key, cfg):
    """aux3 → ("Aux 3", Slot, MIDI-Nummer für den Namen). Stereo-Mixe belegen 2 Slots."""
    art, nr = re.fullmatch(r"(aux|staux)(\d+)", key).groups()
    nr = int(nr)
    if art == "aux":
        return f"Aux {nr}", nr - 1, nr - 1
    return f"StAux {nr}", cfg["mono_aux_anzahl"] + (nr - 1) * 2, 0x40 + nr - 1


def profile():
    """Verfügbare Branding-Profile: Ordnername → Anzeigename."""
    liste = {}
    for d in sorted(BRANDING.glob("*/profil.json")):
        if re.fullmatch(r"[a-z0-9-]+", d.parent.name):
            try:
                liste[d.parent.name] = json.loads(d.read_text()).get("name", d.parent.name)
            except ValueError:
                pass
    return liste


def branding():
    """Gewähltes Profil für die Seiten: Titel, Logo als SVG-Text, Farben."""
    ordner = BRANDING / cfg["branding"]
    try:
        p = json.loads((ordner / "profil.json").read_text())
    except (OSError, ValueError):
        p = {}
    logo = None
    if p.get("logo"):
        datei = (ordner / p["logo"]).resolve()
        if datei.parent == ordner.resolve() and datei.suffix == ".svg" and datei.exists():
            logo = datei.read_text()
    return {"name": p.get("name", ""), "titel": p.get("titel", "Talkback"), "logo": logo, "farben": p.get("farben", {}),
            "sprache": cfg.get("sprache", "auto")}


def pruefen(cfg):
    """Wirft ValueError mit verständlicher Meldung, gibt die bereinigte Fassung zurück."""
    c = {k: cfg.get(k, v) for k, v in STANDARD.items()}
    if c["branding"] not in profile():
        c["branding"] = "standard"
    ipaddress.ip_address(c["pult_ip"])
    for feld, lo, hi in (("talkback_kanal", 1, 128), ("midi_kanal", 1, 12), ("mono_aux_anzahl", 0, 24)):
        c[feld] = int(c[feld])
        if not lo <= c[feld] <= hi:
            raise ValueError(f"{feld} muss zwischen {lo} und {hi} liegen")
    c["ziele"] = [z for z in dict.fromkeys(c["ziele"]) if re.fullmatch(r"(aux([1-9]|1\d|2[0-4])|staux([1-9]|1[0-2]))", z)]
    if not c["ziele"]:
        raise ValueError("mindestens ein Mix muss ausgewählt sein")
    namen, gruppen = set(), []
    for g in c["gruppen"]:
        name = str(g.get("name", "")).strip()[:20]
        if not name or name in namen:
            raise ValueError(f"Gruppenname „{name}“ fehlt oder ist doppelt")
        namen.add(name)
        mg = g.get("mutegruppe")
        mg = int(mg) if mg not in (None, "", 0, "0") else None
        if mg is not None and not 1 <= mg <= 24:
            raise ValueError("Mute-Gruppe muss zwischen 1 und 24 liegen")
        gruppen.append({"name": name, "rest": bool(g.get("rest")), "mutegruppe": mg,
                        "mixe": [m for m in g.get("mixe", []) if m in c["ziele"]]})
    if sum(g["rest"] for g in gruppen) > 1:
        raise ValueError("nur eine Gruppe kann „alle übrigen“ sein")
    mgs = [g["mutegruppe"] for g in gruppen if g["mutegruppe"]]
    if len(mgs) != len(set(mgs)):
        raise ValueError("jede Mute-Gruppe nur einmal vergeben")
    c["gruppen"] = gruppen
    c["auto_update"] = bool(c["auto_update"])
    c["pausiert"] = bool(c["pausiert"])
    if c["sprache"] not in ("auto", "de", "en"):
        c["sprache"] = "auto"
    return c


def laden():
    try:
        return pruefen(json.loads(EINSTELLUNGEN.read_text()))
    except FileNotFoundError:
        pass
    except (ValueError, TypeError, AttributeError) as e:
        print("einstellungen.json fehlerhaft, nehme Standard:", e, flush=True)
        return pruefen(STANDARD)
    c = json.loads(json.dumps(STANDARD))
    try:  # alte gruppen.json übernehmen (Indizes in der alten, festen Ziel-Reihenfolge)
        alt = json.loads(ALT_GRUPPEN.read_text())
        for g in c["gruppen"]:
            g["mixe"] = [c["ziele"][i] for i in alt.get(g["name"], []) if i < len(c["ziele"])]
    except (OSError, ValueError):
        pass
    c = pruefen(c)
    EINSTELLUNGEN.write_text(json.dumps(c, indent=2, ensure_ascii=False))
    return c


cfg = laden()
ZIELE, PARAM_ZU_ZIEL = [], {}
zustand = {"verbunden": False, "an": [], "namen": [], "gruppen_an": {}, "version": VERSION, "update": None,
           "vorhanden": {}}  # alle Mixe, die das Pult hat: key → Name (aus den Namensabfragen)
ALLE_MIXE = [(f"aux{i}", i - 1) for i in range(1, 25)] + [(f"staux{i}", 0x40 + i - 1) for i in range(1, 13)]
mg_stand = {}
lock = threading.Lock()
pult = {"sock": None, "handle": None, "udp": None, "midi": None}


def anwenden(neu, neu_verbinden):
    """Neue Einstellungen übernehmen. Bei anderer IP oder anderem Kanal die Verbindungen neu aufbauen."""
    global cfg, ZIELE, PARAM_ZU_ZIEL
    with lock:
        cfg = neu
        ZIELE = [(k,) + ziel_info(k, cfg) for k in cfg["ziele"]]  # (key, Anzeige, Slot, MIDI-Nr)
        PARAM_ZU_ZIEL = {param(z[2]): i for i, z in enumerate(ZIELE)}
        if neu_verbinden or len(zustand["an"]) != len(ZIELE):
            # neue Verbindung → das Pult schickt beim Abonnieren alles neu
            zustand.update(an=[None] * len(ZIELE), namen=[""] * len(ZIELE))
            mg_stand.clear()
        # sonst den bekannten Zustand behalten: das Pult meldet nur Änderungen, nicht den Stand nochmal
        alt = zustand["gruppen_an"]
        zustand["gruppen_an"] = {g["name"]: alt.get(g["name"], False) for g in cfg["gruppen"]}
        for name in list(mg_stand):
            if name not in zustand["gruppen_an"]:
                del mg_stand[name]
        socks = [pult["sock"], pult["midi"]]
    if neu_verbinden:
        for s in socks:  # die Threads merken das und verbinden sich neu
            try:
                s.shutdown(socket.SHUT_RDWR)
            except (OSError, AttributeError):
                pass


def param(slot):
    return 0x4550 + (cfg["talkback_kanal"] - 1) * 56 + slot


def midi_basis():
    return cfg["midi_kanal"] - 1


# ---------- Pult: natives Protokoll ----------

def nachrichten(buf):
    while (a := buf.find(b"\xf0")) >= 0 and (e := buf.find(b"\xf7", a)) >= 0:
        yield bytes(buf[a:e + 1])
        del buf[:e + 1]


def senden(s, h, prm, daten):
    s.sendall(b"\xf0\x00\x00" + h + TAG + prm.to_bytes(2, "big") + len(daten).to_bytes(2, "big") + daten + b"\xf7")


def abonnieren(s, h):
    for p in PARAM_ZU_ZIEL:  # pro Parameter einzeln, wie Mixing Station
        senden(s, h, 0x0006, b"\x00\x00" + TAG + p.to_bytes(2, "big") * 2 + b"\x00\xff")


def nativ():
    """Hält die Verbindung zum Pult, abonniert die Assigns und führt den Zustand."""
    while True:
        s = u = None
        if cfg["pausiert"]:
            time.sleep(1)
            continue
        try:
            ip = cfg["pult_ip"]
            s = socket.create_connection((ip, 51321), timeout=5)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # merkt echte Abbrüche (Kabel, Pult aus)
            s.setsockopt(socket.IPPROTO_TCP, 0x10, 10)  # TCP_KEEPALIVE (macOS): nach 10 s Ruhe prüfen
            # Anmeldung: eigenen UDP-Port nennen, das Pult nennt seinen. Ohne Lebenszeichen per UDP
            # meldet das Pult „Internal Error“ und trennt nach ~30 s (siehe udp_lebenszeichen)
            u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            u.bind(("", 0))
            u.settimeout(0.2)
            port = u.getsockname()[1].to_bytes(2, "big")
            s.sendall(b"\xe0\x00\x04\x01\x03" + port + b"\xe7" + b"\xe0\x00\x04\x04\x03" + port + b"\xe7")
            name = b"Input Mixer\x00"
            s.sendall(b"\xf0\x00\x01\x00\x00" + TAG + b"\x00\x04" + len(name).to_bytes(2, "big") + name + b"\xf7")
            s.settimeout(2)
            buf, h = bytearray(), None
            udp = {"sock": u, "ziel": None}
            pult["udp"] = udp
            with lock:
                pult["sock"] = s
            while True:
                try:
                    d = s.recv(65536)
                except socket.timeout:  # Funkstille ist normal, wenn sich am Pult nichts ändert
                    continue
                if not d:
                    raise ConnectionError("Pult hat getrennt")
                if udp["ziel"] is None and (k := (bytes(buf) + d).find(b"\xe0\x00\x04\x02\x03")) >= 0:
                    rest = (bytes(buf) + d)[k + 5:k + 7]
                    if len(rest) == 2:
                        udp["ziel"] = (ip, int.from_bytes(rest, "big"))
                buf += d
                for m in nachrichten(buf):
                    if h is None and m[1] == 0 and m[3:5] == TAG and m[5:11] == b"\x00\x00\x00\x02\x00\x02":
                        h = m[11:13]
                        abonnieren(s, h)
                        with lock:
                            pult["handle"] = h
                            zustand["verbunden"] = True
                    elif h and len(m) == 13 and m[3:7] == TAG + h:
                        with lock:
                            i = PARAM_ZU_ZIEL.get(int.from_bytes(m[7:9], "big"))
                            if i is not None:
                                zustand["an"][i] = bool(m[11])
        except OSError as e:
            print(time.strftime("%H:%M:%S"), "Pult-Verbindung weg:", repr(e), flush=True)
        with lock:
            pult.update(sock=None, handle=None, udp=None)
            zustand["verbunden"] = False
            zustand["an"] = [None] * len(ZIELE)
        for x in (s, u):
            try:
                x.close()
            except (OSError, AttributeError):
                pass
        time.sleep(3)


def udp_lebenszeichen():
    """Jede Sekunde e0 00 01 03 e7 per UDP ans Pult (wie Mixing Station), Eingehendes verwerfen."""
    while True:
        udp = pult.get("udp")
        if udp and udp["ziel"]:
            try:
                udp["sock"].sendto(b"\xe0\x00\x01\x03\xe7", udp["ziel"])
                ende = time.time() + 1
                while time.time() < ende:
                    try:
                        udp["sock"].recv(65536)
                    except socket.timeout:
                        pass
                continue
            except OSError:
                pass
        time.sleep(0.2)


# ---------- Pult: MIDI über TCP ----------

def midi():
    """Dauerverbindung MIDI/TCP: Mix-Namen (jede Minute) und die Mute-Gruppen der Softkeys."""
    while True:
        if cfg["pausiert"]:
            time.sleep(1)
            continue
        try:
            s = socket.create_connection((cfg["pult_ip"], 51325), timeout=5)
            with lock:
                pult["midi"] = s
            s.settimeout(1)
            buf, naechste, lauf = bytearray(), 0, None
            while True:
                if time.time() > naechste:
                    # alle möglichen Mixe abfragen: nur die vorhandenen antworten, so zählt das Tool sie selbst
                    gefragt = time.time()
                    for _, nr in ALLE_MIXE:
                        s.sendall(bytes([0xF0, 0, 0, 0x1A, 0x50, 0x10, 1, 0, midi_basis() + 2, 0x01, nr, 0xF7]))
                    naechste = time.time() + 60
                    threading.Timer(3, mixe_auswerten, args=(gefragt,)).start()
                try:
                    d = s.recv(4096)
                except socket.timeout:
                    continue
                if not d:
                    raise ConnectionError("MIDI getrennt")
                for b in d:
                    if b == 0xFE:  # Active Sensing
                        continue
                    if b & 0x80 and b != 0xF7:  # neues Statusbyte
                        buf = bytearray([b])
                        if b < 0xF0:
                            lauf = b
                        continue
                    if not buf and lauf:  # Running Status
                        buf = bytearray([lauf])
                    buf.append(b)
                    if buf[0] == 0xF0 and b == 0xF7:
                        midi_nachricht(bytes(buf)); buf = bytearray()
                    elif buf[0] != 0xF0 and len(buf) == 3:
                        midi_nachricht(bytes(buf)); buf = bytearray()
        except OSError:
            pass
        with lock:
            pult["midi"] = None
        time.sleep(3)


def mixe_auswerten(seit):
    """Nach einer Abfragerunde: welche Mixe gibt es, wie viele Mono-Aux? Stimmt die Zahl nicht, umstellen."""
    with lock:
        frisch = {nr: name for nr, (name, t) in antworten.items() if t >= seit}
        if not frisch:
            return  # keine Antwort (Pult weg), nichts ändern
        zustand["vorhanden"] = {k: frisch[nr] for k, nr in ALLE_MIXE if nr in frisch}
        mono = sum(1 for nr in frisch if nr < 0x40)
    if mono != cfg["mono_aux_anzahl"]:
        print(time.strftime("%H:%M:%S"), f"Pult hat {mono} Mono-Aux, stelle um", flush=True)
        speichern(dict(cfg, mono_aux_anzahl=mono))


def mutegruppe_note(nr):
    return 0x45 + nr  # Mute-Gruppe 1 = 0x46


antworten = {}  # MIDI-Nummer → (Name, Zeit) der letzten Namensantworten


def midi_nachricht(m):
    if m[0] == 0xF0 and len(m) > 11 and m[9] == 0x02:  # Name
        name = m[11:-1].split(b"\x00")[0].decode("latin1").strip()
        with lock:
            antworten[m[10]] = (name, time.time())
            for i, z in enumerate(ZIELE):
                if m[10] == z[3]:
                    zustand["namen"][i] = name
    # Mute-Gruppen: Note On auf Kanal Basis+4, 7F = gemutet, 3F = nicht gemutet (danach ein 00 als Abschluss)
    elif m[0] == 0x90 | (midi_basis() + 4) and m[2] in (0x7F, 0x3F):
        for g in cfg["gruppen"]:
            if g["mutegruppe"] and mutegruppe_note(g["mutegruppe"]) == m[1]:
                softkey(g["name"], m[2] == 0x3F)  # invertiert: Gruppe an = Mute-Gruppe aus (LED grün)


# ---------- Gruppen ----------

def mixe_von(name):
    """Indizes der Mixe einer Gruppe. „alle übrigen“ = alles, was in keiner anderen Gruppe steckt."""
    keys = [z[0] for z in ZIELE]
    g = next((g for g in cfg["gruppen"] if g["name"] == name), None)
    if not g:
        return []
    if g["rest"]:
        belegt = {m for h in cfg["gruppen"] if not h["rest"] for m in h["mixe"]}
        return [i for i, k in enumerate(keys) if k not in belegt]
    return [keys.index(m) for m in g["mixe"] if m in keys]


def gruppe_schalten(name, an):
    """an: Mixe der Gruppe dazu. aus: Mixe raus, außer eine andere aktive Gruppe braucht sie."""
    with lock:
        neu = list(zustand["an"])
        aktiv = dict(zustand["gruppen_an"])
    if None in neu or name not in aktiv:
        return False
    aktiv[name] = an
    behalten = {i for h, a in aktiv.items() if a and h != name for i in mixe_von(h)}
    for i in mixe_von(name):
        neu[i] = an or i in behalten
    return setzen(neu)


def softkey(name, an):
    with lock:
        if mg_stand.get(name) == an:  # eigenes Echo oder unverändert
            return
        mg_stand[name] = an
    gruppe_schalten(name, an)


def led_abgleich():
    """Gruppe gilt als an, wenn alle ihre Mixe assigned sind. LED (Mute-Gruppe) folgt dem,
    aber erst wenn der Zustand 2 Runden (0,6 s) gleich bleibt, sonst flackert sie beim Umschalten."""
    vorher = {}
    while True:
        time.sleep(0.3)
        with lock:
            an, s, gruppen = list(zustand["an"]), pult.get("midi"), list(cfg["gruppen"])
        if not an or None in an:
            continue
        for g in gruppen:
            m = mixe_von(g["name"])
            ist = bool(m) and all(an[i] for i in m if i < len(an))
            stabil, vorher[g["name"]] = vorher.get(g["name"]) == ist, ist
            if not stabil:
                continue
            with lock:
                zustand["gruppen_an"][g["name"]] = ist
                alt = mg_stand.get(g["name"])
                mg_stand[g["name"]] = ist
            if alt != ist and s and g["mutegruppe"]:
                k, n = 0x90 | (midi_basis() + 4), mutegruppe_note(g["mutegruppe"])
                try:
                    s.sendall(bytes([k, n, 0x3F if ist else 0x7F, k, n, 0]))
                except OSError:
                    pass


def setzen(an):
    """an: Liste mit True/False je Ziel."""
    with lock:
        s, h = pult["sock"], pult["handle"]
        if not s or not h or len(an) != len(ZIELE):
            return False
        zustand["an"] = [bool(w) for w in an]  # auf einmal, damit der LED-Abgleich keinen halben Zustand sieht
        params = [param(z[2]) for z in ZIELE]
    for p, wert in zip(params, an):
        senden(s, h, p, bytes([1 if wert else 0]))
    return True


def speichern(neu):
    neu = pruefen(neu)
    verbinden = any(neu[k] != cfg[k] for k in ("pult_ip", "talkback_kanal", "midi_kanal", "mono_aux_anzahl", "ziele", "pausiert"))
    EINSTELLUNGEN.write_text(json.dumps(neu, indent=2, ensure_ascii=False))
    anwenden(neu, verbinden)


# ---------- Updates ----------

def update_installieren(info):
    import aktualisieren
    print(time.strftime("%H:%M:%S"), "installiere Version", info["version"], flush=True)
    aktualisieren.installieren(info["url"])
    (ORDNER / ".nach-update").write_text(info["version"])  # nach dem Neustart keinen Browser öffnen
    aktualisieren.neu_starten()


PFLICHT = ["suche.py", "stream.css", "talkback.css", "oberflaeche.js"]  # Module, die ältere Updater noch nicht kannten


def update_wache():
    """Prüft alle 6 h auf ein neues Release. Automatisch installiert wird nur zwischen 4 und 5 Uhr."""
    import aktualisieren
    naechste = 0
    # Selbstreparatur: hat ein älterer Updater eine neue Datei nicht mitgebracht, das Release nochmal holen
    marke = ORDNER / f".reparatur-{VERSION}"  # höchstens ein Versuch pro Version, keine Neustart-Schleife
    if any(not (ORDNER / d).exists() for d in PFLICHT) and not marke.exists():
        marke.write_text("1")
        try:
            v, url, _ = aktualisieren.neueste()
            update_installieren({"version": v, "url": url})
        except Exception as e:
            print(time.strftime("%H:%M:%S"), "Selbstreparatur fehlgeschlagen:", repr(e), flush=True)
    while True:
        if time.time() > naechste:
            try:
                v, url, text = aktualisieren.neueste()
                neu = {"version": v, "url": url, "text": text[:2000]} if aktualisieren.version_tupel(v) > aktualisieren.version_tupel(VERSION) else None
                with lock:
                    zustand["update"] = neu
                naechste = time.time() + 6 * 3600
            except Exception as e:  # offline, GitHub nicht erreichbar … später nochmal
                print(time.strftime("%H:%M:%S"), "Update-Prüfung fehlgeschlagen:", repr(e), flush=True)
                naechste = time.time() + 1800
        info = zustand["update"]
        if info and cfg["auto_update"] and datetime.datetime.now().hour == 4:
            try:
                update_installieren(info)
            except Exception as e:
                print(time.strftime("%H:%M:%S"), "Update fehlgeschlagen, alte Fassung läuft weiter:", repr(e), flush=True)
                naechste, zustand["update"] = time.time() + 6 * 3600, None
        time.sleep(300)


def beenden():
    """Beendet das Tool. Als LaunchAgent wird der Dienst abgemeldet, sonst startet launchd es sofort neu.
    Bei der nächsten Anmeldung startet es wieder."""
    time.sleep(0.5)
    import os, subprocess
    if os.environ.get("XPC_SERVICE_NAME", "").endswith("talkback"):
        subprocess.run(["/bin/launchctl", "bootout", f"gui/{os.getuid()}/{os.environ['XPC_SERVICE_NAME']}"])
    os._exit(0)


# ---------- Web ----------

class Web(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def antwort(self, body, typ="application/json", code=200):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", typ + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/zustand":
            with lock:
                z = dict(zustand, ziele=[z[1] for z in ZIELE], keys=[z[0] for z in ZIELE], auto_update=cfg["auto_update"], pult_ip=cfg["pult_ip"],
                         pausiert=cfg["pausiert"], mono_aux_anzahl=cfg["mono_aux_anzahl"],
                         gruppen=[dict(g, indizes=mixe_von(g["name"])) for g in cfg["gruppen"]])
            return self.antwort(json.dumps(z))
        if self.path == "/suche":
            try:
                import suche
                return self.antwort(json.dumps(suche.suchen()))
            except ImportError:
                return self.antwort('"Suche fehlt, Update läuft"', code=503)
        if self.path == "/einstellungen.json":
            return self.antwort(json.dumps(dict(cfg, profile=profile())))
        if self.path == "/branding.json":
            return self.antwort(json.dumps(branding()))
        datei = {"/": "index.html", "/einstellungen": "einstellungen.html"}.get(self.path, self.path.lstrip("/"))
        p = (ORDNER / datei).resolve()
        typen = {".html": "text/html", ".svg": "image/svg+xml", ".css": "text/css", ".js": "text/javascript"}
        if p.parent != ORDNER or p.suffix not in typen or p.name in ("talkback.py",) or not p.exists():
            return self.antwort("nicht gefunden", "text/plain", 404)
        self.antwort(p.read_bytes(), typen[p.suffix])

    def do_POST(self):
        try:
            daten = json.loads(self.rfile.read(int(self.headers["Content-Length"])) or "null")
        except ValueError:
            return self.antwort('"kein gültiges JSON"', code=400)
        if self.path == "/setzen":
            ok = setzen(daten["an"])
            return self.antwort(json.dumps(ok), code=200 if ok else 503)
        if self.path == "/gruppe":
            with lock:
                an = not zustand["gruppen_an"].get(daten["name"], True)
            ok = gruppe_schalten(daten["name"], an)
            return self.antwort(json.dumps(ok), code=200 if ok else 503)
        if self.path == "/gruppe-mixe":  # Zahnrad auf der Hauptseite
            neu = json.loads(json.dumps(cfg))
            for g in neu["gruppen"]:
                if g["name"] == daten["name"]:
                    g["mixe"] = [ZIELE[i][0] for i in daten["indizes"] if 0 <= i < len(ZIELE)]
            speichern(neu)
            return self.antwort("true")
        if self.path == "/pause":  # Knopf „Pause“ / „Fortsetzen“
            speichern(dict(cfg, pausiert=bool(daten.get("an"))))
            return self.antwort("true")
        if self.path == "/beenden":  # Knopf „Beenden“: bis zur nächsten Anmeldung aus
            self.antwort("true")
            threading.Thread(target=beenden, daemon=True).start()
            return
        if self.path == "/update-pruefen":  # Knopf „Nach Updates suchen“
            try:
                import aktualisieren
                v, url, text = aktualisieren.neueste()
                neu = {"version": v, "url": url, "text": text[:2000]} if aktualisieren.version_tupel(v) > aktualisieren.version_tupel(VERSION) else None
                with lock:
                    zustand["update"] = neu
                return self.antwort(json.dumps(neu))
            except Exception as e:
                return self.antwort(json.dumps(str(e)), code=502)
        if self.path == "/update":  # Knopf „jetzt installieren“
            info = zustand["update"]
            if not info:
                return self.antwort('"kein Update verfügbar"', code=400)
            self.antwort("true")
            def los():
                try:
                    update_installieren(info)
                except Exception as e:
                    print(time.strftime("%H:%M:%S"), "Update fehlgeschlagen, alte Fassung läuft weiter:", repr(e), flush=True)
            threading.Thread(target=los, daemon=True).start()
            return
        if self.path == "/einstellungen":
            try:
                speichern(daten)
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                return self.antwort(json.dumps(str(e)), code=400)
            return self.antwort("true")
        self.antwort("nicht gefunden", "text/plain", 404)


if __name__ == "__main__":
    anwenden(cfg, False)
    threading.Thread(target=nativ, daemon=True).start()
    threading.Thread(target=udp_lebenszeichen, daemon=True).start()
    threading.Thread(target=midi, daemon=True).start()
    threading.Thread(target=led_abgleich, daemon=True).start()
    threading.Thread(target=update_wache, daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", WEB), Web)  # nur am Rechner selbst erreichbar
    print(f"Talkback läuft → http://localhost:{WEB}")
    marke = ORDNER / ".nach-update"
    if marke.exists() or "--kein-browser" in sys.argv:
        marke.unlink(missing_ok=True)
    else:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{WEB}")).start()
    server.serve_forever()
