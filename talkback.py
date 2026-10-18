#!/usr/bin/env python3
"""Talkback: schaltet das Assign eines Talkback-Kanals auf In-Ear-Mixe, per Browser oder Softkey am Pult.
Hier liegt alles, was für jedes Pult gleich ist: Einstellungen, Gruppen, Softkey-Logik, Oberfläche, Updates.
Das Pult selbst steckt in einem Treiber in pulte/ (z. B. pulte/avantis.py).
Einstellungen in einstellungen.json, änderbar unter http://localhost:8787/einstellungen
Start: python3 talkback.py  → http://localhost:8787"""
import datetime, ipaddress, json, re, sys, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VERSION = "0.7.0"  # erhöhen → die GitHub-Action baut daraus ein Release, die Tools holen es sich
WEB = 8787
ORDNER = Path(__file__).resolve().parent
EINSTELLUNGEN = ORDNER / "einstellungen.json"
ALT_GRUPPEN = ORDNER / "gruppen.json"  # Format bis 18.10.2026, wird einmalig übernommen
BRANDING = ORDNER / "branding"  # je Profil ein Ordner mit profil.json und optional logo.svg
# Dateien, die ältere Updater noch nicht kannten. Fehlt eine, holt sich das Tool das Release einmal neu
PFLICHT = ["suche.py", "stream.css", "talkback.css", "oberflaeche.js", "pulte/__init__.py", "pulte/basis.py", "pulte/avantis.py"]


def selbstreparatur():
    marke = ORDNER / f".reparatur-{VERSION}"  # höchstens ein Versuch pro Version, keine Neustart-Schleife
    if any(not (ORDNER / d).exists() for d in PFLICHT) and not marke.exists():
        marke.write_text("1")
        import aktualisieren
        v, url, _ = aktualisieren.neueste()
        print(time.strftime("%H:%M:%S"), "Dateien fehlen, hole Version", v, "nochmal", flush=True)
        aktualisieren.installieren(url)
        (ORDNER / ".nach-update").write_text(v)
        aktualisieren.neu_starten()


try:
    from pulte import TREIBER
except ImportError:  # ein älterer Updater hat pulte/ nicht mitgebracht
    selbstreparatur()
    raise

STANDARD = {
    "branding": "standard",
    "auto_update": True,       # nachts um 4 Uhr installieren, nie während eines Gottesdienstes
    "pausiert": False,         # Pause: keine Verbindung zum Pult, bis jemand „Fortsetzen“ drückt
    "sprache": "auto",         # auto (folgt dem Browser), de, en
    "pult_typ": "avantis",     # Schlüssel in pulte/__init__.py
    "pult_ip": "192.168.1.50",
    "talkback_kanal": 87,
    "midi_kanal": 12,          # MIDI-Basiskanal am Pult (Setup → Control → MIDI)
    "mono_aux_anzahl": 12,     # zählt der Avantis-Treiber selbst
    "ziele": [f"aux{i}" for i in range(1, 10)] + [f"staux{i}" for i in range(1, 6)],
    "gruppen": [
        {"name": "Band", "rest": True, "mixe": [], "mutegruppe": 6},
        {"name": "MD", "rest": False, "mixe": [], "mutegruppe": 7},
        {"name": "Vicom", "rest": False, "mixe": [], "mutegruppe": 8},
    ],
}


# ---------- Einstellungen ----------

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
    if c["pult_typ"] not in TREIBER:
        c["pult_typ"] = "avantis"
    ipaddress.ip_address(c["pult_ip"])
    for feld, lo, hi in (("talkback_kanal", 1, 128), ("midi_kanal", 1, 12), ("mono_aux_anzahl", 0, 24)):
        c[feld] = int(c[feld])
        if not lo <= c[feld] <= hi:
            raise ValueError(f"{feld} muss zwischen {lo} und {hi} liegen")
    moeglich = {k for k, _ in TREIBER[c["pult_typ"]].moegliche_ziele(c)}
    c["ziele"] = [z for z in dict.fromkeys(c["ziele"]) if z in moeglich]
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
ZIELE = []  # (Schlüssel, Anzeige) in der Reihenfolge der Oberfläche
zustand = {"verbunden": False, "an": [], "namen": [], "gruppen_an": {}, "version": VERSION, "update": None,
           "vorhanden": {}}  # alle Mixe, die das Pult hat: Schlüssel → Name
