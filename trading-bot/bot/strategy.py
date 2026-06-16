"""Breakout strategy: Donchian channel entries with an ATR-based stop.

Classic turtle-style logic:
  * go long  when price closes above the highest high of the last N bars
  * go short when price closes below the lowest low of the last N bars
  * exit on the opposite M-bar Donchian channel (M < N) or when the ATR stop
    is breached.

The strategy is pure: it reads closed candles + the current position and
returns an :class:`Signal`. It never talks to an exchange.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from . import indicators as ind
from .models import Candle, Intent, Position, Side, Signal


@dataclass
class BreakoutParams:
    entry_period: int = 20      # N: breakout lookback for entries
    exit_period: int = 10       # M: opposite-channel lookback for exits
    atr_period: int = 14
    atr_stop_mult: float = 2.0  # protective stop = entry +/- mult * ATR
    allow_short: bool = True    # ignored on spot (cannot short)


class BreakoutStrategy:
    def __init__(self, params: Optional[BreakoutParams] = None) -> None:
        self.p = params or BreakoutParams()

    @property
    def warmup(self) -> int:
        """Minimum candles required before signals are valid."""
        return max(self.p.entry_period, self.p.exit_period, self.p.atr_period) + 2

    def decide(self, candles: List[Candle], position: Optional[Position]) -> Signal:
        if len(candles) < self.warmup:
            return Signal(Intent.HOLD, "warming up")

        close = candles[-1].close
        upper = ind.highest_high(candles, self.p.entry_period)
        lower = ind.lowest_low(candles, self.p.entry_period)
        exit_upper = ind.highest_high(candles, self.p.exit_period)
        exit_lower = ind.lowest_low(candles, self.p.exit_period)
        atr = ind.atr(candles, self.p.atr_period)
        if None in (upper, lower, exit_upper, exit_lower, atr):
            return Signal(Intent.HOLD, "indicators not ready")

        if position is None:
            if close > upper:
                return Signal(Intent.OPEN_LONG, f"close {close:.2f} > {upper:.2f}",
                              stop=close - self.p.atr_stop_mult * atr)
            if self.p.allow_short and close < lower:
                return Signal(Intent.OPEN_SHORT, f"close {close:.2f} < {lower:.2f}",
                              stop=close + self.p.atr_stop_mult * atr)
            return Signal(Intent.HOLD, "no breakout")

        # Manage an open position.
        if position.side is Side.BUY:
            if position.stop is not None and close <= position.stop:
                return Signal(Intent.CLOSE, "stop hit (long)")
            if close < exit_lower:
                return Signal(Intent.CLOSE, f"exit channel {close:.2f} < {exit_lower:.2f}")
        else:  # short
            if position.stop is not None and close >= position.stop:
                return Signal(Intent.CLOSE, "stop hit (short)")
            if close > exit_upper:
                return Signal(Intent.CLOSE, f"exit channel {close:.2f} > {exit_upper:.2f}")
        return Signal(Intent.HOLD, "hold position")
