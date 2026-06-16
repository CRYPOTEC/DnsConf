import unittest

from polybot.config import Config, WatchItem
from polybot.engine import maybe_resolve, run_once
from polybot.models import Market, NewsItem, Signal
from polybot.paper import PaperBroker, Portfolio


class FakeSource:
    def __init__(self, items):
        self.name = "fake"
        self._items = items

    def fetch(self):
        return self._items


def open_market():
    return Market(id="1", question="US x Iran peace deal?", slug="m",
                  outcomes=["Yes", "No"], prices=[0.40, 0.60], token_ids=["a", "b"])


class ResolveTests(unittest.TestCase):
    def test_closed_market_settles_position(self):
        pf = Portfolio(1000.0)
        broker = PaperBroker(pf)
        # buy a Yes position
        sig = Signal(market=open_market(), outcome_index=0, confidence=0.8,
                     rationale="t", news_uid="u", suggested_price=0.40)
        broker.buy(sig, 100.0)  # 250 shares @0.40
        closed = Market(id="1", question="Q", slug="m", outcomes=["Yes", "No"],
                        prices=[0.99, 0.01], token_ids=["a", "b"], closed=True)
        maybe_resolve(pf, {"m": closed}, broker, log=lambda *_: None)
        self.assertEqual(len(pf.positions), 0)
        self.assertAlmostEqual(pf.realized_pnl, 150.0)  # 250*(1-0.4)


class RunOnceTests(unittest.TestCase):
    def test_keyword_cycle_executes_paper_trade(self):
        cfg = Config.load(None)
        cfg.watchlist = [WatchItem(slug="m", match_keywords=["iran"],
                                   bull_keywords=["deal"], bear_keywords=["war"])]
        pf = Portfolio(1000.0)
        seen, traded = set(), {}
        news = [NewsItem(source="x", title="Iran and US reach a deal", link="l1")]
        executed = run_once(
            cfg, pf, seen, traded,
            market_fetcher=lambda slug, mid: open_market(),
            sources=[FakeSource(news)],
            log=lambda *_: None,
        )
        self.assertEqual(len(executed), 1)
        self.assertEqual(executed[0].outcome_name, "Yes")
        self.assertEqual(len(pf.positions), 1)
        # the headline is now marked seen
        self.assertEqual(len(seen), 1)


if __name__ == "__main__":
    unittest.main()