mg_stand = {}  # Gruppe → zuletzt bekannter Zustand ihrer Softkey-LED (an = grün)
lock = threading.Lock()


class Melder:
    """Nimmt die Meldungen des Treibers entgegen (siehe pulte/basis.py) und schreibt sie in den Zustand."""

    def index(self, ziel):
        return next((i for i, z in enumerate(ZIELE) if z[0] == ziel), None)

    def verbunden(self, ja):
        with lock:
            zustand["verbunden"] = ja
            if not ja:
                zustand["an"] = [None] * len(ZIELE)

    def assign(self, ziel, an):
        with lock:
            i = self.index(ziel)
            if i is not None and i < len(zustand["an"]):
                zustand["an"][i] = an

    def name(self, ziel, name):
        with lock:
            i = self.index(ziel)
            if i is not None and i < len(zustand["namen"]):
                zustand["namen"][i] = name

    def vorhanden(self, ziele):
        with lock:
            zustand["vorhanden"] = ziele

    def mutegruppe(self, nr, gemutet):
        for g in cfg["gruppen"]:
            if g["mutegruppe"] == nr:
                softkey(g["name"], not gemutet)  # invertiert: Gruppe an = Mute-Gruppe aus (LED grün)

    def einstellung(self, **werte):
        speichern(dict(cfg, **werte))


treiber = TREIBER[cfg["pult_typ"]](cfg, Melder())


def anwenden(neu, neu_verbinden):
    """Neue Einstellungen übernehmen. Bei anderer IP, anderem Kanal oder Pause die Verbindung neu aufbauen."""
    global cfg, ZIELE
    with lock:
        cfg = neu
        beschriftung = dict(TREIBER[cfg["pult_typ"]].moegliche_ziele(cfg))
        ZIELE = [(k, beschriftung.get(k, k)) for k in cfg["ziele"]]
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
    treiber.anwenden(cfg, [z[0] for z in ZIELE], neu_verbinden)


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
            an, gruppen = list(zustand["an"]), list(cfg["gruppen"])
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
            if alt != ist and g["mutegruppe"]:
                treiber.mutegruppe_setzen(g["mutegruppe"], not ist)  # LED grün = Mute-Gruppe aus


def setzen(an):
    """an: Liste mit True/False je Ziel."""
    with lock:
        if not treiber.bereit() or len(an) != len(ZIELE):
            return False
        zustand["an"] = [bool(w) for w in an]  # auf einmal, damit der LED-Abgleich keinen halben Zustand sieht
        werte = {z[0]: bool(w) for z, w in zip(ZIELE, an)}
    return treiber.setzen(werte)


def speichern(neu):
    neu = pruefen(neu)
    if neu["pult_typ"] != cfg["pult_typ"]:  # anderes Pult → anderer Treiber, sauberster Weg ist ein Neustart
        EINSTELLUNGEN.write_text(json.dumps(neu, indent=2, ensure_ascii=False))
        import aktualisieren
        (ORDNER / ".nach-update").write_text("pult")
        threading.Thread(target=aktualisieren.neu_starten, daemon=True).start()
        return
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


def update_wache():
    """Prüft alle 6 h auf ein neues Release. Automatisch installiert wird nur zwischen 4 und 5 Uhr."""
    import aktualisieren
    naechste = 0
    try:
        selbstreparatur()
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
                         pult=treiber.name,
                         pausiert=cfg["pausiert"], mono_aux_anzahl=cfg["mono_aux_anzahl"],
                         gruppen=[dict(g, indizes=mixe_von(g["name"])) for g in cfg["gruppen"]])
            return self.antwort(json.dumps(z))
        if self.path == "/suche":
            try:
                return self.antwort(json.dumps(TREIBER[cfg["pult_typ"]].suchen()))
            except ImportError:
                return self.antwort('"Suche fehlt, Update läuft"', code=503)
        if self.path == "/einstellungen.json":
            return self.antwort(json.dumps(dict(cfg, profile=profile(),
                                                moegliche_ziele=TREIBER[cfg["pult_typ"]].moegliche_ziele(cfg),
                                                pult_typen={k: f"{v.name} ({v.getestet})" if v.getestet else v.name for k, v in TREIBER.items()})))
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
    treiber.start()
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
