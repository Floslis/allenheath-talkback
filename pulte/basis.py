"""Schnittstelle für Pult-Treiber.

Ein Treiber kennt nur das Pult: Verbindung, Protokoll, welche Mixe es gibt. Gruppen, Softkey-Logik,
Einstellungen und Oberfläche liegen in talkback.py und sind für alle Pulte gleich.

Der Treiber meldet alles, was er vom Pult erfährt, über das Melder-Objekt zurück (siehe Melder).
Ziele (Mixe) heißen überall gleich: ein kurzer Schlüssel wie „aux3“ oder „staux1“, den der Treiber festlegt.
"""


class Melder:
    """Was talkback.py vom Treiber erfährt. Alle Aufrufe dürfen aus beliebigen Threads kommen."""

    def verbunden(self, ja: bool): ...
    def assign(self, ziel: str, an: bool): ...            # Zustand eines Ziels (Talkback-Kanal → Mix)
    def name(self, ziel: str, name: str): ...             # Name eines Mixes vom Pult
    def vorhanden(self, ziele: dict): ...                 # alle Mixe, die das Pult wirklich hat: Schlüssel → Name
    def mutegruppe(self, nr: int, gemutet: bool): ...     # Softkey hat eine Mute-Gruppe geschaltet
    def einstellung(self, **werte): ...                   # Treiber hat etwas über das Pult gelernt (z. B. mono_aux_anzahl)


class Treiber:
    """Basisklasse. Ein neues Pult = eine neue Datei in pulte/ mit einer Unterklasse und einem Eintrag in pulte/__init__.py."""

    name = "Pult"           # Anzeigename, z. B. „Allen & Heath Avantis“
    getestet = ""           # z. B. „Firmware V2.01“

    def __init__(self, cfg: dict, melder: Melder):
        self.cfg = cfg
        self.melder = melder

    @staticmethod
    def moegliche_ziele(cfg: dict) -> list:
        """Alle Ziele, die dieses Pult haben kann: Liste von (Schlüssel, Anzeige), z. B. ("aux3", "Aux 3")."""
        return []

    @staticmethod
    def suchen() -> list:
        """Pulte im Netz finden: Liste von {"ip", "modell", "firmware"}."""
        return []

    def start(self):
        """Verbindungen aufbauen (eigene Threads), danach laufend melden."""

    def anwenden(self, cfg: dict, ziele: list, neu_verbinden: bool):
        """Neue Einstellungen. ziele = Schlüssel in der Reihenfolge der Oberfläche.
        neu_verbinden: IP, Kanal o. ä. geändert oder Pause umgeschaltet → Verbindung neu aufbauen."""

    def bereit(self) -> bool:
        """Kann gerade geschaltet werden?"""
        return False

    def setzen(self, werte: dict) -> bool:
        """Assigns setzen: {Schlüssel: an/aus}. False, wenn nicht verbunden."""
        return False

    def mutegruppe_setzen(self, nr: int, gemutet: bool):
        """Mute-Gruppe setzen (für die Softkey-LED)."""
