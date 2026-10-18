"""Treiber für Allen & Heath Avantis (getestet mit Firmware V2.01 Rev. 97241).

Natives Protokoll (TCP 51321 + UDP) für Assign und Zustand, aus Mitschnitten von Mixing Station nachgebaut.
MIDI über TCP (51325, offiziell dokumentiert) für Mix-Namen und Mute-Gruppen.
Protokoll-Notizen stehen im README unter „How it works“."""
import re, socket, threading, time

from .basis import Treiber

TAG = b"\x01\xf4"
# alle Mixe, die ein Avantis haben kann: (Schlüssel, Anzeige, MIDI-Nummer für den Namen)
ALLE_MIXE = [(f"aux{i}", f"Aux {i}", i - 1) for i in range(1, 25)] + \
            [(f"staux{i}", f"StAux {i}", 0x40 + i - 1) for i in range(1, 13)]
MIDI_NR = {k: nr for k, _, nr in ALLE_MIXE}


def nachrichten(buf):
    while (a := buf.find(b"\xf0")) >= 0 and (e := buf.find(b"\xf7", a)) >= 0:
        yield bytes(buf[a:e + 1])
        del buf[:e + 1]


def senden(s, h, prm, daten):
    s.sendall(b"\xf0\x00\x00" + h + TAG + prm.to_bytes(2, "big") + len(daten).to_bytes(2, "big") + daten + b"\xf7")


