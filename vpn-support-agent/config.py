"""Configuration loaded from environment / .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader so we don't need an extra dependency."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass
class Config:
    anthropic_api_key: str
    anthropic_model: str
    telegram_bot_token: str
    telegram_admin_chat_id: str
    composio_api_key: str
    composio_user_id: str
    google_sheet_id: str
    google_sheet_name: str

    @property
    def admin_notifications_enabled(self) -> bool:
        return bool(self.telegram_admin_chat_id)

    @property
    def sheet_logging_enabled(self) -> bool:
        return bool(self.composio_api_key and self.google_sheet_id)


def load_config() -> Config:
    _load_dotenv()
    cfg = Config(
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        anthropic_model=os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5"),
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        telegram_admin_chat_id=os.environ.get("TELEGRAM_ADMIN_CHAT_ID", ""),
        composio_api_key=os.environ.get("COMPOSIO_API_KEY", ""),
        composio_user_id=os.environ.get("COMPOSIO_USER_ID", "vpn-admin"),
        google_sheet_id=os.environ.get("GOOGLE_SHEET_ID", ""),
        google_sheet_name=os.environ.get("GOOGLE_SHEET_NAME", "Жалобы"),
    )
    missing = []
    if not cfg.anthropic_api_key:
        missing.append("ANTHROPIC_API_KEY")
    if not cfg.telegram_bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if missing:
        raise SystemExit(
            "Не заданы обязательные переменные: " + ", ".join(missing)
            + "\nСкопируй .env.example в .env и заполни значения."
        )
    return cfg
