"""The support agent: Claude (the brain) + tools (the hands).

Claude reads the FAQ, answers the user, and decides when to call tools:
  - log_issue        → append a row to the Google Sheet (via Composio)
  - escalate_to_admin → send an urgent Telegram message to the admin chat
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import anthropic

from composio_client import ComposioClient, ComposioError
from config import Config
from telegram_api import TelegramAPI

MAX_TOOL_ITERATIONS = 5
MAX_HISTORY_MESSAGES = 12  # keep recent context bounded

TOOLS = [
    {
        "name": "log_issue",
        "description": (
            "Зафиксировать обращение/жалобу пользователя в таблице. "
            "Вызывай, когда пользователь сообщает о проблеме: не подключается, "
            "не работает сервер, низкая скорость, проблема с оплатой, не пришёл код и т.п. "
            "Вызывай ОДИН раз на обращение."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["connection", "payment", "speed", "server_down", "account", "other"],
                    "description": "Тип проблемы.",
                },
                "country_or_server": {
                    "type": "string",
                    "description": "Страна/сервер, если упомянуты (например, 'Германия'). Иначе пусто.",
                },
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Серьёзность: high — оплата/массовый сбой/недоступность.",
                },
                "summary": {
                    "type": "string",
                    "description": "Короткое описание проблемы своими словами (1–2 предложения).",
                },
            },
            "required": ["category", "severity", "summary"],
        },
    },
    {
        "name": "escalate_to_admin",
        "description": (
            "Отправить срочное уведомление администратору. Вызывай для серьёзных проблем: "
            "недоступность сервера, сбой оплаты у платящего пользователя, массовая проблема."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Что случилось и что проверить."},
                "severity": {"type": "string", "enum": ["medium", "high"]},
            },
            "required": ["summary", "severity"],
        },
    },
]

SYSTEM_PROMPT_TEMPLATE = """\
Ты — ассистент поддержки VPN-сервиса. Общаешься с пользователями в Telegram.

Правила:
- Отвечай на том языке, на котором написал пользователь (русский/английский).
- Будь кратким, дружелюбным и по делу. Без воды.
- Отвечай ТОЛЬКО на основе базы знаний ниже. Не выдумывай факты, цены, сроки.
  Если ответа в базе нет — честно скажи, что передашь вопрос специалисту, и зафиксируй обращение.
- Если пользователь сообщает о проблеме — вызови инструмент log_issue (один раз).
- Для серьёзных проблем (сервер недоступен, сбой оплаты, массовый сбой) — дополнительно
  вызови escalate_to_admin.
- Никогда не обещай возвраты средств и не меняй подписку сам — это делает человек/магазин.
- После работы инструментов дай пользователю понятный финальный ответ.

=== БАЗА ЗНАНИЙ ===
{knowledge_base}
=== КОНЕЦ БАЗЫ ЗНАНИЙ ===
"""

FALLBACK_REPLY = (
    "Извините, не смог обработать запрос. Передам ваш вопрос специалисту — он скоро ответит."
)


class SupportAgent:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
        self.telegram = TelegramAPI(cfg.telegram_bot_token)
        self.composio = (
            ComposioClient(cfg.composio_api_key, cfg.composio_user_id)
            if cfg.sheet_logging_enabled
            else None
        )
        kb = Path(__file__).with_name("knowledge_base.md").read_text(encoding="utf-8")
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(knowledge_base=kb)

    # ── tool execution ────────────────────────────────────────────────
    def _exec_tool(self, name: str, args: dict) -> str:
        if name == "log_issue":
            return self._log_issue(args)
        if name == "escalate_to_admin":
            return self._escalate(args)
        return f"Неизвестный инструмент: {name}"

    def _log_issue(self, args: dict) -> str:
        row = [
            dt.datetime.now().isoformat(timespec="seconds"),
            args.get("category", ""),
            args.get("country_or_server", ""),
            args.get("severity", ""),
            args.get("summary", ""),
        ]
        if not self.composio:
            return "Логирование в таблицу не настроено (нет Composio/Sheet). Обращение не записано."
        try:
            self.composio.append_sheet_row(
                self.cfg.google_sheet_id, self.cfg.google_sheet_name, row
            )
            return "Обращение записано в таблицу."
        except ComposioError as e:
            return f"Не удалось записать в таблицу: {e}"

    def _escalate(self, args: dict) -> str:
        if not self.cfg.admin_notifications_enabled:
            return "Уведомления администратору не настроены (нет TELEGRAM_ADMIN_CHAT_ID)."
        text = f"🚨 [{args.get('severity','')}] Эскалация поддержки:\n{args.get('summary','')}"
        try:
            self.telegram.send_message(self.cfg.telegram_admin_chat_id, text)
            return "Администратор уведомлён."
        except Exception as e:  # network/Telegram errors shouldn't break the reply
            return f"Не удалось уведомить администратора: {e}"

    # ── main loop ─────────────────────────────────────────────────────
    def run(self, messages: list[dict]) -> tuple[str, list[dict]]:
        """Run the tool-use loop. Returns (reply_text, updated_messages)."""
        for _ in range(MAX_TOOL_ITERATIONS):
            resp = self.client.messages.create(
                model=self.cfg.anthropic_model,
                max_tokens=1024,
                system=self.system_prompt,
                tools=TOOLS,
                messages=messages,
            )

            if resp.stop_reason == "refusal":
                return FALLBACK_REPLY, messages

            if resp.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": resp.content})
                results = []
                for block in resp.content:
                    if block.type == "tool_use":
                        output = self._exec_tool(block.name, block.input)
                        results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": output,
                            }
                        )
                messages.append({"role": "user", "content": results})
                continue

            # end_turn (or anything else): collect the text answer
            text = "".join(b.text for b in resp.content if b.type == "text").strip()
            messages.append({"role": "assistant", "content": resp.content})
            return (text or FALLBACK_REPLY), messages

        return FALLBACK_REPLY, messages
