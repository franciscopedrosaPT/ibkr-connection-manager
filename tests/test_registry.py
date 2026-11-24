import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from icm import monitor, registry  # noqa: E402
from datetime import datetime, timezone  # noqa: E402


def test_registry_sem_conflitos():
    assert registry.conflicts(registry.load()) == []


def test_conflito_detectado():
    reg = registry.load()
    reg.bots.append(registry.Bot(name="intruso", project="x", endpoint="tws_live", client_ids=[70]))
    assert any("70" in c for c in registry.conflicts(reg))


def test_any_colide_com_todos():
    reg = registry.load()
    reg.bots.append(registry.Bot(name="intruso", project="x", endpoint="ibg_paper", client_ids=[90]))
    assert registry.conflicts(reg)


def test_quiet_window():
    w = ["04:45-05:45"]
    assert monitor.in_quiet_window(datetime(2026, 11, 24, 5, 0, tzinfo=timezone.utc), w)
    assert not monitor.in_quiet_window(datetime(2026, 11, 24, 6, 0, tzinfo=timezone.utc), w)
    assert monitor.in_quiet_window(datetime(2026, 11, 24, 23, 30, tzinfo=timezone.utc), ["23:00-01:00"])
