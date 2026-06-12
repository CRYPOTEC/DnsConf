"""Minimal Telegram Bot API wrapper (long polling, no extra dependencies).

Supports two modes at once:
  • обычный чат с ботом (пользователь пишет боту напрямую);
  • Telegram Business — бот подключён к рабочему аккаунту (Premium) и отвечает
    в личных чатах этого аккаунта (updates типа business_message,
    отправка с business_connection_id).
"""
from __future__ import annotations

import json

import requests

# Without business_message in allowed_updates Telegram won't deliver
# messages from connected business accounts.
ALLOWED_UPDATES = json.dumps(["message", "business_message"])


class TelegramAPI:
    def __init__(self, token: str):
        self.base = f"https://api.telegram.org/bot{token}"

    def get_updates(self, offset: int | None = None, timeout: int = 50) -> list[dict]:
        resp = requests.get(
            f"{self.base}/getUpdates",
            params={"offset": offset, "timeout": timeout, "allowed_updates": ALLOWED_UPDATES},
            timeout=timeout + 10,
        )
        resp.raise_for_status()
        return resp.json().get("result", [])

    def send_message(
        self, chat_id: str | int, text: str, business_connection_id: str | None = None
    ) -> None:
        # Telegram caps messages at 4096 chars.
        payload: dict = {"chat_id": chat_id, "text": text[:4096]}
        if business_connection_id:
            payload["business_connection_id"] = business_connection_id
        requests.post(f"{self.base}/sendMessage", json=payload, timeout=30)

    def get_me(self) -> dict:
        resp = requests.get(f"{self.base}/getMe", timeout=30)
        resp.raise_for_status()
        return resp.json().get("result", {})
