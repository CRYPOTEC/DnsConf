"""Turn news + watchlist rules into trade signals.

Deterministic keyword strategy: relevance (match_keywords) gates a market,
then directional keywords (bull -> Yes, bear -> No) decide the side and
confidence. This is intentionally simple and testable; an LLM-scored
variant can be slotted in later behind the same `detect` interface.
"""

from __future__ import annotations

from .config import WatchItem
from .models import Market, NewsItem, Signal


def _count_hits(haystack: str, needles: list[str]) -> tuple[int, bool, bool]:
    """Return (#matches, any_in_title, any_match) for needles in haystack.

    `haystack` is "title\\nsummary"; the first line is treated as the title.
    """
    title = haystack.split("\n", 1)[0].lower()
    full = haystack.lower()
    count = 0
    in_title = False
    for n in needles:
        n = n.lower().strip()
        if not n:
            continue
        if n in full:
            count += 1
            if n in title:
                in_title = True
    return count, in_title, count > 0


def score(news: NewsItem, item: WatchItem) -> tuple[int, bool, float, str] | None:
    """Score one news item against one watch rule.

    Returns (outcome_choice, _, confidence, rationale) where outcome_choice
    is +1 for the bull outcome and -1 for the bear outcome, or None if the
    item is irrelevant or directionally ambiguous.
    """
    text = news.text
    _, _, relevant = _count_hits(text, item.match_keywords)
    if not relevant:
        return None

    bull_hits, bull_title, bull_any = _count_hits(text, item.bull_keywords)
    bear_hits, bear_title, bear_any = _count_hits(text, item.bear_keywords)

    if bull_any == bear_any:  # neither, or conflicting -> no clean edge
        return None

    if bull_any:
        choice, hits, in_title, word = 1, bull_hits, bull_title, "bull"
    else:
        choice, hits, in_title, word = -1, bear_hits, bear_title, "bear"

    confidence = 0.5 + 0.1 * (hits - 1) + (0.15 if in_title else 0.0)
    confidence = max(0.0, min(0.95, confidence))
    rationale = (
        f"{word} signal: {hits} keyword hit(s)"
        f"{' in headline' if in_title else ''} | \"{news.title[:80]}\""
    )
    return choice, in_title, confidence, rationale


def detect(
    news_items: list[NewsItem],
    markets: dict[str, Market],   # keyed by watch-item id used below
    watch: list[WatchItem],
    min_confidence: float,
) -> list[Signal]:
    """Produce signals for all (news, rule) pairs that clear the threshold.

    `markets` maps a watch key (slug or id) to its resolved Market.
    """
    signals: list[Signal] = []
    for item in watch:
        key = item.slug or item.id
        market = markets.get(key)
        if market is None:
            continue
        bull_idx = market.outcome_index(item.bull_outcome)
        bear_idx = market.outcome_index(item.bear_outcome)
        if bull_idx < 0 or bear_idx < 0:
            continue
        for news in news_items:
            res = score(news, item)
            if res is None:
                continue
            choice, _, confidence, rationale = res
            if confidence < min_confidence:
                continue
            outcome_idx = bull_idx if choice == 1 else bear_idx
            signals.append(Signal(
                market=market,
                outcome_index=outcome_idx,
                confidence=confidence,
                rationale=rationale,
                news_uid=news.uid,
                suggested_price=market.price_of(outcome_idx),
            ))
    return signals


def detect_llm(
    news_items: list[NewsItem],
    markets: dict[str, Market],
    watch: list[WatchItem],
    min_confidence: float,
    scorer,                       # duck-typed: .score(news, market) -> Verdict|None
    max_calls: int = 20,
) -> list[Signal]:
    """LLM-scored detection.

    The keyword `match_keywords` still gate relevance (a cheap pre-filter that
    bounds how many paid LLM calls we make); Claude then judges direction and
    confidence. Falls through to nothing if the scorer returns None.
    """
    signals: list[Signal] = []
    calls = 0
    for item in watch:
        key = item.slug or item.id
        market = markets.get(key)
        if market is None:
            continue
        bull_idx = market.outcome_index(item.bull_outcome)
        bear_idx = market.outcome_index(item.bear_outcome)
        if bull_idx < 0 or bear_idx < 0:
            continue
        for news in news_items:
            _, _, relevant = _count_hits(news.text, item.match_keywords)
            if not relevant:
                continue
            if calls >= max_calls:
                return signals
            verdict = scorer.score(news, market)
            calls += 1
            if verdict is None or not verdict.relevant:
                continue
            if verdict.direction == "yes":
                outcome_idx = bull_idx
            elif verdict.direction == "no":
                outcome_idx = bear_idx
            else:
                continue
            if verdict.confidence < min_confidence:
                continue
            signals.append(Signal(
                market=market,
                outcome_index=outcome_idx,
                confidence=verdict.confidence,
                rationale=f"LLM: {verdict.rationale}",
                news_uid=news.uid,
                suggested_price=market.price_of(outcome_idx),
            ))
    return signals
