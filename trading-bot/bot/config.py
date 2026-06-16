"""Configuration loading (JSON file + environment for secrets).

Secrets (API keys) come ONLY from environment variables, never the JSON file:
  BYBIT_API_KEY, BYBIT_API_SECRET
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List

from .engine import SymbolConfig
from .models import Market
from .risk import RiskParams
from .strategy import BreakoutParams


@dataclass
class SimConfig:
    starting_balance: float = 10_000.0
    n_candles: int = 1500
    seed: int = 42
    start_price: float = 50_000.0
    fee_rate: float = 0.00055
    slippage: float = 0.0005


@dataclass
class BotConfig:
    mode: str = "backtest"            # "backtest" | "live"
    env: str = "demo"                 # exchange env for live: demo|testnet|live
    poll_interval: float = 15.0
    candle_limit: int = 200
    state_path: str = "state/bot_state.json"
    symbols: List[SymbolConfig] = field(default_factory=list)
    strategy: BreakoutParams = field(default_factory=BreakoutParams)
    risk: RiskParams = field(default_factory=RiskParams)
    sim: SimConfig = field(default_factory=SimConfig)

    @property
    def api_key(self) -> str:
        return os.environ.get("BYBIT_API_KEY", "")

    @property
    def api_secret(self) -> str:
        return os.environ.get("BYBIT_API_SECRET", "")


def _symbols(raw: list) -> List[SymbolConfig]:
    out = []
    for s in raw:
        out.append(SymbolConfig(
            symbol=s["symbol"],
            market=Market(s.get("market", "linear")),
            interval=str(s.get("interval", "60")),
            leverage=float(s.get("leverage", 3.0)),
        ))
    return out


def load_config(path: str) -> BotConfig:
    with open(path) as f:
        raw = json.load(f)

    cfg = BotConfig()
    cfg.mode = raw.get("mode", cfg.mode)
    cfg.env = raw.get("env", cfg.env)
    cfg.poll_interval = float(raw.get("poll_interval", cfg.poll_interval))
    cfg.candle_limit = int(raw.get("candle_limit", cfg.candle_limit))
    cfg.state_path = raw.get("state_path", cfg.state_path)

    if "symbols" in raw:
        cfg.symbols = _symbols(raw["symbols"])
    if not cfg.symbols:
        cfg.symbols = [SymbolConfig("BTCUSDT", Market.LINEAR, "60", 3.0)]

    s = raw.get("strategy", {})
    cfg.strategy = BreakoutParams(
        entry_period=int(s.get("entry_period", 20)),
        exit_period=int(s.get("exit_period", 10)),
        atr_period=int(s.get("atr_period", 14)),
        atr_stop_mult=float(s.get("atr_stop_mult", 2.0)),
        allow_short=bool(s.get("allow_short", True)),
    )

    r = raw.get("risk", {})
    cfg.risk = RiskParams(
        risk_per_trade=float(r.get("risk_per_trade", 0.01)),
        max_leverage=float(r.get("max_leverage", 3.0)),
        max_daily_loss=float(r.get("max_daily_loss", 0.10)),
        min_notional=float(r.get("min_notional", 5.0)),
    )

    sim = raw.get("sim", {})
    cfg.sim = SimConfig(
        starting_balance=float(sim.get("starting_balance", 10_000.0)),
        n_candles=int(sim.get("n_candles", 1500)),
        seed=int(sim.get("seed", 42)),
        start_price=float(sim.get("start_price", 50_000.0)),
        fee_rate=float(sim.get("fee_rate", 0.00055)),
        slippage=float(sim.get("slippage", 0.0005)),
    )
    return cfg
