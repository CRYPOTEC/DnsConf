"""RSS/Atom source — wraps the stdlib feed reader in news.py."""

from __future__ import annotations

from .. import news as news_mod
from ..models import NewsItem


class RssSource:
    def __init__(self, feeds: list[str], timeout: float = 15.0):
        self.feeds = feeds
        self.timeout = timeout
        self.name = "rss"

    def fetch(self) -> list[NewsItem]:
        return news_mod.fetch_all(self.feeds, self.timeout)
