"""Bloomberg Energy news scraper — uses saved auth state."""
from __future__ import annotations

from typing import Any

from playwright.async_api import BrowserContext

from ..db import upsert_news
from .premium_base import PremiumScraper


class BloombergEnergy(PremiumScraper):
    name = "bloomberg_oil"
    URL = "https://www.bloomberg.com/energy"

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        page = await ctx.new_page()
        await page.goto(self.URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # If hit by bot challenge, abort gracefully
        title = await page.title()
        if "robot" in title.lower() or "captcha" in title.lower():
            await page.close()
            return {"items_found": 0, "items_new": 0,
                    "skipped": "bot challenge — needs manual nav once"}

        anchors = await page.query_selector_all("a[href*='/news/articles/']")
        items: list[dict] = []
        seen: set[str] = set()
        for a in anchors[:40]:
            href = await a.get_attribute("href")
            text = (await a.inner_text() or "").strip()
            if not href or not text or len(text) < 10:
                continue
            url = href if href.startswith("http") else f"https://www.bloomberg.com{href}"
            if url in seen:
                continue
            seen.add(url)
            items.append({
                "title": text[:300],
                "url": url,
                "source": "bloomberg",
                "tags": ["bloomberg", "energy"],
            })

        new = upsert_news(items)
        await page.close()
        return {"items_found": len(items), "items_new": new}
