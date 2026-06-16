import unittest

from polybot.config import WatchItem
from polybot.models import Market, NewsItem
from polybot.signals import detect, score


def make_market():
    return Market(
        id="1", question="US x Iran peace deal?", slug="iran",
        outcomes=["Yes", "No"], prices=[0.40, 0.60],
        token_ids=["a", "b"],
    )


def make_watch():
    return WatchItem(
        slug="iran",
        match_keywords=["iran", "tehran"],
        bull_keywords=["peace deal", "agreement"],
        bear_keywords=["strike", "war"],
    )


class ScoreTests(unittest.TestCase):
    def test_irrelevant_returns_none(self):
        n = NewsItem(source="x", title="Stocks rally on tech earnings", link="l1")
        self.assertIsNone(score(n, make_watch()))

    def test_bull_signal(self):
        n = NewsItem(source="x", title="Iran and US reach peace deal", link="l2")
        res = score(n, make_watch())
        self.assertIsNotNone(res)
        choice, in_title, conf, _ = res
        self.assertEqual(choice, 1)
        self.assertTrue(in_title)

    def test_bear_signal(self):
        n = NewsItem(source="x", title="US launches strike on Iran", link="l3")
        res = score(n, make_watch())
        choice, _, _, _ = res
        self.assertEqual(choice, -1)

    def test_conflicting_is_ambiguous(self):
        n = NewsItem(
            source="x",
            title="Iran peace deal collapses as US prepares strike",
            link="l4",
        )
        self.assertIsNone(score(n, make_watch()))


class DetectTests(unittest.TestCase):
    def test_detect_maps_to_correct_outcome(self):
        market = make_market()
        watch = make_watch()
        news = [NewsItem(source="x", title="Iran and US reach peace deal", link="l5")]
        sigs = detect(news, {"iran": market}, [watch], min_confidence=0.5)
        self.assertEqual(len(sigs), 1)
        self.assertEqual(sigs[0].outcome_name, "Yes")
        self.assertEqual(sigs[0].suggested_price, 0.40)

    def test_min_confidence_filters(self):
        market = make_market()
        watch = make_watch()
        # single bull hit, not in title -> confidence 0.5; raise the bar
        news = [NewsItem(source="x", title="Diplomats meet in Tehran",
                         summary="hopes for an agreement", link="l6")]
        sigs = detect(news, {"iran": market}, [watch], min_confidence=0.9)
        self.assertEqual(sigs, [])


if __name__ == "__main__":
    unittest.main()
