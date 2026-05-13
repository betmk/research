"""Oil Not Dead (theoilbandit.substack.com) — public posts."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ..config import SOURCES
from ..db import upsert_news
from .base import BaseScraper


class OilNotDead(BaseScraper):
    name = "oil_not_dead"

    async def fetch(self) -> dict[str, Any]:
        url = SOURCES["oil_not_dead"]
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0 Safari/537.36"
                    )
                },
            )
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        items: list[dict] = []

        # Substack post links live under /p/<slug>
        seen: set[str] = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/p/" not in href:
                continue
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            full_url = href if href.startswith("http") else f"https://theoilbandit.substack.com{href}"
            if full_url in seen:
                continue
            seen.add(full_url)
            items.append({
                "title": title,
                "url": full_url,
                "source": "oil_not_dead",
                "summary": None,
                "tags": ["oil", "oil_not_dead", "substack"],
            })

        new_count = upsert_news(items[:20])
        return {
            "items_found": min(len(items), 20),
            "items_new": new_count,
        }
