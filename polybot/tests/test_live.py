import os
import tempfile
import unittest

from polybot.config import Config
from polybot.live import LiveBroker
from polybot.models import Market, Signal
from polybot.paper import Portfolio


def make_signal(price=0.50):
    m = Market(id="1", question="Q?", slug="q", outcomes=["Yes", "No"],
               prices=[price, 1 - price], token_ids=["tok-yes", "tok-no"])
    return Signal(market=m, outcome_index=0, confidence=0.8, rationale="t",
                  news_uid="u", suggested_price=price)


def base_cfg(**overrides):
    cfg = Config.load(None)
    cfg.live_enabled = True
    cfg.live_min_paper_trades = 0
    cfg.live_min_paper_pnl = 0.0
    cfg.live_max_stake_usd = 5.0
    cfg.live_daily_loss_limit_usd = 100.0
    cfg.live_confirm_above_usd = 100.0   # high -> no confirm by default
    cfg.live_killswitch_file = os.path.join(tempfile.gettempdir(), "polybot-no-such-stop")
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


class FakeAdapter:
    def __init__(self):
        self.orders = []

    def place_order(self, token_id, price, size, side):
        self.orders.append((token_id, price, size, side))
        return {"orderId": "ok"}


class LiveGateTests(unittest.TestCase):
    def test_disabled(self):
        cfg = base_cfg(live_enabled=False)
        res = LiveBroker(cfg).execute(make_signal(), 5.0, Portfolio(1000))
        self.assertEqual(res["status"], "disabled")

    def test_killswitch_blocks(self):
        with tempfile.NamedTemporaryFile() as f:
            cfg = base_cfg(live_killswitch_file=f.name)
            res = LiveBroker(cfg).execute(make_signal(), 5.0, Portfolio(1000))
        self.assertEqual(res["status"], "blocked")
        self.assertIn("kill-switch", res["reason"])

    def test_paper_gate_blocks_short_record(self):
        cfg = base_cfg(live_min_paper_trades=50)
        res = LiveBroker(cfg).execute(make_signal(), 5.0, Portfolio(1000))
        self.assertEqual(res["status"], "blocked")
        self.assertIn("track record", res["reason"])

    def test_dry_run_without_adapter_and_stake_clamp(self):
        cfg = base_cfg()
        res = LiveBroker(cfg).execute(make_signal(), 100.0, Portfolio(1000))
        self.assertEqual(res["status"], "dry_run")
        self.assertEqual(res["stake"], 5.0)  # clamped to live_max_stake_usd

    def test_confirmation_declined(self):
        cfg = base_cfg(live_confirm_above_usd=1.0)
        broker = LiveBroker(cfg, adapter=FakeAdapter(), confirm_fn=lambda s, k: False)
        res = broker.execute(make_signal(), 5.0, Portfolio(1000))
        self.assertEqual(res["status"], "declined")

    def test_placed_with_adapter(self):
        adapter = FakeAdapter()
        broker = LiveBroker(base_cfg(), adapter=adapter, confirm_fn=lambda s, k: True)
        res = broker.execute(make_signal(price=0.50), 5.0, Portfolio(1000))
        self.assertEqual(res["status"], "placed")
        self.assertEqual(len(adapter.orders), 1)
        self.assertAlmostEqual(res["size"], 10.0)  # 5 / 0.50
        self.assertAlmostEqual(broker.deployed_today, 5.0)

    def test_daily_cap_blocks(self):
        cfg = base_cfg(live_daily_loss_limit_usd=12.0)
        broker = LiveBroker(cfg, adapter=FakeAdapter(), confirm_fn=lambda s, k: True)
        pf = Portfolio(1000)
        self.assertEqual(broker.execute(make_signal(), 5.0, pf)["status"], "placed")
        self.assertEqual(broker.execute(make_signal(), 5.0, pf)["status"], "placed")
        res = broker.execute(make_signal(), 5.0, pf)  # 15 > 12
        self.assertEqual(res["status"], "blocked")
        self.assertIn("daily cap", res["reason"])


if __name__ == "__main__":
    unittest.main()
