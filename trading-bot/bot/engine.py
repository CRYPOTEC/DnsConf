"""The live trading loop — exchange-agnostic.

For every configured symbol each tick: pull candles, ask the strategy, size
with the risk manager, and route market orders through the exchange adapter.
The same loop drives the paper simulator (``poll_interval=0``, stops when the
feed is exhausted) and live Bybit (``poll_interval`` seconds, runs forever).

Protective stops are tracked here (client-side) and persisted to a JSON state
file so the bot survives a restart.
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .exchanges.base import Exchange
from .models import Intent, Market, Side
from .risk import RiskManager
from .strategy import BreakoutStrategy

log = logging.getLogger("bot.engine")


@dataclass
class SymbolConfig:
    symbol: str
    market: Market
    interval: str = "60"     # Bybit kline interval (minutes, or D/W/M)
    leverage: float = 3.0


class Engine:
    def __init__(
        self,
        exchange: Exchange,
        strategy: BreakoutStrategy,
        risk: RiskManager,
        symbols: List[SymbolConfig],
        poll_interval: float = 15.0,
        candle_limit: int = 200,
        state_path: Optional[str] = None,
    ) -> None:
        self.ex = exchange
        self.strategy = strategy
        self.risk = risk
        self.symbols = symbols
        self.poll_interval = poll_interval
        self.candle_limit = candle_limit
        self.state_path = state_path
        self.stops: Dict[str, float] = {}
        self._running = False
        self._load_state()

    # ---- persistence -----------------------------------------------------
    def _load_state(self) -> None:
        if self.state_path and os.path.exists(self.state_path):
            try:
                with open(self.state_path) as f:
                    self.stops = {k: float(v) for k, v in json.load(f).get("stops", {}).items()}
                log.info("loaded state: %d stop(s)", len(self.stops))
            except Exception as e:
                log.warning("could not load state: %s", e)

    def _save_state(self) -> None:
        if not self.state_path:
            return
        tmp = self.state_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"stops": self.stops}, f)
        os.replace(tmp, self.state_path)

    # ---- main loop -------------------------------------------------------
    def run(self) -> None:
        self._running = True
        for sc in self.symbols:
            if sc.market is Market.LINEAR:
                self.ex.set_leverage(sc.symbol, sc.market, sc.leverage)
        log.info("engine started: %s, exchange=%s", [s.symbol for s in self.symbols], self.ex.name)
        try:
            while self._running:
                for sc in self.symbols:
                    try:
                        self._process(sc)
                    except Exception as e:
                        log.exception("error processing %s: %s", sc.symbol, e)
                if not self.ex.has_more():
                    break
                if self.poll_interval > 0:
                    time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            log.info("interrupted, shutting down")
        finally:
            self._save_state()

    def stop(self) -> None:
        self._running = False

    # ---- per-symbol logic ------------------------------------------------
    def _process(self, sc: SymbolConfig) -> None:
        candles = self.ex.get_candles(sc.symbol, sc.market, sc.interval, self.candle_limit)
        if len(candles) < self.strategy.warmup:
            return

        last = candles[-1]
        day_key = datetime.fromtimestamp(last.ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        equity = self.ex.get_balance()
        self.risk.roll_day(day_key, equity)
        self.risk.update_equity(equity)

        pos = self.ex.get_position(sc.symbol, sc.market)
        if pos is not None and sc.symbol in self.stops:
            pos.stop = self.stops[sc.symbol]

        signal = self.strategy.decide(candles, pos)
        price = last.close
        info = self.ex.instrument_info(sc.symbol, sc.market)

        if signal.intent in (Intent.OPEN_LONG, Intent.OPEN_SHORT) and pos is None:
            if not self.risk.can_open():
                return
            if signal.intent is Intent.OPEN_SHORT and not sc.market.can_short:
                return
            side = Side.BUY if signal.intent is Intent.OPEN_LONG else Side.SELL
            stop = signal.stop
            if stop is None:
                return
            qty = self.risk.size(equity, price, stop, info.qty_step, info.min_qty)
            if qty <= 0:
                return
            self.ex.place_market_order(sc.symbol, sc.market, side, qty)
            self.stops[sc.symbol] = stop
            self._save_state()
            log.info("OPEN %s %s qty=%.6f @~%.4f stop=%.4f (%s)",
                     side.value, sc.symbol, qty, price, stop, signal.reason)

        elif signal.intent is Intent.CLOSE and pos is not None:
            self.ex.place_market_order(sc.symbol, sc.market, pos.side.opposite,
                                       pos.qty, reduce_only=True)
            self.stops.pop(sc.symbol, None)
            self._save_state()
            log.info("CLOSE %s qty=%.6f @~%.4f (%s)",
                     sc.symbol, pos.qty, price, signal.reason)
