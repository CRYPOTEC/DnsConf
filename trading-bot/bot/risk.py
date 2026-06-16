"""Risk management: position sizing and trading guards.

Sizing is risk-based: each trade risks a fixed fraction of equity, defined by
the distance between entry and the protective stop. Notional is additionally
capped by ``max_leverage`` so a tight stop can't blow up exposure.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RiskParams:
    risk_per_trade: float = 0.01    # fraction of equity risked per trade (1%)
    max_leverage: float = 3.0       # cap notional / equity (futures)
    max_daily_loss: float = 0.10    # halt new entries after -10% on the day
    min_notional: float = 5.0       # skip trades smaller than this (quote ccy)


def round_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return (int(value / step)) * step


class RiskManager:
    def __init__(self, params: Optional[RiskParams] = None) -> None:
        self.p = params or RiskParams()
        self._day: Optional[str] = None
        self._day_start_equity: float = 0.0
        self.halted = False

    def roll_day(self, day_key: str, equity: float) -> None:
        """Reset the daily loss guard at the start of a new day."""
        if self._day != day_key:
            self._day = day_key
            self._day_start_equity = equity
            self.halted = False

    def update_equity(self, equity: float) -> None:
        if self._day_start_equity <= 0:
            self._day_start_equity = equity
            return
        drawdown = 1 - equity / self._day_start_equity
        if drawdown >= self.p.max_daily_loss:
            self.halted = True

    def can_open(self) -> bool:
        return not self.halted

    def size(
        self,
        equity: float,
        entry: float,
        stop: float,
        qty_step: float,
        min_qty: float,
    ) -> float:
        """Return order quantity in base units (0 if the trade should be skipped)."""
        stop_dist = abs(entry - stop)
        if stop_dist <= 0 or entry <= 0 or equity <= 0:
            return 0.0
        risk_amount = equity * self.p.risk_per_trade
        qty = risk_amount / stop_dist

        # Cap by leverage: notional = qty * entry <= equity * max_leverage.
        max_qty = (equity * self.p.max_leverage) / entry
        qty = min(qty, max_qty)

        qty = round_step(qty, qty_step)
        if qty < min_qty:
            return 0.0
        if qty * entry < self.p.min_notional:
            return 0.0
        return qty
