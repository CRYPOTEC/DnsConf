import os
import unittest

from polybot import sources
from polybot.config import Config
from polybot.models import NewsItem
from polybot.sources import newsapi, twitter


class NewsApiParseTests(unittest.TestCase):
    def test_parse(self):
        payload = {"articles": [
            {"title": "Big news", "url": "http://a", "description": "desc",
             "publishedAt": "2026-06-16T12:00:00Z", "source": {"name": "Reuters"}},
            {"title": "", "url": "http://b"},  # skipped (no title)
        ]}
        items = newsapi.parse(payload)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Big news")
        self.assertEqual(items[0].source, "newsapi:Reuters")


class TwitterParseTests(unittest.TestCase):
    def test_parse(self):
        payload = {"data": [
            {"id": "123", "text": "Breaking: deal reached\nmore detail",
             "created_at": "2026-06-16T18:30:00.000Z"},
            {"id": "124", "text": ""},  # skipped
        ]}
        items = twitter.parse(payload)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Breaking: deal reached")
        self.assertIn("123", items[0].link)


class FakeSource:
    def __init__(self, name, items=None, exc=None):
        self.name = name
        self._items = items or []
        self._exc = exc

    def fetch(self):
        if self._exc:
            raise self._exc
        return self._items


class AggregateTests(unittest.TestCase):
    def test_dedup_and_isolation(self):
        a = NewsItem(source="s", title="same", link="http://x")
        b = NewsItem(source="s", title="same", link="http://x")  # dup uid
        c = NewsItem(source="s", title="other", link="http://y")
        srcs = [
            FakeSource("ok", [a, c]),
            FakeSource("dup", [b]),
            FakeSource("broken", exc=RuntimeError("down")),
        ]
        out = sources.fetch_all(srcs)
        self.assertEqual(len(out), 2)  # a/b deduped, c kept, broken skipped


class BuildSourcesTests(unittest.TestCase):
    def setUp(self):
        for k in ("NEWSAPI_KEY", "TWITTER_BEARER_TOKEN"):
            os.environ.pop(k, None)

    def test_rss_only_by_default(self):
        cfg = Config.load(None)
        srcs = sources.build_sources(cfg)
        self.assertEqual([s.name for s in srcs], ["rss"])

    def test_newsapi_needs_query_and_key(self):
        cfg = Config.load(None)
        cfg.newsapi_query = "iran"
        self.assertEqual([s.name for s in sources.build_sources(cfg)], ["rss"])  # no key
        os.environ["NEWSAPI_KEY"] = "k"
        try:
            names = [s.name for s in sources.build_sources(cfg)]
        finally:
            os.environ.pop("NEWSAPI_KEY", None)
        self.assertIn("newsapi", names)


if __name__ == "__main__":
    unittest.main()
