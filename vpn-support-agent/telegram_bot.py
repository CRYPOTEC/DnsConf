"""Telegram long-polling loop: routes user messages to the SupportAgent."""
from __future__ import annotations

import datetime as dt
import json
import time
from pathlib import Path

from agent import MAX_HISTORY_MESSAGES, SupportAgent
from config import Config
from telegram_api import TelegramAPI

# Full text of every incoming message (stdout log truncates) — useful to
# recover long texts users send, e.g. draft knowledge-base instructions.
INCOMING_LOG = Path(__file__).with_name("incoming.log")


def _log_incoming(message: dict, text: str) -> None:
    sender = message.get("from") or {}
    entry = {
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "chat_id": message["chat"]["id"],
        "from": sender.get("username") or sender.get("first_name") or "",
        "text": text,
    }
    try:
        with INCOMING_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[incoming.log] не записалось: {e}")

WELCOME = "Здравствуйте! Чем могу помочь?"


def _trim(history: list[dict]) -> list[dict]:
    history = history[-MAX_HISTORY_MESSAGES:]
    # A conversation must start with a user turn.
    while history and history[0]["role"] != "user":
        history.pop(0)
    return history


def run_bot(cfg: Config) -> None:
    agent = SupportAgent(cfg)
    tg = TelegramAPI(cfg.telegram_bot_token)
    histories: dict[int, list[dict]] = {}
    offset: int | None = None

    me = tg.get_me()
    print(f"Бот @{me.get('username')} запущен. Модель: {cfg.anthropic_model}. Жду сообщений…")

    while True:
        try:
            updates = tg.get_updates(offset=offset)
        except Exception as e:
            print(f"[getUpdates] ошибка: {e}; повтор через 3с")
            time.sleep(3)
            continue

        for update in updates:
            offset = update["update_id"] + 1
            business = update.get("business_message")
            message = business or update.get("message") or update.get("edited_message")
            if not message:
                continue

            chat_id = message["chat"]["id"]
            # Documents/photos carry their text in "caption", not "text".
            text = (message.get("text") or message.get("caption") or "").strip()
            if not text:
                kinds = [k for k in ("photo", "document", "voice", "video",
                                     "sticker", "audio", "video_note") if k in message]
                print(f"[msg] chat={chat_id}: без текста (вложение: {kinds or 'неизвестно'}) — пропущено")
                continue
            bcid = business.get("business_connection_id") if business else None

            # Business mode: the chat is between a customer and the work account.
            # Outgoing messages typed by the account owner also arrive as
            # business_message (sender ≠ chat) — never auto-reply to those.
            if business:
                sender_id = (message.get("from") or {}).get("id")
                if sender_id != chat_id:
                    continue

            if text in ("/start", "/help") and not business:
                tg.send_message(chat_id, WELCOME)
                continue

            print(f"[msg] chat={chat_id}{' business' if bcid else ''}: {text[:80]!r}")
            _log_incoming(message, text)
            convo = histories.get(chat_id, []) + [{"role": "user", "content": text}]
            try:
                reply, _ = agent.run(convo)
            except Exception as e:
                print(f"[agent] ошибка: {e}")
                reply = "Извините, временная ошибка. Попробуйте ещё раз чуть позже."
            print(f"[reply] chat={chat_id}: {reply[:80]!r}")

            tg.send_message(chat_id, reply, business_connection_id=bcid)
            histories[chat_id] = _trim(
                histories.get(chat_id, [])
                + [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
            )
