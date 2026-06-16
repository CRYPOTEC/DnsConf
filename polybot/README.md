# polybot — бот для Polymarket на новостях (бумага + опц. лайв)

Бот, который торгует на [Polymarket](https://polymarket.com) по новостям:
читает источники, ловит события по заданным рынкам и совершает сделки.
**По умолчанию — бумажный режим** (виртуальные деньги, реальные цены), чтобы
проверить наличие edge у стратегии «новость → сигнал → ставка» **до** того,
как рисковать капиталом. Лайв-исполнение есть, но выключено и обмотано
предохранителями (см. ниже).

## Возможности

1. **Две стратегии сигналов**
   - `keyword` — детерминированный keyword-матчинг (офлайн, без ключей).
   - `llm` — оценка новости через **Claude** (`claude-opus-4-8`, structured
     outputs, adaptive thinking): модель читает новость + рынок и выдаёт
     направление (Yes/No) и калиброванную уверенность. Keyword-слова при этом
     служат дешёвым фильтром релевантности, чтобы ограничить число платных
     вызовов.
2. **Несколько источников** — RSS/Atom, NewsAPI.org, X/Twitter, опционально
   websocket-стрим. Источники мёржатся и дедуплицируются.
3. **Авто-resolve + бэктест** — закрытые рынки автоматически рассчитываются
   (честный P&L); офлайн-бэктест прогоняет сохранённый датасет.
4. **Лайв-исполнение** (CLOB) — отдельный модуль с жёсткими предохранителями;
   по умолчанию выключен.
5. **Управление позициями + Telegram** — тейк-профит / стоп-лосс / фиксация у
   разрешения, алерты при росте (+20% / +50% / +100%), и уведомления в Telegram
   о входах (с причиной и планом выхода), росте, выходах, разрешении и сводке.
   Для круглосуточной работы — артефакты деплоя (systemd/Docker), см.
   [DEPLOY.md](DEPLOY.md).

> ⚠️ Контент новостей **недоверенный** (фейки, двусмысленность, prompt-injection
> через текст новости). И keyword-, и LLM-стратегия написаны консервативно;
> LLM-промпт изолирует новость и запрещает следовать инструкциям из неё.

## Требования

- **Python 3.10+**, стандартная библиотека — для ядра (paper/keyword/RSS/бэктест).
- Опционально:
  - `anthropic` — для LLM-стратегии (плюс `ANTHROPIC_API_KEY`).
  - `websockets` — для websocket-источника.
  - `py-clob-client` — для лайв-исполнения (плюс `POLYMARKET_PK`).

Без этих пакетов соответствующие функции просто отключаются, а бот
продолжает работать в базовом режиме.

## Секреты — только через переменные окружения

```
ANTHROPIC_API_KEY      LLM-оценка сигналов
NEWSAPI_KEY            источник NewsAPI
TWITTER_BEARER_TOKEN   источник X/Twitter
POLYMARKET_PK          кошелёк для лайв-исполнения (только лайв-режим)
```

## Быстрый старт

```bash
cd polybot
python -m polybot markets --limit 15     # найти рынки и их slug'и
python -m polybot init                    # создать config.json
# вписать slug рынка + ключевые слова в config.json
python -m polybot run --once              # один цикл (бумага)
python -m polybot run --loop              # крутить постоянно
python -m polybot status                  # портфель
python -m polybot news --limit 20         # превью источников
python -m polybot backtest --data examples/backtest_sample.json
python -m polybot telegram-test           # проверить связь с Telegram / найти chat id
```

Круглосуточный запуск (на постоянно включённом хосте) и подключение Telegram —
в **[DEPLOY.md](DEPLOY.md)**.

## Конфиг (`config.json`)

| поле | смысл |
|------|-------|
| `starting_cash` / `stake_usd` / `max_position_usd` | банк, размер ставки, потолок на (рынок, исход) |
| `min_confidence` | минимальная уверенность сигнала (0..1) |
| `slippage_bps` / `fee_bps` / `cooldown_sec` | проскальзывание, комиссия, пауза между сделками |
| `strategy` | `keyword` или `llm` |
| `llm_model` / `llm_effort` / `llm_thinking` / `llm_max_calls_per_cycle` | параметры LLM-оценки |
| `news_feeds` | список RSS/Atom-лент |
| `newsapi_query` / `twitter_query` / `websocket_url` | доп. источники (нужны ключи в env) |
| `watchlist` | какие рынки отслеживать (см. ниже) |
| `live_*` | лайв-исполнение и предохранители (см. ниже) |

### Элемент watchlist

```json
{
  "slug": "us-x-iran-permanent-peace-deal-by-june-15-2026-734-856-129",
  "match_keywords": ["iran", "tehran"],
  "bull_keywords": ["peace deal", "agreement", "ceasefire"],
  "bear_keywords": ["strike", "attack", "war", "talks fail"]
}
```

- `match_keywords` — относится ли новость к рынку (для LLM это тоже фильтр).
- `bull_keywords` → покупка **Yes**, `bear_keywords` → покупка **No**
  (в keyword-стратегии). В LLM-стратегии направление решает модель.

## LLM-стратегия

```json
{ "strategy": "llm", "llm_model": "claude-opus-4-8", "llm_effort": "low" }
```
Нужен `ANTHROPIC_API_KEY` и пакет `anthropic` (`pip install anthropic`). Если
их нет — бот сам откатывается на keyword-стратегию. Стоимость ограничена
`llm_max_calls_per_cycle` (новости фильтруются `match_keywords` до вызова модели).

## Бэктест

```bash
python -m polybot backtest --data examples/backtest_sample.json
```
Датасет (см. формат в `polybot/backtest.py`) содержит `markets`, `news`,
`watchlist` и опц. `resolutions` (исход рынка). Прогон детерминированный и
офлайновый — удобно проверять изменения стратегии/ключевых слов.

## Лайв-исполнение (по умолчанию ВЫКЛ)

Включается `"live_enabled": true`. Предохранители (`polybot/live.py`):

1. **kill-switch** — если есть файл `STOP` (имя в `live_killswitch_file`),
   ордера не ставятся.
2. **Гейт по бумажной статистике** — нужно ≥ `live_min_paper_trades` сделок и
   бумажный P&L ≥ `live_min_paper_pnl` («заслужи лайв на симуляторе»).
3. **Лимит ставки** — `live_max_stake_usd` на сделку.
4. **Дневной лимит капитала под риском** — `live_daily_loss_limit_usd`.
5. **Ручное подтверждение** для ставок выше `live_confirm_above_usd`.
6. Если нет `py-clob-client` / `POLYMARKET_PK` — остаётся **dry-run** (только
   логирует, что поставил бы).

Реальное размещение ордера изолировано в адаптере `ClobAdapter` — сверь его с
установленной версией `py-clob-client` перед боевым использованием.

## Как это устроено

```
sources/      RSS / NewsAPI / Twitter / websocket  (контент недоверенный!)
polymarket.py Gamma API → Market (цены)            (только чтение)
signals.py    detect (keyword) / detect_llm        (тестируемо)
llm.py        Claude-оценка новости → Verdict       (опц., structured outputs)
paper.py      Portfolio + PaperBroker (buy/sell)   (симуляция, P&L)
engine.py     цикл: resolve→manage→signals→trades→heartbeat
notify.py     Telegram / console уведомления       (вход/рост/выход/сводка)
backtest.py   офлайн-прогон датасета
live.py       LiveBroker + ClobAdapter             (опц., предохранители)
storage.py    state.json (портфель, seen-news, алерты)
cli.py        markets / news / run / status / backtest / telegram-test / init
```

## Тесты

```bash
cd polybot
python -m unittest discover -s tests -v
# или, если установлен pytest:
pytest -q
```
49 тестов, все офлайн (внешние зависимости подменяются фейками).
