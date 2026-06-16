import unittest

from polybot.models import Market, Signal
from polybot.paper import InsufficientFunds, PaperBroker, Portfolio


def make_market():
    return Market(
        id="1", question="Q?", slug="q",
        outcomes=["Yes", "No"], prices=[0.50, 0.50],
        token_ids=["a", "b"],
    )


def make_signal(market, idx=0, price=0.50):
    return Signal(
        market=market, outcome_index=idx, confidence=0.7,
        rationale="test", news_uid="u1", suggested_price=price,
    )


class BuyTests(unittest.TestCase):
    def test_buy_decrements_cash_and_adds_shares(self):
        pf = Portfolio(1000.0)
        broker = PaperBroker(pf)  # no fee/slippage
        trade = broker.buy(make_signal(make_market()), stake_usd=50.0)
        self.assertAlmostEqual(pf.cash, 950.0)
        self.assertAlmostEqual(trade.shares, 100.0)  # 50 / 0.50
        self.assertEqual(len(pf.positions), 1)

    def test_slippage_raises_fill_price(self):
        pf = Portfolio(1000.0)
        broker = PaperBroker(pf, slippage_bps=100.0)  # +1%
        trade = broker.buy(make_signal(make_market()), stake_usd=50.0)
        self.assertAlmostEqual(trade.price, 0.505)

    def test_max_position_enforced(self):
        pf = Portfolio(1000.0)
        broker = PaperBroker(pf, max_position_usd=60.0)
        sig = make_signal(make_market())
        broker.buy(sig, stake_usd=50.0)
        with self.assertRaises(InsufficientFunds):
            broker.buy(sig, stake_usd=50.0)  # 50+50 > 60

    def test_insufficient_cash(self):
        pf = Portfolio(10.0)
        broker = PaperBroker(pf)
        with self.assertRaises(InsufficientFunds):
            broker.buy(make_signal(make_market()), stake_usd=50.0)


class ResolveTests(unittest.TestCase):
    def test_winning_resolution_pays_out(self):
        pf = Portfolio(1000.0)
        broker = PaperBroker(pf)
        m = make_market()
        broker.buy(make_signal(m, idx=0), stake_usd=50.0)  # 100 Yes shares @0.50
        realized = broker.resolve(m, winning_outcome_index=0)
        self.assertAlmostEqual(realized, 50.0)        # 100*1 - 100*0.5
        self.assertAlmostEqual(pf.cash, 1050.0)
        self.assertEqual(len(pf.positions), 0)

    def test_losing_resolution(self):
        pf = Portfolio(1000.0)
        broker = PaperBroker(pf)
        m = make_market()
        broker.buy(make_signal(m, idx=0), stake_usd=50.0)
        realized = broker.resolve(m, winning_outcome_index=1)  # No wins
        self.assertAlmostEqual(realized, -50.0)
        self.assertAlmostEqual(pf.cash, 950.0)


class MarkToMarketTests(unittest.TestCase):
    def test_unrealized_pnl(self):
        pf = Portfolio(1000.0)
        broker = PaperBroker(pf)
        m = make_market()
        broker.buy(make_signal(m, idx=0), stake_usd=50.0)  # 100 @0.50
        prices = {"1:0": 0.60}
        self.assertAlmostEqual(pf.unrealized_pnl(prices), 10.0)   # 100*(0.6-0.5)
        self.assertAlmostEqual(pf.equity(prices), 1010.0)


if __name__ == "__main__":
    unittest.main()
