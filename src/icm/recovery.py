"""Fase 2 (v0.2.0): recuperação automática de um endpoint via IBC.

Regras de segurança:
- só endpoints com `recover:` no registry.yaml (hoje: só o IB Gateway PAPER);
- nunca dentro das janelas de manutenção; nunca se existir o ficheiro data/PAUSE_RECOVERY;
- máximo `max_per_hour` tentativas por hora; depois avisa e pára até à hora seguinte;
- se o processo do IBG já existe mas a porta está fechada há ≥ `stuck_min` minutos (ex. preso num diálogo),
  termina ESSE processo (só o que corresponde a `process_match`, nunca o TWS live) e volta a arrancar.
O script do IBC (credenciais no config do IBC, fora deste repositório) é que faz o login.
"""
from __future__ import annotations

import logging
import subprocess
import time
from collections import deque
from pathlib import Path

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]
PAUSE = ROOT / "data" / "PAUSE_RECOVERY"


def paused() -> bool:
    return PAUSE.exists()


def find_procs(match: str) -> list:
    """Processos (java/ibgateway) cuja linha de comando contém `match` (sem maiúsculas)."""
    try:
        import psutil
    except Exception:  # pragma: no cover
        logger.warning("psutil indisponível — não consigo ver processos")
        return []
    out = []
    m = match.lower()
    for p in psutil.process_iter(["name", "cmdline", "exe"]):
        try:
            txt = " ".join(p.info.get("cmdline") or []) + " " + str(p.info.get("exe") or "")
            if m in txt.lower() and "tws.exe" not in txt.lower():
                out.append(p)
        except Exception:
            continue
    return out


def kill(procs: list) -> int:
    n = 0
    for p in procs:
        try:
            for c in p.children(recursive=True):
                c.kill()
            p.kill()
            n += 1
        except Exception as exc:
            logger.warning("não consegui terminar o processo %s: %s", getattr(p, "pid", "?"), exc)
    return n


def launch(cmd: str) -> None:
    """Arranca o script do IBC numa consola própria (o IBC fica a correr nessa janela)."""
    CREATE_NEW_CONSOLE = 0x00000010
    subprocess.Popen(["cmd.exe", "/c", cmd], cwd=str(Path(cmd).parent),
                     creationflags=CREATE_NEW_CONSOLE, close_fds=True)


class Recoverer:
    def __init__(self, name: str, cfg: dict, max_per_hour: int = 3):
        self.name = name
        self.cmd = cfg["cmd"]
        self.match = cfg.get("process_match", "ibgateway")
        self.stuck_s = 60 * int(cfg.get("stuck_min", 10))
        self.wait_s = 60 * int(cfg.get("wait_min", 5))
        self.max_per_hour = max_per_hour
        self.attempts: deque[float] = deque()
        self.last = 0.0
        self.gave_up_hour: int | None = None

    def step(self, down_for_s: float, notify) -> str | None:
        """Chamado a cada ciclo enquanto o endpoint está em baixo. Devolve o que fez (para o log)."""
        now = time.time()
        while self.attempts and now - self.attempts[0] > 3600:
            self.attempts.popleft()
        if now - self.last < self.wait_s:
            return None  # ainda a dar tempo à tentativa anterior (login IBC demora 1–3 min)
        if len(self.attempts) >= self.max_per_hour:
            h = int(now // 3600)
            if self.gave_up_hour != h:
                self.gave_up_hour = h
                notify(f"❌ Recuperação automática de {self.name}: {self.max_per_hour} tentativas na última hora "
                       f"sem sucesso — preciso de intervenção manual (ver C:\\IBC\\Logs).")
            return "limite de tentativas"
        procs = find_procs(self.match)
        if procs and down_for_s < self.stuck_s:
            return f"processo existe ({len(procs)}), porta fechada há {down_for_s / 60:.0f} min — a aguardar"
        if procs:
            n = kill(procs)
            notify(f"🔧 {self.name}: aberto mas sem responder há {down_for_s / 60:.0f} min — terminei {n} "
                   f"processo(s) e vou arrancar de novo via IBC.")
            time.sleep(5)
        self.attempts.append(now)
        self.last = now
        launch(self.cmd)
        notify(f"🔧 {self.name} em baixo — a arrancar via IBC (tentativa {len(self.attempts)}/{self.max_per_hour} "
               f"nesta hora). Aviso quando voltar a responder.")
        return "arranque IBC"
