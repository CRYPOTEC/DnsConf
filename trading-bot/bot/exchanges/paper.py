"""Paper-trading exchange: virtual money, simulated fills.

Used two ways:
  * **Backtest / local sim** — seeded with a pre-built candle feed, the cursor
    advances one bar per :meth:`get_candles` call (so the live engine can drive
    it with ``poll_interval=0``). This is what runs inside the dev container,
    where Bybit is geo-blocked.
  * Forward paper-trading on a live feed is possible by feeding it real candles,
    but on a VPS you'll typically point the engine at Bybit Demo instead.

Fills happen at the last closed price adjusted for slippage, minus a taker fee.
The model is intentionally simple (no margin lock, no funding) — enough to
validate strategy + risk + PnL accounting before risking anything real.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..models import Candle, Fill, Market, Position, Side, Trade
from .base import Exchange, InstrumentInfo


@dataclass
class _OpenPos:
    side: Side
    qty: float
    entry: float
    opened_ts: int
    entry_fee: float


class PaperExchange(Exchange):
    name = "paper"

    def __init__(
        self,
        feeds: Dict[str, List[Candle]],
        starting_balance: float = 10_000.0,
        fee_rate: float = 0.00055,   # Bybit linear taker ~0.055%
        slippage: float = 0.0005,    # 5 bps
        warmup: int = 30,
        instruments: Optional[Dict[str, InstrumentInfo]] = None,
    ) -> None:
        self.feeds = feeds
        self.balance = starting_balance
        self.fee_rate = fee_rate
        self.slippage = slippage
        self.warmup = warmup
        self.cursors: Dict[str, int] = {s: warmup for s in feeds}
        self.last_price: Dict[str, float] = {}
        self.positions: Dict[str, _OpenPos] = {}
        self.trades: List[Trade] = []
        self.instruments = instruments or {}

    # ---- market data -----------------------------------------------------
    def get_candles(self, symbol: str, market: Market, interval: str,
                    limit: int = 200) -> List[Candle]:
        feed = self.feeds[symbol]
        cur = self.cursors.setdefault(symbol, self.warmup)
        cur = min(cur, len(feed))
        window = feed[max(0, cur - limit):cur]
        if window:
            self.last_price[symbol] = window[-1].close
        if self.cursors[symbol] < len(feed):
            self.cursors[symbol] += 1
        return window

    def has_more(self) -> bool:
        return any(self.cursors.get(s, 0) < len(f) for s, f in self.feeds.items())

    def instrument_info(self, symbol: str, market: Market) -> InstrumentInfo:
        if symbol in self.instruments:
            return self.instruments[symbol]
        return InstrumentInfo(symbol, qty_step=0.001, min_qty=0.001,
                              tick_size=0.01, base_coin=symbol[:-4], quote_coin="USDT")

    # ---- account ---------------------------------------------------------
    def _equity(self) -> float:
        eq = self.balance
        for sym, p in self.positions.items():
            price = self.last_price.get(sym, p.entry)
            eq += (price - p.entry) * p.qty * p.side.sign
        return eq

    def get_balance(self) -> float:
        return self._equity()

    def get_position(self, symbol: str, market: Market) -> Optional[Position]:
        p = self.positions.get(symbol)
        if p is None:
            return None
        return Position(symbol, market, p.side, p.qty, p.entry)

    # ---- trading ---------------------------------------------------------
    def place_market_order(self, symbol: str, market: Market, side: Side,
                           qty: float, reduce_only: bool = False) -> Fill:
        ref = self.last_price.get(symbol)
        if ref is None:
            raise RuntimeError(f"no price for {symbol} yet")
        ts = self.feeds[symbol][min(self.cursors[symbol], len(self.feeds[symbol])) - 1].ts
        price = ref * (1 + self.slippage) if side is Side.BUY else ref * (1 - self.slippage)
        fee = price * qty * self.fee_rate

        existing = self.positions.get(symbol)
        if reduce_only or (existing and existing.side is not side):
            if existing is None:
                # nothing to close
                return Fill(symbol, side, 0.0, price, 0.0, ts, reduce_only=True)
            gross = (price - existing.entry) * existing.qty * existing.side.sign
            net = gross - existing.entry_fee - fee
            self.balance += net
            self.trades.append(Trade(
                symbol=symbol, side=existing.side, qty=existing.qty,
                entry=existing.entry, exit=price, pnl=net,
                fees=existing.entry_fee + fee,
                opened_ts=existing.opened_ts, closed_ts=ts,
            ))
            del self.positions[symbol]
            return Fill(symbol, side, existing.qty, price, fee, ts, reduce_only=True)

        # opening a new position
        self.balance -= fee
        self.positions[symbol] = _OpenPos(side=side, qty=qty, entry=price,
                                          opened_ts=ts, entry_fee=fee)
        return Fill(symbol, side, qty, price, fee, ts)
