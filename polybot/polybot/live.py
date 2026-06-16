"""Guarded live execution on Polymarket (CLOB).

DANGER: this places REAL orders with REAL USDC. It is OFF by default and
wrapped in layered guards so it cannot fire by accident:

  1. live_enabled must be true in config.
  2. A kill-switch file (default ./STOP) must NOT exist.
  3. Paper track-record gate: require N paper trades and paper P&L >= threshold
     before any live order is allowed ("earn live mode on the simulator first").
  4. Per-trade stake is clamped to live_max_stake_usd.
  5. Daily capital-at-risk is capped at live_daily_loss_limit_usd (you can't
     lose more than you deploy, so a daily deployment cap bounds daily loss).
  6. Trades above live_confirm_above_usd require interactive confirmation.
  7. If the CLOB adapter / wallet key isn't wired, it stays in DRY-RUN and only
     logs the order it *would* have placed.

The actual order placement lives in a thin adapter (ClobAdapter) so the broker
logic is testable without network or keys.
"""

from __future__ import annotations

import os
import time

from .config import Config
from .models import Signal
from .paper import Portfolio


class LiveBroker:
    def __init__(self, cfg: Config, adapter=None, confirm_fn=None, now_fn=time.time):
        self.cfg = cfg
        self.adapter = adapter            # exposes place_order(token_id, price, size, side)
        self.confirm_fn = confirm_fn or self._default_confirm
        self.now_fn = now_fn
        self._day = self._today()
        self.deployed_today = 0.0

    # --- gates -------------------------------------------------------------
    def _today(self) -> str:
        return time.strftime("%Y-%m-%d", time.gmtime(self.now_fn()))

    def _roll_day(self) -> None:
        today = self._today()
        if today != self._day:
            self._day = today
            self.deployed_today = 0.0

    def killswitch_active(self) -> bool:
        return os.path.exists(self.cfg.live_killswitch_file)

    def paper_gate(self, pf: Portfolio) -> tuple[bool, str]:
        if len(pf.trades) < self.cfg.live_min_paper_trades:
            return False, (
                f"paper track record too short "
                f"({len(pf.trades)}/{self.cfg.live_min_paper_trades} trades)"
            )
        if pf.realized_pnl < self.cfg.live_min_paper_pnl:
            return False, (
                f"paper realized P&L ${pf.realized_pnl:.2f} "
                f"< required ${self.cfg.live_min_paper_pnl:.2f}"
            )
        return True, ""

    def _default_confirm(self, signal: Signal, stake: float) -> bool:  # pragma: no cover
        ans = input(
            f"CONFIRM live BUY ${stake:.2f} of '{signal.outcome_name}' @ "
            f"{signal.suggested_price:.3f} [{signal.market.question[:60]}]? (yes/no) "
        )
        return ans.strip().lower() in ("y", "yes")

    # --- execution ---------------------------------------------------------
    def execute(self, signal: Signal, stake: float, pf: Portfolio) -> dict:
        """Attempt a live order. Returns a result dict; never raises on a gate."""
        self._roll_day()

        if not self.cfg.live_enabled:
            return {"status": "disabled", "reason": "live_enabled is false"}
        if self.killswitch_active():
            return {"status": "blocked", "reason": f"kill-switch file "
                    f"'{self.cfg.live_killswitch_file}' present"}

        ok, reason = self.paper_gate(pf)
        if not ok:
            return {"status": "blocked", "reason": reason}

        stake = min(stake, self.cfg.live_max_stake_usd)

        if self.deployed_today + stake > self.cfg.live_daily_loss_limit_usd + 1e-9:
            return {"status": "blocked", "reason": (
                f"daily cap reached "
                f"(${self.deployed_today:.2f}+${stake:.2f} > "
                f"${self.cfg.live_daily_loss_limit_usd:.2f})")}

        if stake > self.cfg.live_confirm_above_usd:
            if not self.confirm_fn(signal, stake):
                return {"status": "declined", "reason": "user did not confirm"}

        price = signal.suggested_price
        size = stake / price if price > 0 else 0.0
        token_id = (signal.market.token_ids[signal.outcome_index]
                    if signal.outcome_index < len(signal.market.token_ids) else "")

        if self.adapter is None:
            return {"status": "dry_run", "reason": "no CLOB adapter wired",
                    "token_id": token_id, "price": price, "size": round(size, 2),
                    "stake": stake}

        try:
            resp = self.adapter.place_order(token_id=token_id, price=price,
                                            size=size, side="BUY")
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "reason": str(exc)}

        self.deployed_today += stake
        return {"status": "placed", "stake": stake, "size": round(size, 2),
                "price": price, "token_id": token_id, "response": resp}


class ClobAdapter:  # pragma: no cover - requires py-clob-client, keys, network
    """Thin wrapper over py-clob-client. Verify against the installed SDK
    version before trusting in production — the CLOB API surface changes.
    """

    def __init__(self, host: str = "https://clob.polymarket.com", chain_id: int = 137):
        from py_clob_client.client import ClobClient

        pk = os.environ.get("POLYMARKET_PK")
        if not pk:
            raise RuntimeError("POLYMARKET_PK env var is required for live trading")
        self._client = ClobClient(host, key=pk, chain_id=chain_id)
        self._client.set_api_creds(self._client.create_or_derive_api_creds())

    def place_order(self, token_id: str, price: float, size: float, side: str):
        from py_clob_client.clob_types import OrderArgs
        from py_clob_client.order_builder.constants import BUY, SELL

        order = self._client.create_order(OrderArgs(
            price=price, size=size,
            side=BUY if side == "BUY" else SELL,
            token_id=token_id,
        ))
        return self._client.post_order(order)


def build_adapter(cfg: Config):  # pragma: no cover
    """Construct a real CLOB adapter, or None if live trading isn't configured."""
    if not cfg.live_enabled or not os.environ.get("POLYMARKET_PK"):
        return None
    try:
        return ClobAdapter()
    except Exception as exc:  # noqa: BLE001
        print(f"  ! could not build CLOB adapter (staying dry-run): {exc}")
        return None
