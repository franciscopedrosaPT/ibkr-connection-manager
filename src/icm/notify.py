"""Telegram (mesmo bot/grupo dos outros projectos). Credenciais só no .env deste projecto (fora do Git)."""
from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]


def _load_env() -> None:
    f = ROOT / ".env"
    if not f.exists():
        return
    for ln in f.read_text(encoding="utf-8", errors="replace").splitlines():
        s = ln.split("#", 1)[0].strip()
        if "=" in s:
            k, v = s.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def send(text: str) -> bool:
    _load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chats = [c for c in (os.environ.get("TELEGRAM_CHAT_ID", ""), os.environ.get("TELEGRAM_GROUP_CHAT_ID", "")) if c]
    if not token or not chats:
        logger.info("Telegram não configurado — mensagem só no log")
        return False
    import requests
    ok = True
    for cid in chats:
        try:
            r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                              json={"chat_id": cid, "text": text[:4000], "disable_web_page_preview": True},
                              timeout=15)
            ok &= r.status_code == 200
        except Exception as exc:  # nunca registar o token
            logger.warning("Telegram falhou (%s)", type(exc).__name__)
            ok = False
    return ok
