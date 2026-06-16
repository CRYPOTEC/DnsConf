"""Unit tests for indicators, strategy signals and risk sizing.

Runs under pytest, or standalone:  python tests/test_strategy.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import indicators as ind                       # noqa: E402
from bot.models import Candle, Intent, Market, Position, Side  # noqa: E402
from bot.risk import RiskManager, RiskParams            # noqa: E402
from bot.strategy import BreakoutParams, BreakoutStrategy  # noqa: E402


def _flat(n, price=100.0, jitter=0.0):
    out = []
    ts = 0
    for i in range(n):
        hi = price + jitter
        lo = price - jitter
        out.append(Candle(ts, price, hi, lo, price, 1.0))
        ts += 60_000
    return out


def test_indicators_basic():
    candles = [Candle(i, 10 + i, 12 + i, 8 + i, 10 + i, 1.0) for i in range(30)]
    assert ind.highest_high(candles, 5, offset=1) == 12 + 28  # bars [24..28]
    assert ind.lowest_low(candles, 5, offset=1) == 8 + 24
    assert ind.atr(candles, 14) is not None
    assert ind.atr(candles[:3], 14) is None  # not enough data


def test_breakout_long():
    strat = BreakoutStrategy(BreakoutParams())
    candles = _flat(40, 100.0, jitter=0.5)
    candles.append(Candle(40 * 60_000, 100.0, 110.0, 100.0, 110.0, 1.0))  # upside break
    sig = strat.decide(candles, None)
    assert sig.intent is Intent.OPEN_LONG, sig
    assert sig.stop is not None and sig.stop < 110.0


def test_breakout_short():
    strat = BreakoutStrategy(BreakoutParams(allow_short=True))
    candles = _flat(40, 100.0, jitter=0.5)
    candles.append(Candle(40 * 60_000, 100.0, 100.0, 90.0, 90.0, 1.0))  # downside break
    sig = strat.decide(candles, None)
    assert sig.intent is Intent.OPEN_SHORT, sig
    assert sig.stop is not None and sig.stop > 90.0


def test_no_short_when_disabled():
    strat = BreakoutStrategy(BreakoutParams(allow_short=False))
    candles = _flat(40, 100.0, jitter=0.5)
    candles.append(Candle(40 * 60_000, 100.0, 100.0, 90.0, 90.0, 1.0))
    sig = strat.decide(candles, None)
    assert sig.intent is Intent.HOLD, sig


def test_long_exit_on_stop():
    strat = BreakoutStrategy(BreakoutParams())
    candles = _flat(40, 100.0, jitter=0.5)
    candles.append(Candle(40 * 60_000, 100.0, 100.0, 90.0, 95.0, 1.0))
    pos = Position("BTCUSDT", Market.LINEAR, Side.BUY, qty=1.0, entry=105.0, stop=96.0)
    sig = strat.decide(candles, pos)
    assert sig.intent is Intent.CLOSE, sig


def test_risk_sizing_and_leverage_cap():
    rm = RiskManager(RiskParams(risk_per_trade=0.01, max_leverage=3.0))
    # risk 1% of 10000 = 100; stop distance 2 -> 50 units
    qty = rm.size(equity=10_000, entry=100, stop=98, qty_step=0.001, min_qty=0.001)
    assert abs(qty - 50.0) < 1e-9, qty

    # tight stop would size huge, but leverage caps notional at equity*lev
    qty2 = rm.size(equity=10_000, entry=100, stop=99.99, qty_step=0.001, min_qty=0.001)
    assert abs(qty2 - 300.0) < 1e-6, qty2  # 10000*3/100


def test_risk_daily_halt():
    rm = RiskManager(RiskParams(max_daily_loss=0.10))
    rm.roll_day("2026-06-16", 10_000)
    assert rm.can_open()
    rm.update_equity(8_900)  # -11%
    assert not rm.can_open()


def _run_all():
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in funcs:
        f()
        print(f"  ok  {f.__name__}")
    print(f"\n{len(funcs)} tests passed")


if __name__ == "__main__":
    _run_all()
