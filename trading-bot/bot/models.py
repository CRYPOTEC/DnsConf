"""Core data types shared across the bot.

Kept dependency-free (stdlib only) so the strategy/risk/backtest core runs
anywhere, even without ``pybit`` installed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Side(str, Enum):
    BUY = "Buy"
    SELL = "Sell"

    @property
    def opposite(self) -> "Side":
        return Side.SELL if self is Side.BUY else Side.BUY

    @property
    def sign(self) -> int:
        """+1 for long, -1 for short — handy for PnL math."""
        return 1 if self is Side.BUY else -1


class Market(str, Enum):
    """Bybit V5 product category."""
    SPOT = "spot"
    LINEAR = "linear"  # USDT-margined perpetual futures

    @property
    def can_short(self) -> bool:
        return self is Market.LINEAR


class Intent(str, Enum):
    """What the strategy wants the engine to do this bar."""
    HOLD = "hold"
    OPEN_LONG = "open_long"
    OPEN_SHORT = "open_short"
    CLOSE = "close"


@dataclass(frozen=True)
class Candle:
    ts: int  # open time, milliseconds
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Signal:
    intent: Intent
    reason: str = ""
    stop: Optional[float] = None  # protective stop price for a new entry


@dataclass
class Position:
    symbol: str
    market: Market
    side: Side
    qty: float
    entry: float
    stop: Optional[float] = None

    def unrealized_pnl(self, price: float) -> float:
        return (price - self.entry) * self.qty * self.side.sign


@dataclass
class Fill:
    symbol: str
    side: Side
    qty: float
    price: float
    fee: float
    ts: int
    reduce_only: bool = False


@dataclass
class Trade:
    """A closed round-trip, for reporting."""
    symbol: str
    side: Side
    qty: float
    entry: float
    exit: float
    pnl: float
    fees: float
    opened_ts: int
    closed_ts: int
    reason: str = ""
