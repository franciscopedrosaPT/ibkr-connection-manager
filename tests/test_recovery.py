import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from icm import recovery  # noqa: E402


def _rec(monkeypatch, procs):
    launched, msgs = [], []
    monkeypatch.setattr(recovery, "launch", lambda cmd: launched.append(cmd))
    monkeypatch.setattr(recovery, "find_procs", lambda m: list(procs))
    monkeypatch.setattr(recovery, "kill", lambda p: len(p))
    monkeypatch.setattr(recovery.time, "sleep", lambda s: None)
    r = recovery.Recoverer("IBG paper (4002)", {"cmd": r"C:\IBC\StartGateway.bat", "stuck_min": 10, "wait_min": 5}, 3)
    return r, launched, msgs


def test_arranca_quando_nao_ha_processo(monkeypatch):
    r, launched, msgs = _rec(monkeypatch, [])
    assert r.step(120, msgs.append) == "arranque IBC" and len(launched) == 1


def test_espera_entre_tentativas(monkeypatch):
    r, launched, msgs = _rec(monkeypatch, [])
    r.step(120, msgs.append)
    assert r.step(180, msgs.append) is None and len(launched) == 1


def test_processo_aberto_aguarda_e_depois_reinicia(monkeypatch):
    r, launched, msgs = _rec(monkeypatch, ["p"])
    assert "a aguardar" in r.step(120, msgs.append) and not launched
    assert r.step(700, msgs.append) == "arranque IBC" and len(launched) == 1


def test_limite_por_hora(monkeypatch):
    r, launched, msgs = _rec(monkeypatch, [])
    for _ in range(3):
        r.last = 0
        r.step(120, msgs.append)
    r.last = 0
    assert r.step(120, msgs.append) == "limite de tentativas" and len(launched) == 3
    assert any("intervenção manual" in m for m in msgs)
