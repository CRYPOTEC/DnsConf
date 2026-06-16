"""Technical indicators, pure-Python (no numpy/pandas).

All functions operate on the list of closed candles, oldest first.
"""
from __future__ import annotations

from typing import List, Optional

from .models import Candle


def highest_high(candles: List[Candle], period: int, offset: int = 1) -> Optional[float]:
    """Highest high over ``period`` bars ending ``offset`` bars back.

    ``offset=1`` excludes the most recent (current) candle, which is what a
    breakout entry compares against to avoid look-ahead.
    """
    end = len(candles) - offset
    start = end - period
    if start < 0:
        return None
    window = candles[start:end]
    if not window:
        return None
    return max(c.high for c in window)


def lowest_low(candles: List[Candle], period: int, offset: int = 1) -> Optional[float]:
    end = len(candles) - offset
    start = end - period
    if start < 0:
        return None
    window = candles[start:end]
    if not window:
        return None
    return min(c.low for c in window)


def true_range(prev_close: float, candle: Candle) -> float:
    return max(
        candle.high - candle.low,
        abs(candle.high - prev_close),
        abs(candle.low - prev_close),
    )


def atr(candles: List[Candle], period: int) -> Optional[float]:
    """Average True Range via Wilder's smoothing (RMA)."""
    if len(candles) < period + 1:
        return None
    trs = [
        true_range(candles[i - 1].close, candles[i])
        for i in range(1, len(candles))
    ]
    # Seed with simple average of first `period` TRs, then Wilder-smooth.
    rma = sum(trs[:period]) / period
    for tr in trs[period:]:
        rma = (rma * (period - 1) + tr) / period
    return rma


def ema(values: List[float], period: int) -> Optional[float]:
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    e = sum(values[:period]) / period
    for v in values[period:]:
        e = v * k + e * (1 - k)
    return e
