import os
import unittest

from polybot.backtest import load, run_backtest
from polybot.config import Config


class BacktestTests(unittest.TestCase):
    def setUp(self):
        self.cfg = Config.load(None)
        here = os.path.dirname(__file__)
        self.data = load(os.path.join(here, "..", "examples", "backtest_sample.json"))

    def test_winning_trade_pnl(self):
        result = run_backtest(self.data, self.cfg)
        # buy 100 @0.40 -> 250 shares; resolves Yes -> 250*(1-0.40) = 150
        self.assertEqual(result["trades"], 1)
        self.assertAlmostEqual(result["realized_pnl"], 150.0)
        self.assertAlmostEqual(result["equity"], 1150.0)
        self.assertEqual(result["open_positions"], 0)

    def test_only_relevant_news_trades(self):
        result = run_backtest(self.data, self.cfg)
        self.assertEqual(result["signals"], 1)  # the unrelated headline is ignored


if __name__ == "__main__":
    unittest.main()
