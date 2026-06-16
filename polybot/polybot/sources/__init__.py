"""Pluggable news sources.

A Source yields NewsItem objects from somewhere (RSS, NewsAPI, X/Twitter, a
websocket stream). The engine asks every configured source for items each
cycle and merges + de-duplicates them.

Secrets come from the environment, never config:
  NEWSAPI_KEY, TWITTER_BEARER_TOKEN
"""

from __future__ import annotations

import os

from ..config import Config
from ..models import NewsItem
from .base import Source
from .rss import RssSource
from .newsapi import NewsApiSource
from .twitter import TwitterSource

__all__ = ["Source", "RssSource", "NewsApiSource", "TwitterSource",
           "build_sources", "fetch_all"]


def build_sources(cfg: Config) -> list[Source]:
    """Construct the enabled sources from config + environment."""
    sources: list[Source] = []
    if cfg.news_feeds:
        sources.append(RssSource(cfg.news_feeds))
    if cfg.newsapi_query and os.environ.get("NEWSAPI_KEY"):
        sources.append(NewsApiSource(os.environ["NEWSAPI_KEY"], cfg.newsapi_query))
    if cfg.twitter_query and os.environ.get("TWITTER_BEARER_TOKEN"):
        sources.append(TwitterSource(os.environ["TWITTER_BEARER_TOKEN"], cfg.twitter_query))
    if cfg.websocket_url:
        # Imported lazily — depends on the optional `websockets` package.
        from .stream import WebSocketSource
        sources.append(WebSocketSource(cfg.websocket_url))
    return sources


def fetch_all(sources: list[Source]) -> list[NewsItem]:
    """Fetch from every source; failures are isolated. Newest first, deduped."""
    out: list[NewsItem] = []
    seen: set[str] = set()
    for src in sources:
        try:
            items = src.fetch()
        except Exception as exc:  # noqa: BLE001 - one source must not kill the rest
            print(f"  ! source {src.name} failed: {exc}")
            continue
        for it in items:
            if it.uid not in seen:
                seen.add(it.uid)
                out.append(it)
    out.sort(key=lambda i: i.published, reverse=True)
    return out
