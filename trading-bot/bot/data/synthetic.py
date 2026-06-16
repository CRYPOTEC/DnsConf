"""Synthetic OHLCV generator for local simulation.

Produces a regime-switching price series (alternating trends and ranges) so a
breakout strategy has something realistic to act on. Seeded for reproducibility.

This is NOT market data and says nothing about real performance — it only
exercises the full pipeline (feed -> strategy -> risk -> fills -> PnL) where the
real exchange is unreachable.
"""
from __future__ import annotations

import random
from typing import List

from ..models import Candle

INTERVAL_MS = 3_600_000  # 1h


def generate(n: int = 1500, start_price: float = 50_000.0, seed: int = 42,
             interval_ms: int = INTERVAL_MS, start_ts: int = 1_700_000_000_000) -> List[Candle]:
    rng = random.Random(seed)
    candles: List[Candle] = []
    price = start_price
    ts = start_ts
    i = 0
    while i < n:
        # pick a regime
        regime = rng.choices(["up", "down", "range"], weights=[0.35, 0.3, 0.35])[0]
        seg_len = rng.randint(20, 80)
        if regime == "up":
            drift, vol = rng.uniform(0.0008, 0.0025), 0.010
        elif regime == "down":
            drift, vol = -rng.uniform(0.0008, 0.0025), 0.012
        else:
            drift, vol = 0.0, 0.006
        for _ in range(seg_len):
            if i >= n:
                break
            open_ = price
            ret = drift + rng.gauss(0, vol)
            close = max(1.0, open_ * (1 + ret))
            hi = max(open_, close) * (1 + abs(rng.gauss(0, vol / 2)))
            lo = min(open_, close) * (1 - abs(rng.gauss(0, vol / 2)))
            vol_traded = rng.uniform(10, 100)
            candles.append(Candle(ts, open_, hi, lo, close, vol_traded))
            price = close
            ts += interval_ms
            i += 1
    return candles
