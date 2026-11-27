"""IBKR Connection Manager — monitor e (Fase 2) recuperação do TWS / IB Gateway partilhados pelos bots."""
from pathlib import Path

try:
    __version__ = (Path(__file__).resolve().parents[2] / "VERSION").read_text(encoding="utf-8").splitlines()[0].strip()
except Exception:  # pragma: no cover
    __version__ = "0.3.1"
