"""Updates von GitHub: prüft das neueste Release und tauscht nur die Code-Dateien.
Einstellungen (einstellungen.json) und eigene Branding-Profile bleiben unangetastet."""
import io, json, os, py_compile, shutil, ssl, sys, tempfile, time, urllib.request, zipfile
from pathlib import Path

REPO = "Floslis/avantis-talkback"
ORDNER = Path(__file__).resolve().parent
SICHERUNG = ORDNER / ".sicherung"
# Alles aus dem Release wird übernommen, außer dem, was dem Nutzer gehört
BEHALTEN = ("einstellungen.json", ".sicherung/", ".nach-update", ".reparatur-", "talkback.log")
BRANDING_MIT = ("branding/standard/", "branding/beispiel/")  # andere Profile in branding/ sind eigene


def version_tupel(v):
    return tuple(int(x) for x in v.lstrip("v").split(".") if x.isdigit())


def abrufen(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "avantis-talkback", "Accept": "application/vnd.github+json"})
    try:
        return urllib.request.urlopen(req, timeout=timeout).read()
    except ssl.SSLError:
        # manche Python-Installationen kennen die Zertifikate des Systems nicht
        import subprocess
        return subprocess.run(["/usr/bin/curl", "-fsSL", "-H", "User-Agent: avantis-talkback", url],
                              capture_output=True, check=True, timeout=timeout).stdout


def neueste():
    """→ (Version, Zip-URL, Beschreibung) des neuesten Releases."""
    r = json.loads(abrufen(f"https://api.github.com/repos/{REPO}/releases/latest"))
    return r["tag_name"].lstrip("v"), r["zipball_url"], r.get("body") or ""


def betrifft(name):
    if name.startswith(BEHALTEN) or name.startswith(".github/"):
        return False
    if name.startswith("branding/"):
        return name.startswith(BRANDING_MIT)
    return True


def installieren(zip_url):
    """Lädt das Release, prüft den Code und tauscht die Dateien. Wirft bei jedem Fehler, ohne etwas zu ändern."""
    daten = zipfile.ZipFile(io.BytesIO(abrufen(zip_url, timeout=60)))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        dateien = []
        for info in daten.infolist():
            teile = info.filename.split("/", 1)  # erster Ordner ist „Floslis-avantis-talkback-<sha>“
            if len(teile) < 2 or not teile[1] or info.is_dir():
                continue
            name = teile[1]
            if ".." in name.split("/") or name.startswith("/") or not betrifft(name):
                continue
            ziel = tmp / name
            ziel.parent.mkdir(parents=True, exist_ok=True)
            ziel.write_bytes(daten.read(info))
            dateien.append(name)
        if "talkback.py" not in dateien:
            raise RuntimeError("Release enthält kein talkback.py")
        for py in ("talkback.py", "aktualisieren.py"):
            if (tmp / py).exists():
                py_compile.compile(str(tmp / py), doraise=True)
        # Sicherung der aktuellen Fassung, dann tauschen
        if SICHERUNG.exists():
            shutil.rmtree(SICHERUNG)
        for name in dateien:
            alt = ORDNER / name
            if alt.exists():
                (SICHERUNG / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(alt, SICHERUNG / name)
        for name in dateien:
            (ORDNER / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(tmp / name, ORDNER / name)
            if name.endswith((".command", ".py")):
                os.chmod(ORDNER / name, 0o755)
    return dateien


def neu_starten():
    """Läuft das Tool als LaunchAgent, startet launchd es neu. Sonst sich selbst neu starten."""
    time.sleep(1)
    if os.environ.get("XPC_SERVICE_NAME", "").endswith("talkback"):
        os._exit(0)
    os.execv(sys.executable, [sys.executable, str(ORDNER / "talkback.py"), "--kein-browser"])
