"""News ingestion from RSS/Atom feeds using only the stdlib XML parser.

SECURITY NOTE: feed content is *untrusted*. Treat titles/summaries as
potentially adversarial — a headline could be crafted to mislead a naive
LLM/keyword strategy (prompt injection / fake breaking news). Signal logic
must stay conservative and never execute on a single unverified item with
real money.
"""

from __future__ import annotations

import calendar
import email.utils
import time
import xml.etree.ElementTree as ET

from .http_util import get
from .models import NewsItem

# Atom namespace
_ATOM = "{http://www.w3.org/2005/Atom}"


def _parse_date(text: str | None) -> float:
    if not text:
        return time.time()
    # RFC 822 (RSS pubDate)
    try:
        dt = email.utils.parsedate_to_datetime(text)
        return dt.timestamp()
    except (TypeError, ValueError, OverflowError):
        pass
    # ISO 8601 (Atom updated/published)
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            return calendar.timegm(time.strptime(text, fmt))
        except ValueError:
            continue
    return time.time()


def _text(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def parse_feed(content: bytes, source: str) -> list[NewsItem]:
    """Parse RSS 2.0 or Atom bytes into NewsItem objects."""
    items: list[NewsItem] = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return items

    # RSS 2.0: <rss><channel><item>
    for item in root.iter("item"):
        items.append(NewsItem(
            source=source,
            title=_text(item.find("title")),
            link=_text(item.find("link")),
            summary=_text(item.find("description")),
            published=_parse_date(_text(item.find("pubDate"))),
        ))

    # Atom: <feed><entry>
    for entry in root.iter(f"{_ATOM}entry"):
        link_el = entry.find(f"{_ATOM}link")
        link = link_el.get("href", "") if link_el is not None else ""
        summary = _text(entry.find(f"{_ATOM}summary")) or _text(entry.find(f"{_ATOM}content"))
        items.append(NewsItem(
            source=source,
            title=_text(entry.find(f"{_ATOM}title")),
            link=link,
            summary=summary,
            published=_parse_date(
                _text(entry.find(f"{_ATOM}updated")) or _text(entry.find(f"{_ATOM}published"))
            ),
        ))

    return [it for it in items if it.title]


def fetch_feed(url: str, timeout: float = 15.0) -> list[NewsItem]:
    return parse_feed(get(url, timeout), source=url)


def fetch_all(urls: list[str], timeout: float = 15.0) -> list[NewsItem]:
    """Fetch every feed; failures are skipped so one bad feed isn't fatal."""
    out: list[NewsItem] = []
    seen: set[str] = set()
    for url in urls:
        try:
            for it in fetch_feed(url, timeout):
                if it.uid not in seen:
                    seen.add(it.uid)
                    out.append(it)
        except Exception:  # noqa: BLE001 - one feed failing must not stop the rest
            continue
    out.sort(key=lambda i: i.published, reverse=True)
    return out
