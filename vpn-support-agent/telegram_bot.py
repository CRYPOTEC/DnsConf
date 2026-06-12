"""Telegram long-polling loop: routes user messages to the SupportAgent."""
from __future__ import annotations

import time

from agent import MAX_HISTORY_MESSAGES, SupportAgent
from config import Config
from telegram_api import TelegramAPI

WELCOME = (
    "Привет! Я бот поддержки. Опишите проблему (подключение, оплата, скорость, "
    "не работает сервер и т.п.) — помогу или передам специалисту."
)


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
            message = update.get("message") or update.get("edited_message")
            if not message or "text" not in message:
                continue

            chat_id = message["chat"]["id"]
            text = message["text"].strip()

            if text in ("/start", "/help"):
                tg.send_message(chat_id, WELCOME)
                continue

            convo = histories.get(chat_id, []) + [{"role": "user", "content": text}]
            try:
                reply, _ = agent.run(convo)
            except Exception as e:
                print(f"[agent] ошибка: {e}")
                reply = "Извините, временная ошибка. Попробуйте ещё раз чуть позже."

            tg.send_message(chat_id, reply)
            histories[chat_id] = _trim(
                histories.get(chat_id, [])
                + [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
            )
