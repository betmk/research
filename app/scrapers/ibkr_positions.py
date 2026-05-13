"""IBKR positions scraper — pulls current account positions on each tick.

Writes to a `positions` snapshot table (TRUNCATE + INSERT — we only care
about the current snapshot, not the time-series of position changes).
"""
from __future__ import annotations

from typing import Any

from .. import ibkr
from ..db import get_conn
from .base import BaseScraper


class IBKRPositions(BaseScraper):
    name = "ibkr_positions"

    async def fetch(self) -> dict[str, Any]:
        positions = await ibkr.get_positions()
        if not positions:
            return {"items_found": 0, "items_new": 0}

        with get_conn() as conn:
            conn.execute("DELETE FROM positions")
            for p in positions:
                conn.execute(
                    """
                    INSERT INTO positions
                      (symbol, local_symbol, sec_type, exchange, currency,
                       position, avg_cost, market_price, market_value,
                       unrealized_pnl, account)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        p["symbol"], p["local_symbol"], p["sec_type"],
                        p["exchange"], p["currency"], p["position"],
                        p["avg_cost"], p["market_price"], p["market_value"],
                        p["unrealized_pnl"], p["account"],
                    ],
                )
        return {"items_found": len(positions), "items_new": len(positions)}
