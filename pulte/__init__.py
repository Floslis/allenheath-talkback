"""Pult-Treiber. Neues Pult: Datei pulte/<name>.py mit einer Unterklasse von basis.Treiber, dann hier eintragen."""
from .avantis import Avantis

TREIBER = {
    "avantis": Avantis,
}
