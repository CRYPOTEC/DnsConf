"""JSON persistence so restarts don't lose the portfolio or re-trade news."""

from __future__ import annotations

import json
import os

from .models import Position, Trade
from .paper import Portfolio


def save(path: str, pf: Portfolio, seen_news: set[str], traded_keys: dict[str, float]) -> None:
    state = {
        "starting_cash": pf.starting_cash,
        "cash": pf.cash,
        "realized_pnl": pf.realized_pnl,
        "positions": [vars(p) for p in pf.positions.values()],
        "trades": [vars(t) for t in pf.trades],
        "seen_news": sorted(seen_news),
        "traded_keys": traded_keys,
    }
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)  # atomic write


def load(path: str, starting_cash: float) -> tuple[Portfolio, set[str], dict[str, float]]:
    if not os.path.exists(path):
        return Portfolio(starting_cash), set(), {}
    with open(path, "r", encoding="utf-8") as fh:
        state = json.load(fh)

    pf = Portfolio(state.get("starting_cash", starting_cash))
    pf.cash = state.get("cash", starting_cash)
    pf.realized_pnl = state.get("realized_pnl", 0.0)
    for p in state.get("positions", []):
        pos = Position(**p)
        pf.positions[pos.key] = pos
    pf.trades = [Trade(**t) for t in state.get("trades", [])]

    seen = set(state.get("seen_news", []))
    traded = dict(state.get("traded_keys", {}))
    return pf, seen, traded
