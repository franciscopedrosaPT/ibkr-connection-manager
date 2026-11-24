"""Monitor: estado do TWS live e do IB Gateway paper, alertas Telegram só em mudanças de estado.

v0.2.0 (Fase 2): endpoints com `recover:` no registry.yaml são levantados automaticamente via IBC
(src/icm/recovery.py). Hoje só o IB Gateway paper.
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from . import notify, probe, recovery, registry

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "data" / "state.json"


def in_quiet_window(now: datetime, windows: list[str]) -> bool:
    m = now.hour * 60 + now.minute
    for w in windows or []:
        a, b = w.split("-")
        ma = int(a[:2]) * 60 + int(a[3:5])
        mb = int(b[:2]) * 60 + int(b[3:5])
        if (ma <= m < mb) if ma <= mb else (m >= ma or m < mb):
            return True
    return False


def _save(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def startup_checks(reg: registry.Registry) -> list[str]:
    return registry.conflicts(reg) + registry.config_mismatches(reg)


def run(once: bool = False) -> None:
    reg = registry.load()
    mon = reg.monitor
    cid = int(mon.get("client_id", 90))
    interval = int(mon.get("interval_s", 60))
    api_every = max(1, int(mon.get("api_every_n", 5)))
    need = 1 if once else max(1, int(mon.get("down_after_failures", 2)))
    quiet = mon.get("quiet_windows_utc") or []

    issues = startup_checks(reg)
    from . import __version__
    head = f"🔌 IBKR Connection Manager v{__version__} — arranque"
    if issues:
        notify.send(head + "\n⚠️ Registo de ligações:\n" + "\n".join(f"• {x}" for x in issues))
    else:
        logger.info("%s: registo OK (%d bots, sem conflitos)", head, len(reg.bots))

    st = {k: {"up": None, "fails": 0, "since": None, "detail": ""} for k in reg.endpoints}
    rcfg = mon.get("recovery") or {}
    recs = {k: recovery.Recoverer(f"{ep.kind} {ep.account} ({ep.port})", ep.recover,
                                  int(rcfg.get("max_per_hour", 3)))
            for k, ep in reg.endpoints.items() if ep.recover and rcfg.get("enabled", False)}
    if recs:
        logger.info("Recuperação automática activa para: %s", ", ".join(recs))
    n = 0
    while True:
        n += 1
        now = datetime.now(timezone.utc)
        for name, ep in reg.endpoints.items():
            r = probe.probe(ep.host, ep.port, cid, with_api=(n % api_every == 1 or once))
            ok = r.tcp and (r.api is not False)
            s = st[name]
            s["fails"] = 0 if ok else s["fails"] + 1
            s["detail"] = r.detail
            s["checked"] = now.isoformat(timespec="seconds")
            lab = f"{ep.kind} {ep.account} ({ep.port})"
            if ok and s["up"] is not True:
                if s["up"] is False:
                    _rec = recs.get(name)
                    _auto = " (recuperado automaticamente via IBC)" if _rec and _rec.last and \
                        time.time() - _rec.last < 1800 else ""
                    notify.send(f"✅ {lab} voltou a responder{_auto}. {r.detail}".strip())
                logger.info("%s UP %s", lab, r.detail)
                s["up"], s["since"] = True, now.isoformat(timespec="seconds")
            elif not ok and s["fails"] >= need and s["up"] is not False:
                s["up"], s["since"] = False, now.isoformat(timespec="seconds")
                if in_quiet_window(now, quiet):
                    logger.info("%s DOWN dentro da janela de manutenção — sem alerta (%s)", lab, r.detail)
                elif ep.critical:
                    notify.send(f"🔴 {lab} EM BAIXO: {r.detail}\n"
                                f"Bots afectados: " + ", ".join(
                                    b.name for b in reg.bots if b.endpoint in (name, "any")) +
                                ("\nRecuperação automática via IBC activa." if name in recs else
                                 "\nSem recuperação automática para este endpoint — reinicia à mão."))
                else:
                    logger.info("%s em baixo (não crítico): %s", lab, r.detail)
            # v0.2.0: enquanto estiver em baixo, tenta recuperar (fora da manutenção e sem pausa)
            if not ok and s["up"] is False and name in recs and not once:
                if in_quiet_window(now, quiet):
                    pass
                elif recovery.paused():
                    logger.info("%s em baixo — recuperação em pausa (data/PAUSE_RECOVERY)", lab)
                else:
                    _since = datetime.fromisoformat(s["since"])
                    _act = recs[name].step((now - _since).total_seconds(), notify.send)
                    if _act:
                        logger.info("recuperação %s: %s", lab, _act)
        _save({"ts": now.isoformat(timespec="seconds"), "endpoints": st})
        if once:
            for name, s in st.items():
                print(f"{name:10s} {'UP' if s['up'] else 'DOWN' if s['up'] is False else '?':5s} {s['detail']}")
            return
        time.sleep(interval)

