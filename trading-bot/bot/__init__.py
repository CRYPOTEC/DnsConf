"""Bybit trading bot (spot + linear futures).

Modular, exchange-agnostic engine:
  strategy + risk + indicators are pure logic, reused across backtest,
  paper trading and live trading. Only the exchange adapter changes.
"""

__version__ = "0.1.0"
