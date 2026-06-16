"""Exchange adapter interface.

The engine is written against this interface only, so the same strategy/risk
logic runs unchanged against the paper simulator or live Bybit (demo or real).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from ..models import Candle, Fill, Market, Position, Side


@dataclass(frozen=True)
class InstrumentInfo:
    symbol: str
    qty_step: float       # minimum increment for order quantity (base units)
    min_qty: float        # minimum order quantity (base units)
    tick_size: float      # price increment
    base_coin: str = ""
    quote_coin: str = "USDT"


class Exchange(ABC):
    name: str = "exchange"

    @abstractmethod
    def get_candles(self, symbol: str, market: Market, interval: str,
                    limit: int = 200) -> List[Candle]:
        ...

    @abstractmethod
    def instrument_info(self, symbol: str, market: Market) -> InstrumentInfo:
        ...

    @abstractmethod
    def get_balance(self) -> float:
        """Account equity in quote currency (USDT)."""
        ...

    @abstractmethod
    def get_position(self, symbol: str, market: Market) -> Optional[Position]:
        ...

    @abstractmethod
    def place_market_order(self, symbol: str, market: Market, side: Side,
                           qty: float, reduce_only: bool = False) -> Fill:
        ...

    def set_leverage(self, symbol: str, market: Market, leverage: float) -> None:
        """Override for futures. No-op by default (spot / paper)."""
        return None

    def has_more(self) -> bool:
        """True for live exchanges. The paper replay returns False at end of feed."""
        return True
