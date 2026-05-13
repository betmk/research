"""Live price scraper — Brent, ICE Gasoil, NYMEX HO, Murban.

Pulls from TradingEconomics (no auth) as primary, Barchart as fallback.
Barchart pages use JS placeholders that fail in plain HTTP; TradingEconomics
serves price values in the static HTML which is more reliable.
"""
from __future__ import annotations

import re
from typing import Any, Optional

import httpx
from bs4 import BeautifulSoup

from ..db import insert_price
from .base import BaseScraper


_TRADINGECONOMICS_URLS = {
    "BRENT": "https://tradingeconomics.com/commodity/brent-crude-oil",
    "WTI": "https://tradingeconomics.com/commodity/crude-oil",
    "ICE_GASOIL": "https://tradingeconomics.com/commodity/gas-oil",
    "NYMEX_HO": "https://tradingeconomics.com/commodity/heating-oil",
}

_PRICE_RE = re.compile(r"([\d,]+\.\d+)")
_PCT_RE = re.compile(r"(-?\d+\.\d+)\s*%")


def _parse_te_price(html: str) -> dict[str, Optional[float]]:
    """Extract last price + change% from a TradingEconomics commodity page.

    The page renders the last value inside `<div class="market-price">` style
    blocks; structure varies. We look for the first standalone price + the
    first percent. Best-effort.
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    price = None
    change_pct = None

    # Look for "<number> USD/Bbl" pattern
    bbl_match = re.search(r"([\d,]+\.\d+)\s*USD/(?:Bbl|MT|Gal)", text)
    if bbl_match:
        price = float(bbl_match.group(1).replace(",", ""))
    else:
        # Fallback to first standalone large number
        nums = _PRICE_RE.findall(text)
        if nums:
            try:
                price = float(nums[0].replace(",", ""))
            except ValueError:
                pass

    pct_match = _PCT_RE.search(text)
    if pct_match:
        try:
            change_pct = float(pct_match.group(1))
        except ValueError:
            pass

    return {"price": price, "change_pct": change_pct}


class Prices(BaseScraper):
    name = "prices"

    async def fetch(self) -> dict[str, Any]:
        items_found = 0
        items_new = 0

        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            },
        ) as client:
            for instrument, url in _TRADINGECONOMICS_URLS.items():
                try:
                    response = await client.get(url)
                    if response.status_code != 200:
                        continue
                    parsed = _parse_te_price(response.text)
                    if not parsed["price"]:
                        continue
                    insert_price({
                        "instrument": instrument,
                        "contract": None,
                        "price": parsed["price"],
                        "change": None,
                        "change_pct": parsed["change_pct"],
                        "source": "tradingeconomics",
                    })
                    items_found += 1
                    items_new += 1
                except (httpx.HTTPError, ValueError):
                    continue

        return {"items_found": items_found, "items_new": items_new}
