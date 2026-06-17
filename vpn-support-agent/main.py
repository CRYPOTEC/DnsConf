"""Entry point. Validates config, reports readiness, starts the Telegram bot."""
from __future__ import annotations

from composio_client import ComposioClient
from config import load_config
from telegram_bot import run_bot


def main() -> None:
    cfg = load_config()

    print("VPN Support Agent — проверка конфигурации:")
    print(f"  • LLM модель:            {cfg.anthropic_model}")
    print(f"  • Логирование в таблицу: {'включено' if cfg.sheet_logging_enabled else 'выключено'}")
    print(f"  • Уведомления админу:    {'включены' if cfg.admin_notifications_enabled else 'выключены'}")

    if cfg.sheet_logging_enabled:
        connected = ComposioClient(cfg.composio_api_key, cfg.composio_user_id).is_toolkit_connected(
            "googlesheets"
        )
        status = "✅ подключён" if connected else "❌ НЕ подключён (жалобы не запишутся)"
        print(f"  • Google Sheets ({cfg.composio_user_id}): {status}")
        if not connected:
            print("    → Подключи Google Sheets в дашборде Composio под этим user id (см. README).")

    run_bot(cfg)


if __name__ == "__main__":
    main()
