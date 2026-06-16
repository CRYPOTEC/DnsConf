import json
import unittest
from types import SimpleNamespace

from polybot.config import WatchItem
from polybot.llm import LLMScorer, Verdict
from polybot.models import Market, NewsItem
from polybot.signals import detect_llm


def make_market():
    return Market(id="1", question="US x Iran peace deal?", slug="iran",
                  outcomes=["Yes", "No"], prices=[0.40, 0.60], token_ids=["a", "b"])


class FakeClient:
    """Mimics anthropic.Anthropic().messages.create(...)."""

    def __init__(self, payload=None, stop_reason="end_turn", raise_exc=None):
        self._payload = payload
        self._stop = stop_reason
        self._raise = raise_exc
        self.messages = SimpleNamespace(create=self._create)
        self.last_kwargs = None

    def _create(self, **kwargs):
        self.last_kwargs = kwargs
        if self._raise:
            raise self._raise
        text = json.dumps(self._payload) if self._payload is not None else "not json"
        block = SimpleNamespace(type="text", text=text)
        # include a leading (empty) thinking block like adaptive thinking does
        thinking = SimpleNamespace(type="thinking", text="")
        return SimpleNamespace(stop_reason=self._stop, content=[thinking, block])


class ScoreTests(unittest.TestCase):
    def test_parses_verdict_and_clamps_confidence(self):
        client = FakeClient({"relevant": True, "direction": "yes",
                             "confidence": 1.7, "rationale": "deal signed"})
        scorer = LLMScorer(client=client)
        v = scorer.score(NewsItem(source="x", title="peace deal", link="l"), make_market())
        self.assertIsNotNone(v)
        self.assertTrue(v.relevant)
        self.assertEqual(v.direction, "yes")
        self.assertEqual(v.confidence, 1.0)  # clamped

    def test_passes_structured_output_and_thinking(self):
        client = FakeClient({"relevant": True, "direction": "no",
                             "confidence": 0.5, "rationale": "x"})
        LLMScorer(client=client, thinking=True, effort="low").score(
            NewsItem(source="x", title="t", link="l"), make_market())
        kw = client.last_kwargs
        self.assertEqual(kw["output_config"]["format"]["type"], "json_schema")
        self.assertEqual(kw["output_config"]["effort"], "low")
        self.assertEqual(kw["thinking"], {"type": "adaptive"})

    def test_refusal_returns_none(self):
        client = FakeClient({"relevant": True, "direction": "yes",
                             "confidence": 0.9, "rationale": "x"}, stop_reason="refusal")
        self.assertIsNone(LLMScorer(client=client).score(
            NewsItem(source="x", title="t", link="l"), make_market()))

    def test_api_error_returns_none(self):
        client = FakeClient(raise_exc=RuntimeError("boom"))
        self.assertIsNone(LLMScorer(client=client).score(
            NewsItem(source="x", title="t", link="l"), make_market()))

    def test_bad_json_returns_none(self):
        client = FakeClient(payload=None)  # produces non-json text
        self.assertIsNone(LLMScorer(client=client).score(
            NewsItem(source="x", title="t", link="l"), make_market()))

    def test_no_client_returns_none(self):
        self.assertIsNone(LLMScorer(client=None).score(
            NewsItem(source="x", title="t", link="l"), make_market()))


class FakeScorer:
    def __init__(self, verdict):
        self.verdict = verdict
        self.calls = 0

    def score(self, news, market):
        self.calls += 1
        return self.verdict


class DetectLlmTests(unittest.TestCase):
    def make_watch(self):
        return WatchItem(slug="iran", match_keywords=["iran"],
                         bull_keywords=[], bear_keywords=[])

    def test_relevance_gate_skips_irrelevant(self):
        scorer = FakeScorer(Verdict(True, "yes", 0.9, "x"))
        news = [NewsItem(source="x", title="tech stocks rally", link="l")]
        sigs = detect_llm(news, {"iran": make_market()}, [self.make_watch()],
                          0.5, scorer)
        self.assertEqual(sigs, [])
        self.assertEqual(scorer.calls, 0)  # never called the model

    def test_yes_verdict_maps_to_bull_outcome(self):
        scorer = FakeScorer(Verdict(True, "yes", 0.8, "deal"))
        news = [NewsItem(source="x", title="Iran deal close", link="l")]
        sigs = detect_llm(news, {"iran": make_market()}, [self.make_watch()],
                          0.5, scorer)
        self.assertEqual(len(sigs), 1)
        self.assertEqual(sigs[0].outcome_name, "Yes")

    def test_low_confidence_filtered(self):
        scorer = FakeScorer(Verdict(True, "yes", 0.3, "weak"))
        news = [NewsItem(source="x", title="Iran maybe", link="l")]
        sigs = detect_llm(news, {"iran": make_market()}, [self.make_watch()], 0.5, scorer)
        self.assertEqual(sigs, [])

    def test_max_calls_caps_spend(self):
        scorer = FakeScorer(Verdict(False, "none", 0.0, "x"))
        news = [NewsItem(source="x", title=f"Iran item {i}", link=f"l{i}") for i in range(10)]
        detect_llm(news, {"iran": make_market()}, [self.make_watch()], 0.5,
                   scorer, max_calls=3)
        self.assertEqual(scorer.calls, 3)


if __name__ == "__main__":
    unittest.main()
