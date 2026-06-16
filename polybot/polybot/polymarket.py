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


def fetch_by_slugs(slugs: list[str], chunk: int = 40,
                   timeout: float = 20.0) -> dict[str, Market]:
    """Resolve many markets by slug in batched requests (Gamma accepts repeated
    `slug=` params). Returns {slug: Market}. Far cheaper than one call each."""
    out: dict[str, Market] = {}
    for i in range(0, len(slugs), chunk):
        part = slugs[i:i + chunk]
        q = "&".join("slug=" + urllib.parse.quote(s) for s in part)
        url = f"{GAMMA}?limit=100&{q}"
        try:
            data = json.loads(get_text(url, timeout))
        except Exception:  # noqa: BLE001 - one bad chunk shouldn't sink the rest
            continue
        for raw in data:
            m = _parse_market(raw)
            if m and m.slug:
                out[m.slug] = m
    return out


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
