"""Configuration loading with sane defaults.

Config is plain JSON so the bot needs no third-party YAML dependency.
A user overrides defaults by copying ``config.example.json`` to
``config.json`` (gitignored) and editing it.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


DEFAULTS = {
    # --- portfolio / risk ---
    "starting_cash": 1000.0,     # virtual USDC
    "stake_usd": 25.0,           # per-trade stake
    "max_position_usd": 100.0,   # cap of cost basis per (market, outcome)
    "min_confidence": 0.5,       # ignore weaker signals
    "fee_bps": 0.0,              # simulated taker fee (Polymarket is ~0)
    "slippage_bps": 50.0,        # adverse fill vs. quoted price
    "cooldown_sec": 3600,        # min seconds between trades on same outcome

    # --- loop ---
    "poll_interval_sec": 120,

    # --- data sources ---
    "news_feeds": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.npr.org/1004/rss.xml",
        "https://rss.cnn.com/rss/edition_world.rss",
    ],

    # --- watchlist ---
    # Each entry binds a real Polymarket market (by slug or id) to keyword
    # rules. `match_keywords` decide relevance; `bull_keywords` push the
    # "Yes" outcome, `bear_keywords` push "No".
    "watchlist": [],

    # storage
    "state_file": "state.json",
}


@dataclass
class WatchItem:
    slug: str = ""
    id: str = ""
    match_keywords: list[str] = field(default_factory=list)
    bull_keywords: list[str] = field(default_factory=list)
    bear_keywords: list[str] = field(default_factory=list)
    # optional: outcome names to map bull/bear onto (defaults Yes/No)
    bull_outcome: str = "Yes"
    bear_outcome: str = "No"


@dataclass
class Config:
    starting_cash: float
    stake_usd: float
    max_position_usd: float
    min_confidence: float
    fee_bps: float
    slippage_bps: float
    cooldown_sec: int
    poll_interval_sec: int
    news_feeds: list[str]
    watchlist: list[WatchItem]
    state_file: str

    @classmethod
    def load(cls, path: str | None = None) -> "Config":
        data = dict(DEFAULTS)
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                data.update(json.load(fh))
        watch = [WatchItem(**w) for w in data.get("watchlist", [])]
        return cls(
            starting_cash=float(data["starting_cash"]),
            stake_usd=float(data["stake_usd"]),
            max_position_usd=float(data["max_position_usd"]),
            min_confidence=float(data["min_confidence"]),
            fee_bps=float(data["fee_bps"]),
            slippage_bps=float(data["slippage_bps"]),
            cooldown_sec=int(data["cooldown_sec"]),
            poll_interval_sec=int(data["poll_interval_sec"]),
            news_feeds=list(data["news_feeds"]),
            watchlist=watch,
            state_file=str(data["state_file"]),
        )
