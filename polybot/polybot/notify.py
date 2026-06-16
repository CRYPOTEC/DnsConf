"""Notifications — Telegram with a console fallback.

The bot announces what it does: opening a position (with reasoning + exit plan),
gain milestones, exits, resolutions, and periodic portfolio summaries.

Telegram is configured purely via environment variables (no secrets in config):
  TELEGRAM_BOT_TOKEN   from @BotFather
  TELEGRAM_CHAT_ID     your chat/channel id (see `polybot telegram-test`)

If those aren't set, messages go to the console so the bot still "talks".
Uses stdlib urllib (Telegram is a non-Anthropic API).
"""

from __future__ import annotations

import json
import os
import urllib.request


class ConsoleNotifier:
    name = "console"

    def send(self, text: str) -> None:
        print(f"  📣 {text}")


class NullNotifier:
    name = "null"

    def send(self, text: str) -> None:
        pass


class TelegramNotifier:
    name = "telegram"

    def __init__(self, token: str, chat_id: str, sender=None, timeout: float = 10.0):
        self.token = token
        self.chat_id = chat_id
        self.timeout = timeout
        self._sender = sender or self._http_send  # injectable for tests

    def _http_send(self, url: str, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            resp.read()

    def send(self, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        try:
            self._sender(url, payload)
        except Exception as exc:  # noqa: BLE001 - never let a notify failure crash the bot
            print(f"  ! telegram send failed: {exc}")


def build_notifier():
    """Telegram if both env vars are present, else console."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        return TelegramNotifier(token, chat)
    return ConsoleNotifier()


def discover_chat_id(token: str, timeout: float = 10.0) -> list[str]:
    """Pull recent chat ids from getUpdates (send your bot a message first)."""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    ids = []
    for upd in data.get("result", []):
        msg = upd.get("message") or upd.get("channel_post") or {}
        chat = msg.get("chat") or {}
        cid = chat.get("id")
        if cid is not None and str(cid) not in ids:
            ids.append(str(cid))
    return ids
