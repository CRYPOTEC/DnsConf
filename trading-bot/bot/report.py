"""Performance reporting for a finished simulation."""
from __future__ import annotations

from typing import List

from .models import Trade


def summarize(trades: List[Trade], starting_balance: float, final_equity: float) -> str:
    n = len(trades)
    if n == 0:
        return (f"No closed trades. Start={starting_balance:.2f} "
                f"End={final_equity:.2f}")

    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]
    gross_profit = sum(t.pnl for t in wins)
    gross_loss = -sum(t.pnl for t in losses)
    total_pnl = sum(t.pnl for t in trades)
    total_fees = sum(t.fees for t in trades)
    win_rate = len(wins) / n * 100
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")
    avg_win = (gross_profit / len(wins)) if wins else 0.0
    avg_loss = (gross_loss / len(losses)) if losses else 0.0
    ret_pct = (final_equity / starting_balance - 1) * 100

    # max drawdown on the closed-trade equity curve
    equity = starting_balance
    peak = equity
    max_dd = 0.0
    for t in trades:
        equity += t.pnl
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak)

    lines = [
        "=" * 48,
        "  BACKTEST / PAPER REPORT",
        "=" * 48,
        f"  Trades:            {n}",
        f"  Win rate:          {win_rate:.1f}%  ({len(wins)}W / {len(losses)}L)",
        f"  Profit factor:     {profit_factor:.2f}",
        f"  Avg win / loss:    {avg_win:.2f} / {avg_loss:.2f}",
        f"  Total fees paid:   {total_fees:.2f}",
        f"  Net PnL:           {total_pnl:+.2f}",
        f"  Max drawdown:      {max_dd * 100:.1f}%",
        "-" * 48,
        f"  Start equity:      {starting_balance:.2f}",
        f"  End equity:        {final_equity:.2f}",
        f"  Return:            {ret_pct:+.2f}%",
        "=" * 48,
    ]
    return "\n".join(lines)
