"""HFI Research public archive scraper.

No auth needed for public posts. Subscriber posts require login (separate
scraper hfi_subscriber.py once creds are supplied).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ..config import SOURCES
from ..db import upsert_news
from .base import BaseScraper


class HFIPublic(BaseScraper):
    name = "hfi_public"

    async def fetch(self) -> dict[str, Any]:
        url = SOURCES["hfi_archive"]
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
        seen: set[str] = set()

        # HFI archive uses Substack-style /p/<slug> URLs.
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/p/" not in href:
                continue
            # Strip query params so we dedup the same post across variations
            base_href = href.split("?")[0].split("#")[0]
            full_url = base_href if base_href.startswith("http") else f"https://www.hfir.com{base_href}"
            if full_url in seen:
                continue
            seen.add(full_url)
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            items.append({
                "title": title[:300],
                "url": full_url,
                "source": "hfi_public",
                "summary": None,
                "published_at": None,
                "tags": ["oil", "hfi"],
            })

        # Cap at 50 (sane upper bound for the archive page)
        items = items[:50]
        new_count = upsert_news(items)
        return {
            "items_found": len(items),
            "items_new": new_count,
            "latest": items[0]["title"] if items else None,
        }
