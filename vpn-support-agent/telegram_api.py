"""Minimal Telegram Bot API wrapper (long polling, no extra dependencies)."""
from __future__ import annotations

import requests


class TelegramAPI:
    def __init__(self, token: str):
        self.base = f"https://api.telegram.org/bot{token}"

    def get_updates(self, offset: int | None = None, timeout: int = 50) -> list[dict]:
        resp = requests.get(
            f"{self.base}/getUpdates",
            params={"offset": offset, "timeout": timeout},
            timeout=timeout + 10,
        )
        resp.raise_for_status()
        return resp.json().get("result", [])

    def send_message(self, chat_id: str | int, text: str) -> None:
        # Telegram caps messages at 4096 chars.
        requests.post(
            f"{self.base}/sendMessage",
            json={"chat_id": chat_id, "text": text[:4096]},
            timeout=30,
        )

    def get_me(self) -> dict:
        resp = requests.get(f"{self.base}/getMe", timeout=30)
        resp.raise_for_status()
        return resp.json().get("result", {})
