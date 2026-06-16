"""Bybit V5 adapter (spot + linear futures) via ``pybit``.

Supports three environments through one flag:
  * ``env="demo"``   -> Bybit Demo Trading (virtual money, real market data)
  * ``env="testnet"``-> Bybit Testnet
  * ``env="live"``   -> real trading

``pybit`` is imported lazily so the rest of the bot (strategy, risk, backtest)
runs without it installed.

Notes / limitations:
  * ``linear`` positions are read server-side and are authoritative (survive a
    restart). Recommended as the primary market.
  * ``spot`` has no positions endpoint, so an open spot long is tracked in a
    small in-memory cache here (entry price recorded on buy). It is long-only
    and its entry is lost on restart — fine for forward testing, but prefer
    ``linear`` for anything that must be restart-safe.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from ..models import Candle, Fill, Market, Position, Side
from .base import Exchange, InstrumentInfo

log = logging.getLogger("bot.bybit")


class BybitExchange(Exchange):
    name = "bybit"

    def __init__(self, api_key: str, api_secret: str, env: str = "demo",
                 account_type: str = "UNIFIED") -> None:
        from pybit.unified_trading import HTTP  # lazy import

        self.env = env
        self.account_type = account_type
        self.session = HTTP(
            testnet=(env == "testnet"),
            demo=(env == "demo"),
            api_key=api_key,
            api_secret=api_secret,
        )
        # client-side cache for spot longs: symbol -> (qty, entry)
        self._spot_pos: Dict[str, Position] = {}
        self._instrument_cache: Dict[str, InstrumentInfo] = {}

    # ---- market data -----------------------------------------------------
    def get_candles(self, symbol: str, market: Market, interval: str,
                    limit: int = 200) -> List[Candle]:
        r = self.session.get_kline(category=market.value, symbol=symbol,
                                   interval=interval, limit=limit)
        rows = r["result"]["list"]  # newest first
        candles = [
            Candle(ts=int(x[0]), open=float(x[1]), high=float(x[2]),
                   low=float(x[3]), close=float(x[4]), volume=float(x[5]))
            for x in rows
        ]
        candles.reverse()  # oldest first
        return candles

    def _last_price(self, symbol: str, market: Market) -> float:
        r = self.session.get_tickers(category=market.value, symbol=symbol)
        return float(r["result"]["list"][0]["lastPrice"])

    def instrument_info(self, symbol: str, market: Market) -> InstrumentInfo:
        key = f"{market.value}:{symbol}"
        if key in self._instrument_cache:
            return self._instrument_cache[key]
        r = self.session.get_instruments_info(category=market.value, symbol=symbol)
        item = r["result"]["list"][0]
        lot = item["lotSizeFilter"]
        price = item["priceFilter"]
        if market is Market.SPOT:
            qty_step = float(lot.get("basePrecision", lot.get("qtyStep", "0.000001")))
            min_qty = float(lot.get("minOrderQty", qty_step))
        else:
            qty_step = float(lot["qtyStep"])
            min_qty = float(lot["minOrderQty"])
        info = InstrumentInfo(
            symbol=symbol,
            qty_step=qty_step,
            min_qty=min_qty,
            tick_size=float(price["tickSize"]),
            base_coin=item.get("baseCoin", ""),
            quote_coin=item.get("quoteCoin", "USDT"),
        )
        self._instrument_cache[key] = info
        return info

    # ---- account ---------------------------------------------------------
    def get_balance(self) -> float:
        r = self.session.get_wallet_balance(accountType=self.account_type)
        lst = r["result"]["list"]
        if not lst:
            return 0.0
        acct = lst[0]
        equity = acct.get("totalEquity") or acct.get("totalWalletBalance") or "0"
        return float(equity)

    def get_position(self, symbol: str, market: Market) -> Optional[Position]:
        if market is Market.SPOT:
            return self._spot_pos.get(symbol)
        r = self.session.get_positions(category=market.value, symbol=symbol)
        for p in r["result"]["list"]:
            size = float(p["size"])
            if size > 0:
                side = Side.BUY if p["side"] == "Buy" else Side.SELL
                return Position(symbol, market, side, size, float(p["avgPrice"]))
        return None

    # ---- trading ---------------------------------------------------------
    def set_leverage(self, symbol: str, market: Market, leverage: float) -> None:
        if market is not Market.LINEAR:
            return
        try:
            self.session.set_leverage(category="linear", symbol=symbol,
                                      buyLeverage=str(leverage), sellLeverage=str(leverage))
        except Exception as e:  # leverage already set -> Bybit returns an error
            log.debug("set_leverage(%s) ignored: %s", symbol, e)

    def place_market_order(self, symbol: str, market: Market, side: Side,
                           qty: float, reduce_only: bool = False) -> Fill:
        info = self.instrument_info(symbol, market)
        qty_str = self._fmt_qty(qty, info.qty_step)
        params = dict(category=market.value, symbol=symbol, side=side.value,
                      orderType="Market", qty=qty_str)
        if market is Market.LINEAR and reduce_only:
            params["reduceOnly"] = True
        if market is Market.SPOT:
            params["marketUnit"] = "baseCoin"

        self.session.place_order(**params)
        price = self._last_price(symbol, market)
        fee = price * qty * 0.00055

        # maintain spot position cache
        if market is Market.SPOT:
            if side is Side.BUY and not reduce_only:
                self._spot_pos[symbol] = Position(symbol, market, Side.BUY, qty, price)
            else:
                self._spot_pos.pop(symbol, None)

        log.info("ORDER %s %s %s qty=%s @~%.4f", market.value, symbol, side.value, qty_str, price)
        return Fill(symbol, side, qty, price, fee, ts=0, reduce_only=reduce_only)

    @staticmethod
    def _fmt_qty(qty: float, step: float) -> str:
        if step >= 1:
            return str(int(qty))
        decimals = max(0, len(str(step).split(".")[-1].rstrip("0")))
        return f"{qty:.{decimals}f}"
