"""Configuration loading with sane defaults.

Config is plain JSON so the core bot needs no third-party YAML dependency.
A user overrides defaults by copying ``config.example.json`` to
``config.json`` (gitignored) and editing it.

Secrets are NEVER stored here — they come from environment variables:
  ANTHROPIC_API_KEY      LLM signal scoring
  NEWSAPI_KEY            NewsAPI.org source
  TWITTER_BEARER_TOKEN   X/Twitter source
  POLYMARKET_PK          live execution wallet key (live mode only)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


DEFAULTS = {
    # --- portfolio / risk (paper) ---
    "starting_cash": 1000.0,
    "stake_usd": 25.0,
    "max_position_usd": 100.0,
    "min_confidence": 0.5,
    "fee_bps": 0.0,
    "slippage_bps": 50.0,
    "cooldown_sec": 3600,

    # --- loop ---
    "poll_interval_sec": 120,

    # --- signal strategy ---
    # "keyword" (deterministic, offline) or "llm" (Claude-scored, needs key).
    "strategy": "keyword",
    "llm_model": "claude-opus-4-8",
    "llm_effort": "low",            # low | medium | high
    "llm_thinking": True,           # adaptive thinking on/off
    "llm_max_calls_per_cycle": 20,  # cost guard

    # --- data sources ---
    "news_feeds": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.npr.org/1004/rss.xml",
        "https://rss.cnn.com/rss/edition_world.rss",
    ],
    "newsapi_query": "",            # if set + NEWSAPI_KEY present -> enabled
    "twitter_query": "",            # if set + TWITTER_BEARER_TOKEN present -> enabled
    "websocket_url": "",            # optional push source (needs `websockets`)

    # --- watchlist ---
    "watchlist": [],

    # --- live execution (OFF by default; paper-first) ---
    "live_enabled": False,
    "live_max_stake_usd": 5.0,
    "live_daily_loss_limit_usd": 20.0,
    "live_confirm_above_usd": 1.0,   # trades above this need manual confirmation
    "live_min_paper_trades": 50,     # gate: require this many paper trades first
    "live_min_paper_pnl": 0.0,       # gate: require paper realized P&L >= this
    "live_killswitch_file": "STOP",  # if this file exists, no live orders

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
    strategy: str
    llm_model: str
    llm_effort: str
    llm_thinking: bool
    llm_max_calls_per_cycle: int
    news_feeds: list[str]
    newsapi_query: str
    twitter_query: str
    websocket_url: str
    watchlist: list[WatchItem]
    live_enabled: bool
    live_max_stake_usd: float
    live_daily_loss_limit_usd: float
    live_confirm_above_usd: float
    live_min_paper_trades: int
    live_min_paper_pnl: float
    live_killswitch_file: str
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
            strategy=str(data["strategy"]),
            llm_model=str(data["llm_model"]),
            llm_effort=str(data["llm_effort"]),
            llm_thinking=bool(data["llm_thinking"]),
            llm_max_calls_per_cycle=int(data["llm_max_calls_per_cycle"]),
            news_feeds=list(data["news_feeds"]),
            newsapi_query=str(data["newsapi_query"]),
            twitter_query=str(data["twitter_query"]),
            websocket_url=str(data["websocket_url"]),
            watchlist=watch,
            live_enabled=bool(data["live_enabled"]),
            live_max_stake_usd=float(data["live_max_stake_usd"]),
            live_daily_loss_limit_usd=float(data["live_daily_loss_limit_usd"]),
            live_confirm_above_usd=float(data["live_confirm_above_usd"]),
            live_min_paper_trades=int(data["live_min_paper_trades"]),
            live_min_paper_pnl=float(data["live_min_paper_pnl"]),
            live_killswitch_file=str(data["live_killswitch_file"]),
            state_file=str(data["state_file"]),
        )
