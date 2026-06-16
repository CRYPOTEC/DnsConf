"""Read-only Polymarket market data via the public Gamma API.

We only *read* prices here — order placement is intentionally absent in the
paper-trading build. Live execution would live in a separate, guarded module
using the CLOB API and a funded wallet.
"""

from __future__ import annotations

import json
import urllib.parse

from .http_util import get_text
from .models import Market

GAMMA = "https://gamma-api.polymarket.com/markets"


def _parse_market(raw: dict) -> Market | None:
    """Convert a Gamma JSON record into a Market. Returns None if unusable."""
    try:
        outcomes = json.loads(raw.get("outcomes") or "[]")
        prices = [float(p) for p in json.loads(raw.get("outcomePrices") or "[]")]
        token_ids = json.loads(raw.get("clobTokenIds") or "[]")
    except (ValueError, TypeError):
        return None
    if not outcomes or len(outcomes) != len(prices):
        return None
    return Market(
        id=str(raw.get("id", "")),
        question=raw.get("question", ""),
        slug=raw.get("slug", ""),
        outcomes=outcomes,
        prices=prices,
        token_ids=token_ids,
        end_date=raw.get("endDate"),
        closed=bool(raw.get("closed", False)),
        best_bid=raw.get("bestBid"),
        best_ask=raw.get("bestAsk"),
    )


def fetch_by_slug(slug: str, timeout: float = 15.0) -> Market | None:
    q = urllib.parse.urlencode({"slug": slug})
    data = json.loads(get_text(f"{GAMMA}?{q}", timeout))
    for raw in data:
        m = _parse_market(raw)
        if m:
            return m
    return None


def fetch_by_id(market_id: str, timeout: float = 15.0) -> Market | None:
    data = json.loads(get_text(f"{GAMMA}/{market_id}", timeout))
    raw = data[0] if isinstance(data, list) else data
    return _parse_market(raw)


def fetch_top(limit: int = 20, timeout: float = 15.0) -> list[Market]:
    """Most-active open markets — handy for discovering slugs."""
    q = urllib.parse.urlencode({
        "limit": limit,
        "active": "true",
        "closed": "false",
        "order": "volume24hr",
        "ascending": "false",
    })
    data = json.loads(get_text(f"{GAMMA}?{q}", timeout))
    out = []
    for raw in data:
        m = _parse_market(raw)
        if m:
            out.append(m)
    return out
