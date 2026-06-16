"""Command-line interface.

    python -m polybot markets [--limit N]   # discover active markets + slugs
    python -m polybot news [--limit N]      # preview configured sources
    python -m polybot run [--once|--loop]   # paper-trade (and optional live)
    python -m polybot status                # show portfolio
    python -m polybot backtest --data F     # replay a saved dataset offline
    python -m polybot init                  # write config.json from example
"""

from __future__ import annotations

import argparse
import os
import shutil
import time

from . import backtest as backtest_mod
from . import notify as notify_mod
from . import polymarket, sources, storage
from .config import Config
from .engine import run_once
from .llm import LLMScorer


def _cmd_markets(args) -> None:
    for m in polymarket.fetch_top(args.limit):
        price_str = ", ".join(f"{o}={p:.2f}" for o, p in zip(m.outcomes, m.prices))
        print(f"\n{m.question}")
        print(f"  slug: {m.slug}")
        print(f"  {price_str}")


def _cmd_news(args) -> None:
    cfg = Config.load(args.config)
    srcs = sources.build_sources(cfg)
    print(f"sources: {', '.join(s.name for s in srcs) or '(none)'}")
    for n in sources.fetch_all(srcs)[: args.limit]:
        ago = (time.time() - n.published) / 60.0
        print(f"[{ago:6.0f}m] ({n.source}) {n.title}")


def _cmd_status(args) -> None:
    cfg = Config.load(args.config)
    pf, seen, traded, alerts = storage.load(cfg.state_file, cfg.starting_cash)
    print(f"cash       : ${pf.cash:.2f}")
    print(f"start cash : ${pf.starting_cash:.2f}")
    print(f"realized   : ${pf.realized_pnl:+.2f}")
    print(f"trades     : {len(pf.trades)}")
    print(f"positions  : {len(pf.positions)}")
    for p in pf.positions.values():
        print(f"  - {p.shares:8.1f} '{p.outcome_name}' @ {p.avg_price:.3f}"
              f"  | {p.market_question[:60]}")


def _cmd_backtest(args) -> None:
    cfg = Config.load(args.config)
    data = backtest_mod.load(args.data)
    result = backtest_mod.run_backtest(data, cfg)
    print("backtest result:")
    for k, v in result.items():
        print(f"  {k:16} {v}")


def _cmd_init(args) -> None:
    example = os.path.join(os.path.dirname(__file__), "..", "config.example.json")
    target = args.config or "config.json"
    if os.path.exists(target):
        print(f"{target} already exists, not overwriting.")
        return
    shutil.copy(example, target)
    print(f"wrote {target} — edit the watchlist, then: python -m polybot run --once")


def _build_scorer(cfg: Config):
    if cfg.strategy != "llm":
        return None
    scorer = LLMScorer.from_env(cfg.llm_model, cfg.llm_effort, cfg.llm_thinking)
    if scorer is None:
        print("  (llm strategy set but anthropic SDK/ANTHROPIC_API_KEY missing "
              "-> falling back to keyword strategy)")
    return scorer


def _build_live_broker(cfg: Config):
    if not cfg.live_enabled:
        return None
    from . import live
    print("  !! LIVE TRADING ENABLED — real orders may be placed")
    return live.LiveBroker(cfg, adapter=live.build_adapter(cfg))


def _cmd_run(args) -> None:
    cfg = Config.load(args.config)
    pf, seen, traded, alerts = storage.load(cfg.state_file, cfg.starting_cash)
    srcs = sources.build_sources(cfg)
    scorer = _build_scorer(cfg)
    live_broker = _build_live_broker(cfg)
    notifier = notify_mod.build_notifier()
    print(f"  notifications: {notifier.name}")

    mode = "ЛАЙВ" if cfg.live_enabled else "бумага"
    notifier.send(
        f"🤖 polybot запущен ({mode}): рынков {len(cfg.watchlist)}, "
        f"стратегия {cfg.strategy}, источники {', '.join(s.name for s in srcs) or '—'}. "
        f"Буду писать про входы, рост и выходы.")

    def cycle() -> None:
        print(f"[{time.strftime('%H:%M:%S')}] cycle")
        try:
            run_once(cfg, pf, seen, traded, alerts, sources=srcs, scorer=scorer,
                     live_broker=live_broker, notifier=notifier)
            storage.save(cfg.state_file, pf, seen, traded, alerts)
        except Exception as exc:  # noqa: BLE001 - keep the 24/7 loop alive
            print(f"  ! cycle error: {exc}")
            notifier.send(f"⚠️ Ошибка цикла (продолжаю работать): {exc}")

    cycle()
    if args.loop:
        try:
            while True:
                time.sleep(cfg.poll_interval_sec)
                cycle()
        except KeyboardInterrupt:
            print("\nstopped.")
            notifier.send("🛑 polybot остановлен.")


def _cmd_telegram_test(args) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN не задан. Получи токен у @BotFather и положи в env.")
        return
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat:
        print("TELEGRAM_CHAT_ID не задан. Напиши что-нибудь своему боту, затем ищу chat id...")
        ids = notify_mod.discover_chat_id(token)
        if ids:
            print("Найденные chat id (положи нужный в TELEGRAM_CHAT_ID):", ", ".join(ids))
        else:
            print("Не нашёл сообщений. Сначала напиши боту в Telegram, потом повтори.")
        return
    notify_mod.TelegramNotifier(token, chat).send(
        "✅ polybot: тестовое сообщение. Связь с Telegram работает.")
    print("Отправлено.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="polybot", description="Polymarket paper-trading bot")
    p.add_argument("--config", default="config.json", help="path to config JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("markets", help="list active markets and their slugs")
    m.add_argument("--limit", type=int, default=20)
    m.set_defaults(func=_cmd_markets)

    n = sub.add_parser("news", help="preview configured news sources")
    n.add_argument("--limit", type=int, default=20)
    n.set_defaults(func=_cmd_news)

    r = sub.add_parser("run", help="run trading")
    grp = r.add_mutually_exclusive_group()
    grp.add_argument("--once", action="store_true", help="single cycle (default)")
    grp.add_argument("--loop", action="store_true", help="loop forever")
    r.set_defaults(func=_cmd_run)

    s = sub.add_parser("status", help="show portfolio")
    s.set_defaults(func=_cmd_status)

    b = sub.add_parser("backtest", help="replay a saved dataset offline")
    b.add_argument("--data", required=True, help="path to backtest dataset JSON")
    b.set_defaults(func=_cmd_backtest)

    t = sub.add_parser("telegram-test", help="verify Telegram setup / discover chat id")
    t.set_defaults(func=_cmd_telegram_test)

    i = sub.add_parser("init", help="create config.json from the example")
    i.set_defaults(func=_cmd_init)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0
