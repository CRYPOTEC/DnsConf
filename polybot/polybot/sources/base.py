"""Source protocol."""

from __future__ import annotations

from typing import Protocol

from ..models import NewsItem


class Source(Protocol):
    name: str

    def fetch(self) -> list[NewsItem]:
        """Return the latest items this source knows about."""
        ...
