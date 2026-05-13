"""HFI Research subscriber feed — pulls full post list from logged-in archive."""
from __future__ import annotations

from typing import Any

from playwright.async_api import BrowserContext

from ..db import upsert_news
from .premium_base import PremiumScraper


class HFISubscriber(PremiumScraper):
    name = "hfi_paid"
    URL = "https://www.hfir.com/archive"

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        page = await ctx.new_page()
        await page.goto(self.URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2500)

        # Substack archive: anchors with /p/<slug>
        anchors = await page.query_selector_all("a[href*='/p/']")
        items: list[dict] = []
        seen: set[str] = set()
        for a in anchors[:30]:
            href = await a.get_attribute("href")
            text = (await a.inner_text() or "").strip()
            if not href or not text or len(text) < 5:
                continue
            url = href if href.startswith("http") else f"https://www.hfir.com{href}"
            if url in seen:
                continue
            seen.add(url)
            items.append({
                "title": text[:300],
                "url": url,
                "source": "hfi_subscriber",
                "tags": ["hfi", "subscriber", "oil"],
            })

        new = upsert_news(items)
        await page.close()
        return {"items_found": len(items), "items_new": new}
