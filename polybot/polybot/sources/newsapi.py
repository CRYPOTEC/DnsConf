"""NewsAPI.org source (https://newsapi.org). Needs NEWSAPI_KEY.

Parsing is split from fetching so it can be unit-tested without network.
"""

from __future__ import annotations

import calendar
import json
import time
import urllib.parse

from ..http_util import get_text
from ..models import NewsItem

ENDPOINT = "https://newsapi.org/v2/everything"


def _parse_iso(text: str | None) -> float:
    if not text:
        return time.time()
    try:
        return calendar.timegm(time.strptime(text, "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, TypeError):
        return time.time()


def parse(payload: dict) -> list[NewsItem]:
    """Convert a NewsAPI response dict into NewsItem objects."""
    items = []
    for art in payload.get("articles", []):
        title = (art.get("title") or "").strip()
        if not title:
            continue
        src = (art.get("source") or {}).get("name") or "newsapi"
        items.append(NewsItem(
            source=f"newsapi:{src}",
            title=title,
            link=art.get("url") or "",
            summary=(art.get("description") or "").strip(),
            published=_parse_iso(art.get("publishedAt")),
        ))
    return items


class NewsApiSource:
    def __init__(self, api_key: str, query: str, page_size: int = 50, timeout: float = 15.0):
        self.api_key = api_key
        self.query = query
        self.page_size = page_size
        self.timeout = timeout
        self.name = "newsapi"

    def fetch(self) -> list[NewsItem]:
        q = urllib.parse.urlencode({
            "q": self.query,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": self.page_size,
            "apiKey": self.api_key,
        })
        payload = json.loads(get_text(f"{ENDPOINT}?{q}", self.timeout))
        return parse(payload)
