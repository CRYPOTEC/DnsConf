"""Command-line interface.

    python -m polybot markets [--limit N]   # discover active markets + slugs
    python -m polybot news [--limit N]      # preview configured feeds
    python -m polybot run [--once|--loop]   # paper-trade
    python -m polybot status                # show portfolio
    python -m polybot init                  # write config.json from example
"""

from __future__ import annotations

import argparse
import os
import shutil
import time

from . import news as news_mod
from . import polymarket, storage
from .config import Config
from .engine import resolve_watchlist, run_once, _default_market_fetcher


def _cmd_markets(args) -> None:
    for m in polymarket.fetch_top(args.limit):
        price_str = ", ".join(
            f"{o}={p:.2f}" for o, p in zip(m.outcomes, m.prices)
        )
        print(f"\n{m.question}")
        print(f"  slug: {m.slug}")
        print(f"  {price_str}")


def _cmd_news(args) -> None:
    cfg = Config.load(args.config)
    for n in news_mod.fetch_all(cfg.news_feeds)[: args.limit]:
        ago = (time.time() - n.published) / 60.0
        print(f"[{ago:6.0f}m] {n.title}")


def _cmd_status(args) -> None:
    cfg = Config.load(args.config)
    pf, seen, traded = storage.load(cfg.state_file, cfg.starting_cash)
    print(f"cash       : ${pf.cash:.2f}")
    print(f"start cash : ${pf.starting_cash:.2f}")
    print(f"realized   : ${pf.realized_pnl:+.2f}")
    print(f"trades     : {len(pf.trades)}")
    print(f"positions  : {len(pf.positions)}")
    for p in pf.positions.values():
        print(
            f"  - {p.shares:8.1f} '{p.outcome_name}' @ {p.avg_price:.3f}"
            f"  | {p.market_question[:60]}"
        )


def _cmd_init(args) -> None:
    example = os.path.join(os.path.dirname(__file__), "..", "config.example.json")
    target = args.config or "config.json"
    if os.path.exists(target):
        print(f"{target} already exists, not overwriting.")
        return
    shutil.copy(example, target)
    print(f"wrote {target} — edit the watchlist, then run: python -m polybot run --once")


def _cmd_run(args) -> None:
    cfg = Config.load(args.config)
    pf, seen, traded = storage.load(cfg.state_file, cfg.starting_cash)

    def cycle() -> None:
        print(f"[{time.strftime('%H:%M:%S')}] cycle")
        run_once(cfg, pf, seen, traded)
        storage.save(cfg.state_file, pf, seen, traded)

    cycle()
    if args.loop:
        try:
            while True:
                time.sleep(cfg.poll_interval_sec)
                cycle()
        except KeyboardInterrupt:
            print("\nstopped.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="polybot", description="Polymarket paper-trading bot")
    p.add_argument("--config", default="config.json", help="path to config JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("markets", help="list active markets and their slugs")
    m.add_argument("--limit", type=int, default=20)
    m.set_defaults(func=_cmd_markets)

    n = sub.add_parser("news", help="preview configured news feeds")
    n.add_argument("--limit", type=int, default=20)
    n.set_defaults(func=_cmd_news)

    r = sub.add_parser("run", help="run paper trading")
    grp = r.add_mutually_exclusive_group()
    grp.add_argument("--once", action="store_true", help="single cycle (default)")
    grp.add_argument("--loop", action="store_true", help="loop forever")
    r.set_defaults(func=_cmd_run)

    s = sub.add_parser("status", help="show portfolio")
    s.set_defaults(func=_cmd_status)

    i = sub.add_parser("init", help="create config.json from the example")
    i.set_defaults(func=_cmd_init)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0
