"""Paper-trading engine: a virtual portfolio with simulated fills.

No network, no money. Buying a "Yes" share at price p costs $p and pays $1
if the market resolves Yes (else $0) — the Polymarket convention.
"""

from __future__ import annotations

import time

from .models import Market, Position, Signal, Trade


class InsufficientFunds(Exception):
    pass


class Portfolio:
    def __init__(self, cash: float):
        self.starting_cash = cash
        self.cash = cash
        self.positions: dict[str, Position] = {}
        self.trades: list[Trade] = []
        self.realized_pnl = 0.0

    # --- valuation ---------------------------------------------------------
    def position_value(self, prices: dict[str, float]) -> float:
        """Mark-to-market value of open positions given current prices.

        `prices` maps Position.key -> current price of that outcome.
        """
        total = 0.0
        for pos in self.positions.values():
            total += pos.shares * prices.get(pos.key, pos.avg_price)
        return total

    def equity(self, prices: dict[str, float]) -> float:
        return self.cash + self.position_value(prices)

    def unrealized_pnl(self, prices: dict[str, float]) -> float:
        total = 0.0
        for pos in self.positions.values():
            cur = prices.get(pos.key, pos.avg_price)
            total += pos.shares * (cur - pos.avg_price)
        return total


class PaperBroker:
    def __init__(
        self,
        portfolio: Portfolio,
        fee_bps: float = 0.0,
        slippage_bps: float = 0.0,
        max_position_usd: float = 1e9,
    ):
        self.pf = portfolio
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps
        self.max_position_usd = max_position_usd

    def _fill_price(self, quoted: float) -> float:
        """Adverse slippage: buys fill above the quote. Clamp to (0,1)."""
        price = quoted * (1.0 + self.slippage_bps / 10_000.0)
        return min(0.999, max(0.001, price))

    def can_buy(self, signal: Signal, stake_usd: float) -> tuple[bool, str]:
        key = f"{signal.market.id}:{signal.outcome_index}"
        existing = self.pf.positions.get(key)
        basis = existing.shares * existing.avg_price if existing else 0.0
        if basis + stake_usd > self.max_position_usd + 1e-9:
            return False, "max_position_usd reached"
        price = self._fill_price(signal.suggested_price)
        cost = stake_usd * (1.0 + self.fee_bps / 10_000.0)
        if cost > self.pf.cash + 1e-9:
            return False, "insufficient cash"
        if price >= 0.999:
            return False, "price too close to 1.0 (no upside)"
        return True, ""

    def buy(self, signal: Signal, stake_usd: float) -> Trade:
        ok, reason = self.can_buy(signal, stake_usd)
        if not ok:
            raise InsufficientFunds(reason)

        price = self._fill_price(signal.suggested_price)
        shares = stake_usd / price
        cost = stake_usd * (1.0 + self.fee_bps / 10_000.0)
        self.pf.cash -= cost

        key = f"{signal.market.id}:{signal.outcome_index}"
        pos = self.pf.positions.get(key)
        if pos is None:
            self.pf.positions[key] = Position(
                market_id=signal.market.id,
                market_question=signal.market.question,
                outcome_index=signal.outcome_index,
                outcome_name=signal.outcome_name,
                shares=shares,
                avg_price=price,
            )
        else:
            total_cost = pos.shares * pos.avg_price + shares * price
            pos.shares += shares
            pos.avg_price = total_cost / pos.shares

        trade = Trade(
            ts=time.time(),
            market_id=signal.market.id,
            market_question=signal.market.question,
            outcome_name=signal.outcome_name,
            side="BUY",
            shares=shares,
            price=price,
            cost=cost,
            rationale=signal.rationale,
        )
        self.pf.trades.append(trade)
        return trade

    def resolve(self, market: Market, winning_outcome_index: int) -> float:
        """Settle every position in a resolved market. Returns realized P&L."""
        realized = 0.0
        for key in list(self.pf.positions.keys()):
            pos = self.pf.positions[key]
            if pos.market_id != market.id:
                continue
            payout = pos.shares * (1.0 if pos.outcome_index == winning_outcome_index else 0.0)
            realized += payout - pos.shares * pos.avg_price
            self.pf.cash += payout
            del self.pf.positions[key]
        self.pf.realized_pnl += realized
        return realized
