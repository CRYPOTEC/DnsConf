# Деплой polybot на круглосуточную работу (24/7)

Бот должен крутиться на **постоянно включённом хосте** (VPS / домашний сервер /
мини-ПК). Локальный ноут или эфемерный контейнер не годятся — при простое/
выключении бот остановится.

## 0. Что понадобится (секреты — только в `.env`, не в git)

| Переменная | Зачем | Где взять |
|------------|-------|-----------|
| `ANTHROPIC_API_KEY` | LLM-стратегия (`strategy: "llm"`) | console.anthropic.com |
| `TELEGRAM_BOT_TOKEN` | уведомления в Telegram | напиши `@BotFather` → `/newbot` |
| `TELEGRAM_CHAT_ID` | куда слать | см. шаг 1 |
| `NEWSAPI_KEY`, `TWITTER_BEARER_TOKEN` | доп. источники (опц.) | newsapi.org / developer.twitter.com |
| `POLYMARKET_PK` | **только** для лайва | приватный ключ кошелька |

## 1. Подключить Telegram (2 минуты)

1. В Telegram напиши **@BotFather** → `/newbot` → получишь `TELEGRAM_BOT_TOKEN`.
2. Напиши своему новому боту любое сообщение (например, «привет»).
3. Узнай свой `chat id`:
   ```bash
   export TELEGRAM_BOT_TOKEN=123:abc
   python -m polybot telegram-test          # выведет найденные chat id
   export TELEGRAM_CHAT_ID=<твой id>
   python -m polybot telegram-test          # пришлёт тестовое сообщение в чат
   ```

## 2. Выбери способ запуска

### Вариант A — systemd (рекомендую для VPS)

```bash
sudo cp -r polybot /opt/polybot && cd /opt/polybot
cp deploy/.env.example .env && nano .env        # вписать ключи
pip3 install anthropic websockets               # для LLM/websocket
sudo cp deploy/polybot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now polybot
journalctl -u polybot -f                         # живые логи
```
`Restart=always` — бот сам поднимется после падения/перезагрузки.

### Вариант B — Docker

```bash
cd polybot
cp deploy/.env.example .env && nano .env
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml logs -f
```

### Вариант C — nohup (просто и быстро)

```bash
cd polybot
cp deploy/.env.example .env && nano .env
chmod +x deploy/run.sh
nohup ./deploy/run.sh > polybot.log 2>&1 &
tail -f polybot.log
```

## 3. Что бот будет присылать в Telegram

- 🤖 запуск (режим, число рынков, источники);
- 🟢 **вход в позицию** — рынок, исход, цена, **причина** (новость) и **план выхода**;
- 📈 **рост** — при пересечении +20% / +50% / +100% (настраивается `notify_gain_tiers`);
- ✅/🛑 **выход** — тейк-профит / стоп-лосс / фиксация у разрешения, с P&L;
- 🏁 **разрешение рынка** — кто победил и сколько реализовано;
- 📊 **сводка** — раз в час (`notify_heartbeat_sec`).

## 4. Управление риском и стоп-кран

- По умолчанию это **бумага** (`live_enabled: false`) — реальные деньги не тратятся.
- Параметры выхода в конфиге: `take_profit_pct`, `stop_loss_pct`, `exit_price_above`.
- **Kill-switch:** создай файл `STOP` в рабочей папке — лайв-ордера мгновенно
  перестанут ставиться (на бумагу не влияет):
  ```bash
  touch /opt/polybot/STOP     # выключить лайв
  rm /opt/polybot/STOP        # включить обратно
  ```
- Лайв включается осознанно и **только** после стабильно положительной бумажной
  статистики (гейт `live_min_paper_trades` / `live_min_paper_pnl`). См. README.

## 5. Обновить watchlist

```bash
python scripts/build_politics_watchlist.py > config.politics.json
sudo systemctl restart polybot     # или docker compose ... up -d --build
```
