"""X/Twitter recent-search source. Needs TWITTER_BEARER_TOKEN.

Uses API v2 GET /2/tweets/search/recent. Parsing is split from fetching for
offline testing. Tweets are treated as low-trust, high-noise input — pair this
source with conservative confidence thresholds (or the LLM strategy).
"""

from __future__ import annotations

import calendar
import json
import time
import urllib.parse
import urllib.request

from ..models import NewsItem

ENDPOINT = "https://api.twitter.com/2/tweets/search/recent"


def _parse_iso(text: str | None) -> float:
    if not text:
        return time.time()
    # Twitter timestamps look like 2026-06-16T18:30:00.000Z
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return calendar.timegm(time.strptime(text, fmt))
        except (ValueError, TypeError):
            continue
    return time.time()


def parse(payload: dict) -> list[NewsItem]:
    """Convert a Twitter v2 search response into NewsItem objects."""
    items = []
    for tw in payload.get("data", []):
        text = (tw.get("text") or "").strip()
        if not text:
            continue
        tid = tw.get("id", "")
        # First line as a pseudo-title, full text as summary.
        title = text.splitlines()[0][:120]
        items.append(NewsItem(
            source="twitter",
            title=title,
            link=f"https://twitter.com/i/web/status/{tid}" if tid else "",
            summary=text,
            published=_parse_iso(tw.get("created_at")),
        ))
    return items


class TwitterSource:
    def __init__(self, bearer_token: str, query: str, max_results: int = 25, timeout: float = 15.0):
        self.bearer_token = bearer_token
        self.query = query
        self.max_results = max_results
        self.timeout = timeout
        self.name = "twitter"

    def fetch(self) -> list[NewsItem]:
        q = urllib.parse.urlencode({
            "query": self.query,
            "max_results": self.max_results,
            "tweet.fields": "created_at",
        })
        req = urllib.request.Request(
            f"{ENDPOINT}?{q}",
            headers={"Authorization": f"Bearer {self.bearer_token}"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
        return parse(payload)
