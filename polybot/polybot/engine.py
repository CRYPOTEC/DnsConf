"""Orchestration: sources -> signals -> trades -> position management.

Each cycle the engine:
  1. settles markets that have resolved (notify),
  2. manages open positions: take-profit / stop-loss / near-resolution exits
     and gain-milestone alerts (notify),
  3. detects new signals and opens paper (and optional live) positions (notify),
  4. emits a periodic portfolio heartbeat.

I/O dependencies (market fetcher, sources, LLM scorer, live broker, notifier)
are injectable so the cycle can be unit-tested offline.
"""

from __future__ import annotations

import time
from typing import Callable

from . import polymarket
from . import sources as sources_mod
from .config import Config
from .models import Market
from .notify import NullNotifier
from .paper import InsufficientFunds, PaperBroker, Portfolio
from .signals import detect, detect_llm

MarketFetcher = Callable[[str, str], "Market | None"]


def _default_market_fetcher(slug: str, market_id: str) -> Market | None:
    if slug:
        return polymarket.fetch_by_slug(slug)
    if market_id:
        return polymarket.fetch_by_id(market_id)
    return None


def resolve_watchlist(cfg: Config, fetcher: MarketFetcher | None = None) -> dict[str, Market]:
    """Resolve every watch entry to a live Market, keyed by slug-or-id.

    Default path batches by slug (cheap for large watchlists). If a per-entry
    `fetcher` is injected (tests), the legacy one-by-one path is used.
    """
    if fetcher is not None:
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

    # Production batch path.
    out = {}
    slug_items = [w for w in cfg.watchlist if w.slug]
    id_items = [w for w in cfg.watchlist if not w.slug and w.id]
    by_slug = polymarket.fetch_by_slugs([w.slug for w in slug_items])
    for w in slug_items:
        m = by_slug.get(w.slug)
        if m:
            out[w.slug] = m
    for w in id_items:
        try:
            m = polymarket.fetch_by_id(w.id)
        except Exception:  # noqa: BLE001
            m = None
        if m:
            out[w.id] = m
    return out


def _current_price(markets: dict[str, Market], pos) -> float | None:
    for m in markets.values():
        if m.id == pos.market_id and pos.outcome_index < len(m.prices):
            return m.prices[pos.outcome_index]
    return None


def markets_price(markets: dict[str, Market], pos) -> float:
    p = _current_price(markets, pos)
    return p if p is not None else pos.avg_price


def maybe_resolve(pf: Portfolio, markets: dict[str, Market], broker: PaperBroker,
                  notifier, log: Callable[[str], None]) -> None:
    """Settle paper positions for any watched market that has resolved."""
    held = {pos.market_id for pos in pf.positions.values()}
    seen_ids: set[str] = set()
    for m in markets.values():
        if m.id in seen_ids or m.id not in held or not m.closed:
            continue
        seen_ids.add(m.id)
        winner = max(range(len(m.prices)), key=lambda i: m.prices[i])
        pnl = broker.resolve(m, winner)
        msg = (f"🏁 Рынок разрешился: победил «{m.outcomes[winner]}» "
               f"[{m.question[:60]}]. Реализовано ${pnl:+.2f}.")
        notifier.send(msg)
        log("  " + msg)


