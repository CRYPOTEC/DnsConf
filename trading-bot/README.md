# Bybit Trading Bot (breakout, spot + futures)

Торговый бот для биржи **Bybit** (спот + USDT-фьючерсы), работающий 24/7.
Стратегия — **импульсная / breakout** (пробой канала Дончиана + ATR-стоп и
риск-менеджмент). Один движок, три режима исполнения через подключаемый адаптер
биржи: **бэктест/симулятор → Bybit Demo → реал**.

> ⚠️ **Дисклеймер.** Это инструмент для алготрейдинга. Торговля сопряжена с
> риском потери средств. Цифры в бэктесте на синтетических данных — это проверка
> логики, **не** прогноз прибыли. Сначала Demo, потом реал с маленьким депозитом.

## Архитектура

```
bot/
├── models.py            # типы: Candle, Position, Side, Market, Signal, Trade
├── indicators.py        # EMA, ATR, Donchian (чистый Python, без numpy)
├── strategy.py          # BreakoutStrategy — только логика сигналов
├── risk.py              # RiskManager — сайзинг по риску, плечо, дневной лимит
├── engine.py            # главный цикл 24/7 (не зависит от биржи)
├── report.py            # отчёт по сделкам (винрейт, PF, просадка)
├── config.py            # загрузка JSON-конфига + секреты из ENV
├── main.py              # точка входа (--mode backtest | live)
├── data/synthetic.py    # генератор данных для локального симулятора
└── exchanges/
    ├── base.py          # интерфейс Exchange
    ├── paper.py         # PaperExchange — виртуальные деньги, симуляция филов
    └── bybit.py         # BybitExchange — pybit, env = demo|testnet|live
```

Ключевая идея: `strategy` + `risk` + `indicators` — чистая логика, которая
работает одинаково в бэктесте, на демо и на реале. Меняется только адаптер биржи.

## Быстрый старт — симулятор (без аккаунта, без сети)

Зависимостей не нужно, всё на стандартной библиотеке:

```bash
cd trading-bot
python3 -m bot.main --config config.example.json --mode backtest
python3 tests/test_strategy.py     # юнит-тесты
```

Получите отчёт: число сделок, винрейт, profit factor, макс. просадка, итоговый PnL.
Параметры стратегии/риска/данных правятся в `config.example.json` (секция `sim`).

## Demo Trading на Bybit (виртуальные деньги, реальные цены)

> Bybit блокирует доступ из некоторых стран на стороне CloudFront. Запускать
> нужно там, где Bybit доступен (ваш VPS в подходящем регионе).

1. На Bybit включите **Demo Trading** и создайте для него **API-ключи**.
2. Установите зависимости и положите ключи в окружение:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env        # впишите BYBIT_API_KEY / BYBIT_API_SECRET
   cp config.example.json config.json
   ```
3. В `config.json` поставьте `"mode": "live"`, `"env": "demo"`.
4. Запуск:
   ```bash
   set -a && source .env && set +a
   python3 -m bot.main --config config.json --mode live
   ```

`env` переключает окружение: `demo` (демо-счёт), `testnet` (тестовая сеть),
`live` (реальные деньги — включайте осознанно).

## Деплой на VPS 24/7

### Вариант A — Docker (рекомендуется)
```bash
cp .env.example .env            # ключи
cp config.example.json config.json   # mode=live, env=demo
docker compose up -d --build
docker compose logs -f
```
Состояние (открытые позиции/стопы) сохраняется в `./state` — бот переживает
рестарт.

### Вариант B — systemd
См. инструкцию в шапке `deploy/tradingbot.service` (venv + EnvironmentFile +
`systemctl enable --now tradingbot`).

## Конфигурация (`config.json`)

| Поле | Значение |
|------|----------|
| `mode` | `backtest` (симулятор) или `live` (Bybit) |
| `env` | `demo` / `testnet` / `live` — окружение Bybit для live |
| `poll_interval` | период опроса в секундах (live) |
| `symbols[]` | `symbol`, `market` (`linear`/`spot`), `interval`, `leverage` |
| `strategy` | `entry_period`, `exit_period`, `atr_period`, `atr_stop_mult`, `allow_short` |
| `risk` | `risk_per_trade`, `max_leverage`, `max_daily_loss`, `min_notional` |
| `sim` | параметры синтетических данных для бэктеста |

Секреты (`BYBIT_API_KEY`, `BYBIT_API_SECRET`) — **только** через переменные
окружения, в репозиторий не коммитятся.

## Управление риском
- Сайзинг от риска: на сделку рискуется фиксированный % депозита (`risk_per_trade`),
  объём считается от расстояния до стопа.
- Ограничение плеча (`max_leverage`) ограничивает номинал позиции.
- Дневной стоп (`max_daily_loss`): после заданной просадки за день новые входы
  блокируются.

## Замечания и ограничения
- `linear` (фьючерсы) — основной рынок: позиции читаются с биржи и переживают
  рестарт. Рекомендуется для breakout (можно шортить).
- `spot` — лонг-онли; открытая спот-позиция кэшируется в адаптере на время сессии.
- Симулятор не моделирует фандинг и блокировку маржи — этого достаточно для
  проверки логики, но реальное исполнение на демо точнее.

## Дальнейшие шаги (roadmap)
- WebSocket-поток вместо опроса REST (меньше задержка).
- Реальные исторические данные для бэктеста (вместо синтетики).
- Серверные стоп-ордера на бирже вместо клиентских.
- Уведомления (Telegram) о сделках и ошибках.
- Несколько стратегий и аллокация капитала между ними.
