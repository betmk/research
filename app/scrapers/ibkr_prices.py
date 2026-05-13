"""IBKR live-price scraper — replaces the TradingEconomics scraper.

Pulls snapshots for everything in app.ibkr.WATCHLIST on every scheduler tick.
"""
from __future__ import annotations

from typing import Any

from .. import ibkr
from ..db import insert_price
from .base import BaseScraper


class IBKRPrices(BaseScraper):
    name = "ibkr_prices"

    async def fetch(self) -> dict[str, Any]:
        quotes = await ibkr.snapshot_quotes()
        items_new = 0
        for label, q in quotes.items():
            if q.get("price") is None:
                continue
            insert_price({
                "instrument": label,
                "contract": q.get("contract"),
                "price": q.get("price"),
                "bid": q.get("bid"),
                "ask": q.get("ask"),
                "change": q.get("change"),
                "change_pct": q.get("change_pct"),
                "prev_close": q.get("prev_close"),
                "day_high": None,
                "day_low": None,
                "source": "ibkr",
            })
            items_new += 1
        return {
            "items_found": len(quotes),
            "items_new": items_new,
        }
