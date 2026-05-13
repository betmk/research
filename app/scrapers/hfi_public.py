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

        # HFI archive uses a list of post links. Defensive parsing — site
        # structure may change. Look for any anchor that points at /p/ which
        # is the Substack-style post path.
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/p/" not in href:
                continue
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            # Resolve relative URLs
            full_url = href if href.startswith("http") else f"https://www.hfir.com{href}"

            # Look for a parent date — varies by template. Try aria-label, sibling.
            published = None
            date_attr = link.get("data-date") or link.get("aria-label")
            if date_attr:
                try:
                    published = datetime.fromisoformat(date_attr.replace("Z", ""))
                except ValueError:
                    pass

            items.append({
                "title": title,
                "url": full_url,
                "source": "hfi_public",
                "summary": None,
                "published_at": published,
                "tags": ["oil", "hfi"],
            })

        # Dedupe by URL within this batch (page may list same post twice)
        seen: set[str] = set()
        unique_items = []
        for item in items:
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            unique_items.append(item)

        new_count = upsert_news(unique_items)
        return {
            "items_found": len(unique_items),
            "items_new": new_count,
            "latest": unique_items[0]["title"] if unique_items else None,
        }