class Avantis(Treiber):
    name = "Allen & Heath Avantis"
    getestet = "Firmware V2.01"

    def __init__(self, cfg, melder):
        super().__init__(cfg, melder)
        self.lock = threading.Lock()
        self.sock = self.handle = self.udp = self.midi_sock = None
        self.ziele = []
        self.param_zu_ziel = {}
        self.antworten = {}  # MIDI-Nummer → (Name, Zeit) der letzten Namensantworten

    @staticmethod
    def moegliche_ziele(cfg):
        return [(k, a) for k, a, _ in ALLE_MIXE]

    @staticmethod
    def suchen():
        import suche
        return suche.suchen()

    # ---------- Einstellungen ----------

    def slot(self, key):
        """Platz eines Mixes im „Input Mixer“. Stereo-Aux liegen hinter den Mono-Aux und belegen je 2 Plätze.
        Bewiesen für 12 Mono-Aux; die Zahl zählt der Treiber selbst (mixe_auswerten)."""
        art, nr = re.fullmatch(r"(aux|staux)(\d+)", key).groups()
        nr = int(nr)
        return nr - 1 if art == "aux" else self.cfg["mono_aux_anzahl"] + (nr - 1) * 2

    def param(self, key):
        return 0x4550 + (self.cfg["talkback_kanal"] - 1) * 56 + self.slot(key)

    def midi_basis(self):
        return self.cfg["midi_kanal"] - 1

    def anwenden(self, cfg, ziele, neu_verbinden):
        with self.lock:
            self.cfg = cfg
            self.ziele = list(ziele)
            self.param_zu_ziel = {self.param(k): k for k in self.ziele}
            socks = [self.sock, self.midi_sock]
        if neu_verbinden:
            for s in socks:  # die Threads merken das und verbinden sich neu
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except (OSError, AttributeError):
                    pass

    def start(self):
        for ziel in (self.nativ, self.udp_lebenszeichen, self.midi):
            threading.Thread(target=ziel, daemon=True).start()

    def bereit(self):
        return bool(self.sock and self.handle)

    def setzen(self, werte):
        with self.lock:
            s, h = self.sock, self.handle
            if not s or not h:
                return False
            params = [(self.param(k), an) for k, an in werte.items()]
        for p, an in params:
            senden(s, h, p, bytes([1 if an else 0]))
        return True

    def mutegruppe_setzen(self, nr, gemutet):
        s = self.midi_sock
        if not s:
            return
        k, n = 0x90 | (self.midi_basis() + 4), 0x45 + nr  # Mute-Gruppe 1 = Note 0x46
        try:
            s.sendall(bytes([k, n, 0x7F if gemutet else 0x3F, k, n, 0]))
        except OSError:
            pass

    # ---------- natives Protokoll ----------

    def abonnieren(self, s, h):
        for p in list(self.param_zu_ziel):  # pro Parameter einzeln, wie Mixing Station
            senden(s, h, 0x0006, b"\x00\x00" + TAG + p.to_bytes(2, "big") * 2 + b"\x00\xff")

    def nativ(self):
        """Hält die Verbindung zum Pult, abonniert die Assigns und meldet den Zustand."""
        while True:
            s = u = None
            if self.cfg["pausiert"]:
                time.sleep(1)
                continue
            try:
                ip = self.cfg["pult_ip"]
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
                self.udp = {"sock": u, "ziel": None}
                with self.lock:
                    self.sock = s
                while True:
                    try:
                        d = s.recv(65536)
                    except socket.timeout:  # Funkstille ist normal, wenn sich am Pult nichts ändert
                        continue
                    if not d:
                        raise ConnectionError("Pult hat getrennt")
                    if self.udp["ziel"] is None and (k := (bytes(buf) + d).find(b"\xe0\x00\x04\x02\x03")) >= 0:
                        rest = (bytes(buf) + d)[k + 5:k + 7]
                        if len(rest) == 2:
                            self.udp["ziel"] = (ip, int.from_bytes(rest, "big"))
                    buf += d
                    for m in nachrichten(buf):
                        if h is None and m[1] == 0 and m[3:5] == TAG and m[5:11] == b"\x00\x00\x00\x02\x00\x02":
                            h = m[11:13]
                            self.abonnieren(s, h)
                            with self.lock:
                                self.handle = h
                            self.melder.verbunden(True)
                        elif h and len(m) == 13 and m[3:7] == TAG + h:
                            key = self.param_zu_ziel.get(int.from_bytes(m[7:9], "big"))
                            if key:
                                self.melder.assign(key, bool(m[11]))
            except OSError as e:
                print(time.strftime("%H:%M:%S"), "Pult-Verbindung weg:", repr(e), flush=True)
            with self.lock:
                self.sock = self.handle = self.udp = None
            self.melder.verbunden(False)
            for x in (s, u):
                try:
                    x.close()
                except (OSError, AttributeError):
                    pass
            time.sleep(3)

    def udp_lebenszeichen(self):
        """Jede Sekunde e0 00 01 03 e7 per UDP ans Pult (wie Mixing Station), Eingehendes verwerfen."""
        while True:
            udp = self.udp
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

    # ---------- MIDI über TCP ----------

    def midi(self):
        """Dauerverbindung MIDI/TCP: Mix-Namen (jede Minute) und die Mute-Gruppen der Softkeys."""
        while True:
            if self.cfg["pausiert"]:
                time.sleep(1)
                continue
            try:
                s = socket.create_connection((self.cfg["pult_ip"], 51325), timeout=5)
                with self.lock:
                    self.midi_sock = s
                s.settimeout(1)
                buf, naechste, lauf = bytearray(), 0, None
                while True:
                    if time.time() > naechste:
                        # alle möglichen Mixe abfragen: nur die vorhandenen antworten, so zählt der Treiber sie selbst
                        gefragt = time.time()
                        for _, _, nr in ALLE_MIXE:
                            s.sendall(bytes([0xF0, 0, 0, 0x1A, 0x50, 0x10, 1, 0, self.midi_basis() + 2, 0x01, nr, 0xF7]))
                        naechste = time.time() + 60
                        threading.Timer(3, self.mixe_auswerten, args=(gefragt,)).start()
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
                            self.midi_nachricht(bytes(buf)); buf = bytearray()
                        elif buf[0] != 0xF0 and len(buf) == 3:
                            self.midi_nachricht(bytes(buf)); buf = bytearray()
            except OSError:
                pass
            with self.lock:
                self.midi_sock = None
            time.sleep(3)

    def midi_nachricht(self, m):
        if m[0] == 0xF0 and len(m) > 11 and m[9] == 0x02:  # Name
            name = m[11:-1].split(b"\x00")[0].decode("latin1").strip()
            self.antworten[m[10]] = (name, time.time())
            for k in self.ziele:
                if MIDI_NR.get(k) == m[10]:
                    self.melder.name(k, name)
        # Mute-Gruppen: Note On auf Kanal Basis+4, 7F = gemutet, 3F = nicht gemutet (danach ein 00 als Abschluss)
        elif m[0] == 0x90 | (self.midi_basis() + 4) and m[2] in (0x7F, 0x3F) and 0x46 <= m[1] < 0x46 + 24:
            self.melder.mutegruppe(m[1] - 0x45, m[2] == 0x7F)

    def mixe_auswerten(self, seit):
        """Nach einer Abfragerunde: welche Mixe gibt es, wie viele Mono-Aux?"""
        frisch = {nr: name for nr, (name, t) in list(self.antworten.items()) if t >= seit}
        if not frisch:
            return  # keine Antwort (Pult weg), nichts ändern
        self.melder.vorhanden({k: frisch[nr] for k, _, nr in ALLE_MIXE if nr in frisch})
        mono = sum(1 for nr in frisch if nr < 0x40)
        if mono != self.cfg["mono_aux_anzahl"]:
            print(time.strftime("%H:%M:%S"), f"Pult hat {mono} Mono-Aux, stelle um", flush=True)
            self.melder.einstellung(mono_aux_anzahl=mono)
