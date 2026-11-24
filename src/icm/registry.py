"""Registo único de ligações IBKR: carregar, validar conflitos e confirmar a configuração real dos bots."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Endpoint:
    name: str
    host: str
    port: int
    kind: str
    account: str
    critical: bool = True
    recover: dict | None = None   # v0.2.0: {cmd, process_match, stuck_min, wait_min}


@dataclass
class Bot:
    name: str
    project: str
    endpoint: str
    client_ids: list[int]
    config_check: dict | None = None


@dataclass
class Registry:
    endpoints: dict[str, Endpoint]
    bots: list[Bot]
    monitor: dict = field(default_factory=dict)


def load(path: Path | None = None) -> Registry:
    p = path or ROOT / "config" / "registry.yaml"
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    eps = {k: Endpoint(name=k, **v) for k, v in (d.get("endpoints") or {}).items()}
    bots = [Bot(**b) for b in (d.get("bots") or [])]
    return Registry(endpoints=eps, bots=bots, monitor=d.get("monitor") or {})


def conflicts(reg: Registry) -> list[str]:
    """Client IDs atribuídos a mais de um bot no MESMO endpoint ('any' colide com todos)."""
    out = []
    seen: dict[tuple[str, int], str] = {}
    for b in reg.bots:
        if b.endpoint != "any" and b.endpoint not in reg.endpoints:
            out.append(f"{b.name}: endpoint desconhecido '{b.endpoint}'")
        targets = list(reg.endpoints) if b.endpoint == "any" else [b.endpoint]
        for cid in b.client_ids:
            for ep in targets:
                k = (ep, int(cid))
                if k in seen and seen[k] != b.name:
                    out.append(f"client ID {cid} em {ep}: '{seen[k]}' e '{b.name}'")
                seen.setdefault(k, b.name)
    return sorted(set(out))


def _read_value(file: Path, key: str) -> str | None:
    """Lê KEY=valor (.env) ou `key: valor` (yaml simples). Nunca devolve linhas que pareçam segredos."""
    if any(s in key.lower() for s in ("pass", "token", "secret", "key_")):
        return None
    txt = file.read_text(encoding="utf-8", errors="replace")
    for ln in txt.splitlines():
        s = ln.split("#", 1)[0].strip()
        m = re.match(rf"^{re.escape(key)}\s*[=:]\s*(.+)$", s)
        if m:
            return m.group(1).strip().strip('"').strip("'")
    return None


def config_mismatches(reg: Registry) -> list[str]:
    """Confirma que o CID configurado em cada bot está dentro da faixa registada."""
    out = []
    for b in reg.bots:
        cc = b.config_check
        if not cc:
            continue
        f = (ROOT / cc["file"]).resolve()
        if not f.exists():
            out.append(f"{b.name}: ficheiro de configuração não encontrado ({cc['file']})")
            continue
        try:
            v = _read_value(f, cc["key"])
        except Exception as exc:
            out.append(f"{b.name}: não foi possível ler {cc['file']} ({type(exc).__name__})")
            continue
        if v is None:
            out.append(f"{b.name}: '{cc['key']}' não encontrado em {cc['file']}")
            continue
        try:
            cid = int(v)
        except ValueError:
            out.append(f"{b.name}: '{cc['key']}' não é um número ({v!r})")
            continue
        if cid not in b.client_ids:
            out.append(f"{b.name}: {cc['key']}={cid} fora da faixa registada {b.client_ids}")
    return out
