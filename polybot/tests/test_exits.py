import unittest

from polybot.config import Config
from polybot.engine import manage_positions
from polybot.models import Market, Position, Signal
from polybot.paper import PaperBroker, Portfolio


class FakeNotifier:
    def __init__(self):
        self.msgs = []
        self.name = "fake"

    def send(self, text):
        self.msgs.append(text)


def market_at(price):
    return Market(id="1", question="Q?", slug="m", outcomes=["Yes", "No"],
                  prices=[price, 1 - price], token_ids=["a", "b"])


def portfolio_with_position(entry, shares=100.0):
    pf = Portfolio(1000.0)
    pos = Position(market_id="1", market_question="Q?", outcome_index=0,
                   outcome_name="Yes", shares=shares, avg_price=entry)
    pf.positions[pos.key] = pos
    return pf


def cfg_exits():
    cfg = Config.load(None)
    cfg.take_profit_pct = 0.5
    cfg.stop_loss_pct = 0.5
    cfg.exit_price_above = 0.97
    cfg.notify_gain_tiers = [0.2, 0.5, 1.0]
    return cfg


class SellTests(unittest.TestCase):
    def test_sell_realizes_profit(self):
        pf = portfolio_with_position(0.50)
        broker = PaperBroker(pf)  # no fee/slippage
        trade, realized = broker.sell("1:0", 0.60, "tp")
        self.assertEqual(trade.side, "SELL")
        self.assertAlmostEqual(realized, 10.0)       # 100*(0.6-0.5)
        self.assertAlmostEqual(pf.cash, 1060.0)      # +100*0.6
        self.assertEqual(len(pf.positions), 0)


class ManageTests(unittest.TestCase):
    def run_manage(self, entry, current, cfg=None, alerts=None):
        cfg = cfg or cfg_exits()
        pf = portfolio_with_position(entry)
        broker = PaperBroker(pf)
        notifier = FakeNotifier()
        alerts = alerts if alerts is not None else {}
        manage_positions(cfg, pf, {"m": market_at(current)}, broker,
                         notifier, alerts, log=lambda *_: None)
        return pf, notifier, alerts

    def test_take_profit_exit(self):
        pf, notifier, _ = self.run_manage(0.50, 0.80)  # +60%
        self.assertEqual(len(pf.positions), 0)
        self.assertTrue(any("тейк" in m for m in notifier.msgs))

    def test_stop_loss_exit(self):
        pf, notifier, _ = self.run_manage(0.50, 0.20)  # -60%
        self.assertEqual(len(pf.positions), 0)
        self.assertTrue(any("стоп" in m for m in notifier.msgs))

    def test_near_resolution_exit(self):
        pf, notifier, _ = self.run_manage(0.90, 0.98)  # +9% but price>=0.97
        self.assertEqual(len(pf.positions), 0)
        self.assertTrue(any("фиксация" in m for m in notifier.msgs))

    def test_gain_tier_alert_without_exit(self):
        pf, notifier, alerts = self.run_manage(0.50, 0.62)  # +24%, below TP
        self.assertEqual(len(pf.positions), 1)              # still open
        self.assertEqual(alerts["1:0"], 0)                  # tier 0 (>=20%) fired
        self.assertTrue(any("+24%" in m or "📈" in m for m in notifier.msgs))

    def test_alert_fires_once_per_tier(self):
        cfg = cfg_exits()
        pf = portfolio_with_position(0.50)
        broker = PaperBroker(pf)
        notifier = FakeNotifier()
        alerts = {"1:0": 0}  # tier 0 already notified
        manage_positions(cfg, pf, {"m": market_at(0.62)}, broker, notifier,
                         alerts, log=lambda *_: None)
        self.assertEqual(notifier.msgs, [])  # no re-alert for the same tier


if __name__ == "__main__":
    unittest.main()
