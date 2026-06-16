"""Offline backtest: replay a saved dataset of news + market snapshots.

Runs the deterministic keyword strategy and the paper engine over a fixed
dataset, applies any known resolutions, and reports P&L. No network — useful
for validating strategy/keyword changes reproducibly.

Dataset JSON shape:
{
  "starting_cash": 1000, "stake_usd": 25, ... (any risk params, optional),
  "watchlist": [ {slug|id, match_keywords, bull_keywords, bear_keywords}, ... ],
  "markets":   [ {id, question, slug, outcomes, prices, token_ids?}, ... ],
  "news":      [ {source, title, link, summary, published}, ... ],
  "resolutions": { "<slug-or-id>": <winning_outcome_index> }   (optional)
}
"""

from __future__ import annotations

import json

from .config import Config, WatchItem
from .models import Market, NewsItem
from .paper import InsufficientFunds, PaperBroker, Portfolio
from .signals import detect


def _markets_from(data: dict) -> dict[str, Market]:
    markets: dict[str, Market] = {}
    for m in data.get("markets", []):
        market = Market(
            id=str(m.get("id", "")),
            question=m.get("question", ""),
            slug=m.get("slug", ""),
            outcomes=list(m["outcomes"]),
            prices=[float(p) for p in m["prices"]],
            token_ids=list(m.get("token_ids", [])),
            end_date=m.get("end_date"),
            closed=bool(m.get("closed", False)),
        )
        if market.slug:
            markets[market.slug] = market
        if market.id:
            markets[market.id] = market
    return markets


def run_backtest(data: dict, cfg: Config) -> dict:
    """Execute the backtest and return a summary dict."""
    starting_cash = float(data.get("starting_cash", cfg.starting_cash))
    stake = float(data.get("stake_usd", cfg.stake_usd))
    min_conf = float(data.get("min_confidence", cfg.min_confidence))
    fee = float(data.get("fee_bps", cfg.fee_bps))
    slip = float(data.get("slippage_bps", cfg.slippage_bps))
    max_pos = float(data.get("max_position_usd", cfg.max_position_usd))

    watch = [WatchItem(**w) for w in data.get("watchlist", [])]
    markets = _markets_from(data)
    news = [NewsItem(**n) for n in data.get("news", [])]

    pf = Portfolio(starting_cash)
    broker = PaperBroker(pf, fee_bps=fee, slippage_bps=slip, max_position_usd=max_pos)

    signals = detect(news, markets, watch, min_conf)
    executed = 0
    for sig in signals:
        try:
            broker.buy(sig, stake)
            executed += 1
        except InsufficientFunds:
            continue

    # Apply resolutions (winning outcome index per market slug-or-id).
    for key, winner in data.get("resolutions", {}).items():
        market = markets.get(key)
        if market is not None:
            broker.resolve(market, int(winner))

    # Mark-to-market any still-open positions at current snapshot prices.
    prices = {}
    for pos in pf.positions.values():
        for m in markets.values():
            if m.id == pos.market_id and pos.outcome_index < len(m.prices):
                prices[pos.key] = m.prices[pos.outcome_index]
                break

    return {
        "starting_cash": starting_cash,
        "signals": len(signals),
        "trades": executed,
        "realized_pnl": pf.realized_pnl,
        "unrealized_pnl": pf.unrealized_pnl(prices),
        "cash": pf.cash,
        "equity": pf.equity(prices),
        "open_positions": len(pf.positions),
    }


def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