def manage_positions(cfg: Config, pf: Portfolio, markets: dict[str, Market],
                     broker: PaperBroker, notifier, alerts: dict,
                     log: Callable[[str], None]) -> None:
    """Exit (TP/SL/near-resolution) and fire gain-milestone alerts."""
    for key in list(pf.positions.keys()):
        pos = pf.positions[key]
        price = _current_price(markets, pos)
        if price is None or pos.avg_price <= 0:
            continue
        gain = (price - pos.avg_price) / pos.avg_price

        reason = None
        if gain >= cfg.take_profit_pct:
            reason = f"тейк-профит +{gain * 100:.0f}%"
        elif gain <= -cfg.stop_loss_pct:
            reason = f"стоп-лосс {gain * 100:.0f}%"
        elif price >= cfg.exit_price_above:
            reason = f"фиксация у разрешения (цена {price:.2f})"

        if reason is not None:
            _, realized = broker.sell(key, price, reason)
            alerts.pop(key, None)
            icon = "✅" if realized >= 0 else "🛑"
            msg = (f"{icon} Закрываю «{pos.outcome_name}» [{pos.market_question[:50]}] "
                   f"— {reason}. P&L ${realized:+.2f}.")
            notifier.send(msg)
            log("  " + msg)
            continue

        # gain-milestone alerts (notify once per crossed tier)
        last_tier = alerts.get(key, -1)
        new_tier = last_tier
        for i, t in enumerate(cfg.notify_gain_tiers):
            if gain >= t:
                new_tier = max(new_tier, i)
        if new_tier > last_tier:
            alerts[key] = new_tier
            unreal = pos.shares * (price - pos.avg_price)
            msg = (f"📈 +{gain * 100:.0f}% по «{pos.outcome_name}» "
                   f"[{pos.market_question[:50]}] — бумажная прибыль ${unreal:+.2f}. "
                   f"Держу; выйду при +{cfg.take_profit_pct * 100:.0f}% / "
                   f"−{cfg.stop_loss_pct * 100:.0f}% / у разрешения.")
            notifier.send(msg)
            log("  " + msg)


def _summary(pf: Portfolio, prices: dict) -> str:
    return (f"📊 Сводка: equity ${pf.equity(prices):.2f} | "
            f"реализовано ${pf.realized_pnl:+.2f} | "
            f"нереализовано ${pf.unrealized_pnl(prices):+.2f} | "
            f"открыто позиций {len(pf.positions)} | сделок {len(pf.trades)}.")


def run_once(
    cfg: Config,
    pf: Portfolio,
    seen_news: set[str],
    traded_keys: dict[str, float],
    alerts: dict | None = None,
    *,
    market_fetcher: MarketFetcher | None = None,
    sources: list | None = None,
    scorer=None,
    live_broker=None,
    notifier=None,
    log: Callable[[str], None] = print,
) -> list:
    """One full cycle. Mutates pf/seen_news/traded_keys/alerts in place."""
    notifier = notifier or NullNotifier()
    if alerts is None:
        alerts = {}
    if sources is None:
        sources = sources_mod.build_sources(cfg)

    markets = resolve_watchlist(cfg, market_fetcher)
    if not markets:
        log("  no watched markets resolved (empty watchlist?)")
        return []

    broker = PaperBroker(pf, fee_bps=cfg.fee_bps, slippage_bps=cfg.slippage_bps,
                         max_position_usd=cfg.max_position_usd)

    maybe_resolve(pf, markets, broker, notifier, log)
    manage_positions(cfg, pf, markets, broker, notifier, alerts, log)

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
    plan = (f"План выхода: тейк +{cfg.take_profit_pct * 100:.0f}%, "
            f"стоп −{cfg.stop_loss_pct * 100:.0f}%, или фиксация у разрешения.")
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
        msg = (f"🟢 Беру ставку: «{trade.outcome_name}» @ {trade.price:.3f} "
               f"(${trade.cost:.2f}) на «{sig.market.question[:60]}». "
               f"Причина: {sig.rationale}. Уверенность {sig.confidence:.0%}. {plan}")
        notifier.send(msg)
        log("  " + msg)
        if live_broker is not None:
            result = live_broker.execute(sig, cfg.stake_usd, pf)
            log(f"    live: {result.get('status')} {result.get('reason', '')}".rstrip())

    for n in fresh:
        seen_news.add(n.uid)

    prices = {p.key: markets_price(markets, p) for p in pf.positions.values()}
    log(
        f"  equity=${pf.equity(prices):.2f} cash=${pf.cash:.2f} "
        f"unreal=${pf.unrealized_pnl(prices):+.2f} real=${pf.realized_pnl:+.2f} "
        f"positions={len(pf.positions)} trades={len(pf.trades)}"
    )

    # periodic heartbeat summary
    if now - float(alerts.get("_last_heartbeat", 0.0)) >= cfg.notify_heartbeat_sec:
        alerts["_last_heartbeat"] = now
        notifier.send(_summary(pf, prices))

    return executed
