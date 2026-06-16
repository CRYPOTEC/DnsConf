"""Orchestration: sources -> signals -> simulated (and optional live) trades.

I/O dependencies (market fetcher, sources, LLM scorer, live broker) are
injectable so the cycle can be unit-tested offline.
"""

from __future__ import annotations

import time
from typing import Callable

from . import polymarket
from . import sources as sources_mod
from .config import Config
from .models import Market, NewsItem
from .paper import InsufficientFunds, PaperBroker, Portfolio
from .signals import detect, detect_llm

MarketFetcher = Callable[[str, str], "Market | None"]


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


def maybe_resolve(pf: Portfolio, markets: dict[str, Market], broker: PaperBroker,
                  log: Callable[[str], None]) -> None:
    """Settle paper positions for any watched market that has resolved.

    A Gamma market is treated as resolved when it is closed; the winning
    outcome is the one priced nearest 1.0.
    """
    held = {pos.market_id for pos in pf.positions.values()}
    seen_ids: set[str] = set()
    for m in markets.values():
        if m.id in seen_ids or m.id not in held or not m.closed:
            continue
        seen_ids.add(m.id)
        winner = max(range(len(m.prices)), key=lambda i: m.prices[i])
        pnl = broker.resolve(m, winner)
        log(f"  RESOLVED '{m.outcomes[winner]}' wins {m.slug} -> realized ${pnl:+.2f}")


def run_once(
    cfg: Config,
    pf: Portfolio,
    seen_news: set[str],
    traded_keys: dict[str, float],
    *,
    market_fetcher: MarketFetcher | None = None,
    sources: list | None = None,
    scorer=None,
    live_broker=None,
    log: Callable[[str], None] = print,
) -> list:
    """One full cycle. Mutates pf/seen_news/traded_keys in place.

    Returns the list of executed paper trades.
    """
    market_fetcher = market_fetcher or _default_market_fetcher
    if sources is None:
        sources = sources_mod.build_sources(cfg)

    markets = resolve_watchlist(cfg, market_fetcher)
    if not markets:
        log("  no watched markets resolved (empty watchlist?)")
        return []

    broker = PaperBroker(
        pf, fee_bps=cfg.fee_bps, slippage_bps=cfg.slippage_bps,
        max_position_usd=cfg.max_position_usd,
    )

    # Settle anything that has resolved since last cycle.
    maybe_resolve(pf, markets, broker, log)

    items = sources_mod.fetch_all(sources)
    fresh = [n for n in items if n.uid not in seen_news]
    log(f"  fetched {len(items)} headlines ({len(fresh)} new)")

    open_markets = {k: m for k, m in markets.items() if not m.closed}
    if cfg.strategy == "llm" and scorer is not None:
        signals = detect_llm(fresh, open_markets, cfg.watchlist, cfg.min_confidence,
                             scorer, max_calls=cfg.llm_max_calls_per_cycle)
    else:
        if cfg.strategy == "llm":
            log("  (llm strategy requested but no scorer available -> keyword)")
        signals = detect(fresh, open_markets, cfg.watchlist, cfg.min_confidence)

    executed = []
    now = time.time()
    for sig in signals:
        out_key = f"{sig.market.id}:{sig.outcome_index}"
        if now - traded_keys.get(out_key, 0.0) < cfg.cooldown_sec:
            continue
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
        if live_broker is not None:
            result = live_broker.execute(sig, cfg.stake_usd, pf)
            log(f"    live: {result.get('status')} - {result.get('reason', '')}".rstrip(" -"))

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
