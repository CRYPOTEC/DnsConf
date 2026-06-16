"""Generate a politics watchlist config from live Polymarket data.

Unions the politics-related Gamma tags (via the EVENTS endpoint, which actually
honors the tag filter — the markets endpoint ignores it), keeps tradeable
binary (Yes/No) markets that are actively traded, and auto-derives
`match_keywords` per market (named entities + key terms). Built for the LLM
strategy: direction in politics needs judgment, so bull/bear keywords are left
empty on purpose (keyword mode would otherwise guess direction and place
wrong-way bets).

Usage:  python scripts/build_politics_watchlist.py > config.politics.json
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request

GAMMA_EVENTS = "https://gamma-api.polymarket.com/events"
TAGS = ["politics", "us-politics", "geopolitics", "elections"]
MIN_VOL_24H = 500.0  # only markets actively traded in the last 24h

POLITICS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "https://feeds.npr.org/1014/rss.xml",
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://thehill.com/news/feed/",
]

STOP = {
    "will", "the", "a", "an", "by", "in", "of", "to", "before", "after", "on",
    "at", "this", "that", "be", "is", "are", "was", "were", "does", "do", "did",
    "who", "what", "when", "where", "which", "whom", "whose", "how", "any",
    "more", "than", "or", "and", "for", "with", "vs", "end", "year", "market",
    "resolve", "reach", "his", "her", "their", "its", "it", "as", "from", "into",
    "out", "up", "down", "off", "over", "under", "during", "between", "again",
    "next", "new", "first", "second", "third", "last", "another", "still",
    "say", "says", "said", "get", "gets", "make", "made", "have", "has", "had",
    "win", "wins", "won", "lose", "loses", "lost", "yes", "no", "if", "then",
    "many", "much", "most", "least", "number", "amount", "percent",
    "there", "here", "about", "they", "them", "some", "such", "each", "both",
    "other", "being", "been", "also", "just", "only", "very", "amid", "while",
    "whether", "into", "than", "that", "what", "when",
}
MONTHS = {"january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"}
LEAD = {"will", "who", "what", "when", "which", "how", "is", "are", "does",
        "the", "a", "an"}


def fetch_tag_markets(slug: str) -> list[dict]:
    """All markets from active, open events carrying this tag (paginated)."""
    out, offset = [], 0
    while offset < 6000:
        q = urllib.parse.urlencode({
            "tag_slug": slug, "active": "true", "closed": "false",
            "limit": 100, "offset": offset,
        })
        req = urllib.request.Request(f"{GAMMA_EVENTS}?{q}",
                                     headers={"User-Agent": "polybot/0.1"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            page = json.loads(resp.read().decode("utf-8", "replace"))
        if not page:
            break
        for event in page:
            out.extend(event.get("markets", []))
        if len(page) < 100:
            break
        offset += 100
    return out


def is_yes_no(market: dict) -> bool:
    try:
        outs = [o.strip().lower() for o in json.loads(market.get("outcomes") or "[]")]
    except (ValueError, TypeError):
        return False
    return "yes" in outs and "no" in outs


def vol24h(market: dict) -> float:
    try:
        return float(market.get("volume24hr") or 0)
    except (ValueError, TypeError):
        return 0.0


def tradeable(market: dict) -> bool:
    return (is_yes_no(market) and bool(market.get("slug"))
            and not market.get("closed") and bool(market.get("acceptingOrders"))
            and vol24h(market) >= MIN_VOL_24H)


def keywords(question: str) -> list[str]:
    kws: list[str] = []
    # Named-entity phrases: runs of Capitalized words.
    for phrase in re.findall(r"\b([A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)*)", question):
        words = phrase.split()
        # strip a leading interrogative/article ("Will", "Who", ...)
        while words and words[0].lower() in LEAD:
            words = words[1:]
        if not words:
            continue
        low = " ".join(words).lower()
        if low and low not in MONTHS and not low.isdigit() and low not in kws:
            kws.append(low)
    # Significant lowercase content words as a fallback / supplement.
    for w in re.findall(r"[a-zA-Z]{4,}", question.lower()):
        if w in STOP or w in MONTHS or w in kws:
            continue
        if w not in " ".join(kws):  # skip words already inside an entity phrase
            kws.append(w)
    return kws[:6]


def main() -> None:
    seen: dict[str, dict] = {}
    for tag in TAGS:
        for m in fetch_tag_markets(tag):
            mid = str(m.get("id", ""))
            if mid and mid not in seen and tradeable(m):
                seen[mid] = m

    markets = sorted(seen.values(), key=vol24h, reverse=True)

    watchlist = []
    for m in markets:
        kws = keywords(m.get("question", ""))
        if not kws:
            continue
        watchlist.append({
            "slug": m["slug"],
            "match_keywords": kws,
            "bull_keywords": [],   # LLM decides direction
            "bear_keywords": [],
        })

    config = {
        "starting_cash": 1000.0,
        "stake_usd": 25.0,
        "max_position_usd": 100.0,
        "min_confidence": 0.6,
        "fee_bps": 0.0,
        "slippage_bps": 50.0,
        "cooldown_sec": 3600,
        "poll_interval_sec": 300,
        "strategy": "llm",
        "llm_model": "claude-opus-4-8",
        "llm_effort": "low",
        "llm_thinking": True,
        "llm_max_calls_per_cycle": 80,
        "news_feeds": POLITICS_FEEDS,
        "newsapi_query": "",
        "twitter_query": "",
        "websocket_url": "",
        "watchlist": watchlist,
        "live_enabled": False,
        "live_max_stake_usd": 5.0,
        "live_daily_loss_limit_usd": 20.0,
        "live_confirm_above_usd": 1.0,
        "live_min_paper_trades": 50,
        "live_min_paper_pnl": 0.0,
        "live_killswitch_file": "STOP",
        "state_file": "state.politics.json",
    }
    print(json.dumps(config, ensure_ascii=False, indent=2))
    print(f"# {len(watchlist)} politics markets", file=sys.stderr)


if __name__ == "__main__":
    main()
