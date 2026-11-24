"""Verificações de saúde de um endpoint IBKR (TWS / IB Gateway). Só leitura: nunca envia ordens."""
from __future__ import annotations

import socket
from dataclasses import dataclass


@dataclass
class ProbeResult:
    tcp: bool
    api: bool | None = None     # None = não verificado neste ciclo
    detail: str = ""


def tcp_ok(host: str, port: int, timeout: float = 3.0) -> bool:
    """Porta da API aberta? (TWS/IBG fechado ou no ecrã de login → porta fechada)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def api_ok(host: str, port: int, client_id: int, timeout: float = 10.0) -> tuple[bool, str]:
    """Handshake da API + reqCurrentTime: confirma que a sessão responde. readonly=True."""
    try:
        from ib_insync import IB
    except Exception as exc:  # pragma: no cover
        return False, f"ib_insync indisponível: {exc}"
    ib = IB()
    try:
        ib.connect(host, port, clientId=client_id, timeout=timeout, readonly=True)
        t = ib.reqCurrentTime()
        accts = ib.managedAccounts()
        return True, f"hora servidor {t:%H:%M:%S} UTC, {len(accts)} conta(s)"
    except Exception as exc:
        msg = str(exc) or type(exc).__name__
        if "326" in msg or "already in use" in msg.lower():
            return False, f"client ID {client_id} do monitor já em uso"
        return False, msg[:160]
    finally:
        try:
            ib.disconnect()
        except Exception:
            pass


def probe(host: str, port: int, client_id: int, with_api: bool) -> ProbeResult:
    if not tcp_ok(host, port):
        return ProbeResult(tcp=False, detail="porta fechada (TWS/IBG fechado ou à espera de login)")
    if not with_api:
        return ProbeResult(tcp=True)
    ok, det = api_ok(host, port, client_id)
    return ProbeResult(tcp=True, api=ok, detail=det)
