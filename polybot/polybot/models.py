"""Core data structures shared across the bot."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Market:
    """A Polymarket market snapshot (binary or multi-outcome)."""

    id: str
    question: str
    slug: str
    outcomes: list[str]
    prices: list[float]            # aligned with `outcomes`
    token_ids: list[str]
    end_date: Optional[str] = None
    closed: bool = False
    best_bid: Optional[float] = None
    best_ask: Optional[float] = None

    def price_of(self, outcome_index: int) -> float:
        return self.prices[outcome_index]

    def outcome_index(self, name: str) -> int:
        """Index of an outcome by case-insensitive name. -1 if missing."""
        lowered = name.strip().lower()
        for i, o in enumerate(self.outcomes):
            if o.strip().lower() == lowered:
                return i
        return -1


@dataclass
class NewsItem:
    """A single news headline pulled from an RSS/Atom feed."""

    source: str
    title: str
    link: str
    summary: str = ""
    published: float = field(default_factory=time.time)  # epoch seconds

    @property
    def uid(self) -> str:
        """Stable id used for de-duplication (link first, else title)."""
        basis = (self.link or self.title).strip().lower()
        return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.summary}".strip()


@dataclass
class Signal:
    """A decision to (paper-)buy one outcome of a market."""

    market: Market
    outcome_index: int
    confidence: float          # 0..1
    rationale: str
    news_uid: str
    suggested_price: float

    @property
    def outcome_name(self) -> str:
        return self.market.outcomes[self.outcome_index]


@dataclass
class Position:
    market_id: str
    market_question: str
    outcome_index: int
    outcome_name: str
    shares: float
    avg_price: float

    @property
    def key(self) -> str:
        return f"{self.market_id}:{self.outcome_index}"


@dataclass
class Trade:
    ts: float
    market_id: str
    market_question: str
    outcome_name: str
    side: str            # "BUY" (sells/exits can be added later)
    shares: float
    price: float
    cost: float          # cash delta incl. fees (positive = spent)
    rationale: str


def to_jsonable(obj):
    """Recursively convert dataclasses/containers to JSON-safe values."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    return obj


def dumps(obj) -> str:
    return json.dumps(to_jsonable(obj), ensure_ascii=False, indent=2)
