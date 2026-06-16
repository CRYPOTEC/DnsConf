"""Orchestration: news -> signals -> simulated trades -> persisted state.

The two I/O dependencies (market fetcher, news fetcher) are injectable so
the cycle can be unit-tested offline.
"""

from __future__ import annotations

import time
from typing import Callable

from . import news as news_mod
from . import polymarket
from .config import Config
from .models import Market, NewsItem
from .paper import InsufficientFunds, PaperBroker, Portfolio
from .signals import detect

MarketFetcher = Callable[[str, str], "Market | None"]  # (slug, id) -> Market
NewsFetcher = Callable[[list[str]], list[NewsItem]]


def _default_market_fetcher(slug: str, market_id: str) -> Market | None:
    if slug:
        return polymarket.fetch_by_slug(slug)
    if market_id:
        return polymarket.fetch_by_id(market_id)
    return None


def resolve_watchlist(cfg: Config, fetcher: MarketFetcher) -> dict[str, Market]:
    """Resolve each watch entry to a live Market, keyed by slug-or-id."""
    out: dict[str, Market] = {}
    for item in cfg.watchlist:
        key = item.slug or item.id
        if not key:
            continue
        try:
            m = fetcher(item.slug, item.id)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! failed to load market {key}: {exc}")
            continue
        if m:
            out[key] = m
    return out


def run_once(
    cfg: Config,
    pf: Portfolio,
    seen_news: set[str],
    traded_keys: dict[str, float],
    market_fetcher: MarketFetcher | None = None,
    news_fetcher: NewsFetcher | None = None,
    log: Callable[[str], None] = print,
) -> list:
    """One full cycle. Mutates pf/seen_news/traded_keys in place.

    Returns the list of executed trades (for logging/tests).
    """
    market_fetcher = market_fetcher or _default_market_fetcher
    news_fetcher = news_fetcher or news_mod.fetch_all

    markets = resolve_watchlist(cfg, market_fetcher)
    if not markets:
        log("  no watched markets resolved (empty watchlist?)")
        return []

    items = news_fetcher(cfg.news_feeds)
    fresh = [n for n in items if n.uid not in seen_news]
    log(f"  fetched {len(items)} headlines ({len(fresh)} new)")

    signals = detect(fresh, markets, cfg.watchlist, cfg.min_confidence)

    broker = PaperBroker(
        pf, fee_bps=cfg.fee_bps, slippage_bps=cfg.slippage_bps,
        max_position_usd=cfg.max_position_usd,
    )
    executed = []
    now = time.time()
    for sig in signals:
        out_key = f"{sig.market.id}:{sig.outcome_index}"
        last = traded_keys.get(out_key, 0.0)
        if now - last < cfg.cooldown_sec:
            continue  # respect cooldown per outcome
        try:
            trade = broker.buy(sig, cfg.stake_usd)
        except InsufficientFunds as exc:
            log(f"  skip {sig.outcome_name} @ {sig.market.slug}: {exc}")
            continue
        traded_keys[out_key] = now
        executed.append(trade)
        log(
            f"  BUY {trade.shares:.1f} '{trade.outcome_name}' @ {trade.price:.3f} "
            f"(${trade.cost:.2f}) conf={sig.confidence:.2f} :: {sig.rationale}"
        )

    # mark every processed headline as seen so we never re-trade it
    for n in fresh:
        seen_news.add(n.uid)

    prices = {p.key: markets_price(markets, p) for p in pf.positions.values()}
    log(
        f"  equity=${pf.equity(prices):.2f} cash=${pf.cash:.2f} "
        f"unreal=${pf.unrealized_pnl(prices):+.2f} real=${pf.realized_pnl:+.2f} "
        f"positions={len(pf.positions)} trades={len(pf.trades)}"
    )
    return executed


def markets_price(markets: dict[str, Market], pos) -> float:
    """Current price for a held position, falling back to its avg price."""
    for m in markets.values():
        if m.id == pos.market_id and pos.outcome_index < len(m.prices):
            return m.prices[pos.outcome_index]
    return pos.avg_price
