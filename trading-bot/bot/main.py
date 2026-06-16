"""Entrypoint.

  python -m bot.main --config config.json              # uses cfg.mode
  python -m bot.main --config config.json --mode backtest
  python -m bot.main --config config.json --mode live
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

from . import report
from .config import BotConfig, load_config
from .data import synthetic
from .engine import Engine
from .exchanges.paper import PaperExchange
from .risk import RiskManager
from .strategy import BreakoutStrategy


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_backtest(cfg: BotConfig) -> int:
    feeds = {
        sc.symbol: synthetic.generate(
            n=cfg.sim.n_candles, start_price=cfg.sim.start_price, seed=cfg.sim.seed + i)
        for i, sc in enumerate(cfg.symbols)
    }
    strat = BreakoutStrategy(cfg.strategy)
    ex = PaperExchange(
        feeds,
        starting_balance=cfg.sim.starting_balance,
        fee_rate=cfg.sim.fee_rate,
        slippage=cfg.sim.slippage,
        warmup=strat.warmup,
    )
    engine = Engine(ex, strat, RiskManager(cfg.risk), cfg.symbols,
                    poll_interval=0, candle_limit=cfg.candle_limit, state_path=None)
    engine.run()
    print(report.summarize(ex.trades, cfg.sim.starting_balance, ex.get_balance()))
    return 0


def run_live(cfg: BotConfig) -> int:
    from .exchanges.bybit import BybitExchange

    if not cfg.api_key or not cfg.api_secret:
        print("ERROR: set BYBIT_API_KEY and BYBIT_API_SECRET in the environment.",
              file=sys.stderr)
        return 2
    if cfg.state_path:
        os.makedirs(os.path.dirname(cfg.state_path) or ".", exist_ok=True)

    logging.getLogger("bot").warning(
        "LIVE mode on Bybit env=%s — orders will be sent (demo=virtual money).", cfg.env)
    ex = BybitExchange(cfg.api_key, cfg.api_secret, env=cfg.env)
    engine = Engine(ex, BreakoutStrategy(cfg.strategy), RiskManager(cfg.risk),
                    cfg.symbols, poll_interval=cfg.poll_interval,
                    candle_limit=cfg.candle_limit, state_path=cfg.state_path)
    engine.run()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Bybit breakout trading bot")
    parser.add_argument("--config", default="config.json", help="path to JSON config")
    parser.add_argument("--mode", choices=["backtest", "live"], default=None,
                        help="override config mode")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    setup_logging(args.verbose)
    cfg = load_config(args.config)
    mode = args.mode or cfg.mode

    if mode == "backtest":
        return run_backtest(cfg)
    return run_live(cfg)


if __name__ == "__main__":
    raise SystemExit(main())
