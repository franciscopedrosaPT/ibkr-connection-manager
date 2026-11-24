"""Arranca o monitor.

Uso:  python scripts/run_monitor.py            # loop contínuo
      python scripts/run_monitor.py --once     # uma verificação e mostra o estado
      python scripts/run_monitor.py --check    # só valida o registo de client IDs
"""
from __future__ import annotations

import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from icm import __version__, monitor, registry  # noqa: E402


def main() -> None:
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    (ROOT / "logs").mkdir(exist_ok=True)
    h = RotatingFileHandler(ROOT / "logs" / "monitor.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[h, logging.StreamHandler()],
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("ib_insync").setLevel(logging.WARNING)
    logging.getLogger(__name__).info("IBKR Connection Manager versão %s", __version__)
    if a.check:
        reg = registry.load()
        issues = monitor.startup_checks(reg)
        print("Registo OK — sem conflitos." if not issues else "\n".join(issues))
        for b in reg.bots:
            print(f"  {b.endpoint:10s} {str(b.client_ids):18s} {b.name}")
        return
    monitor.run(once=a.once)


if __name__ == "__main__":
    main()
