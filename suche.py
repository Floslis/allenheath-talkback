"""Pult im Netz finden.
1. Zuhören: Avantis-Pulte rufen ~1,5× pro Sekunde per UDP-Broadcast auf Port 51319
   „AH_UFV2 Bridge Find Avantis Console {"V":["2","0","1"], ...}“ – mit Modell und Firmware.
2. Notfall: hört man nichts (anderes VLAN, Broadcast gefiltert), das eigene Netz nach TCP 51321 absuchen."""
import ipaddress, json, re, socket, subprocess, threading, time

RUF_PORT = 51319
STEUER_PORT = 51321


def zuhoeren(sekunden=4):
    """→ {ip: {"modell": …, "firmware": …}} aus den Broadcasts der Pulte."""
    gefunden = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):  # damit Director/Mixing Station parallel lauschen können
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    try:
        s.bind(("", RUF_PORT))
    except OSError:
        return gefunden
    s.settimeout(0.5)
    ende = time.time() + sekunden
    while time.time() < ende:
        try:
            daten, (ip, _) = s.recvfrom(2048)
        except socket.timeout:
            continue
        if not daten.startswith(b"AH_UF"):
            continue
        teile = daten.split(b"\x00")
        modell = next((t.decode("latin1") for t in teile if b"Avantis" in t or b"dLive" in t or b"SQ" in t), "Allen & Heath")
        firmware = ""
        m = re.search(rb"\{.*\}", daten)
        if m:
            try:
                firmware = ".".join(json.loads(m.group()).get("V", []))
            except ValueError:
                pass
        gefunden[ip] = {"ip": ip, "modell": modell, "firmware": firmware, "weg": "Ruf"}
    s.close()
    return gefunden


def eigene_netze():
    """IPv4-Netze der eigenen Schnittstellen (macOS ifconfig), höchstens /22 groß."""
    netze = []
    try:
        aus = subprocess.run(["/sbin/ifconfig"], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return netze
    for ip, maske in re.findall(r"inet (\d+\.\d+\.\d+\.\d+) netmask (0x[0-9a-f]+)", aus):
        if ip.startswith("127.") or ip.startswith("169.254."):
            continue
        laenge = bin(int(maske, 16)).count("1")
        netz = ipaddress.ip_network(f"{ip}/{max(laenge, 22)}", strict=False)
        if netz not in netze:
            netze.append(netz)
    return netze


def absuchen(netze=None, timeout=0.6):
    """→ {ip: {...}} aller Geräte im eigenen Netz, die TCP 51321 annehmen."""
    gefunden, lock = {}, threading.Lock()
    hosts = [str(h) for n in (netze or eigene_netze()) for h in n.hosts()]

    def pruefen(ip):
        try:
            with socket.create_connection((ip, STEUER_PORT), timeout=timeout):
                with lock:
                    gefunden[ip] = {"ip": ip, "modell": "Allen & Heath (Port 51321 offen)", "firmware": "", "weg": "Suche"}
        except OSError:
            pass

    for start in range(0, len(hosts), 128):
        threads = [threading.Thread(target=pruefen, args=(ip,), daemon=True) for ip in hosts[start:start + 128]]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    return gefunden


def suchen():
    """Erst zuhören, nur wenn nichts kommt, das Netz absuchen. → Liste, Avantis zuerst."""
    gefunden = zuhoeren()
    if not gefunden:
        gefunden = absuchen()
    return sorted(gefunden.values(), key=lambda g: ("Avantis" not in g["modell"], g["ip"]))
