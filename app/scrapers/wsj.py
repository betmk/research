"""WSJ Oil & Gas news scraper — uses saved auth state for subscriber access."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from playwright.async_api import BrowserContext

from ..db import upsert_news
from .premium_base import PremiumScraper


class WSJOil(PremiumScraper):
    name = "wsj_oil"
    URL = "https://www.wsj.com/news/business/oil-gas"

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        page = await ctx.new_page()
        await page.goto(self.URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2500)

        # WSJ article cards have data-cy="WSJ_Article" or similar; use a
        # broad article-link selector since DOM changes often.
        anchors = await page.query_selector_all("article a[href*='/articles/']")
        items: list[dict] = []
        seen: set[str] = set()
        for a in anchors[:30]:
            href = await a.get_attribute("href")
            text = (await a.inner_text() or "").strip()
            if not href or not text or len(text) < 10:
                continue
            url = href if href.startswith("http") else f"https://www.wsj.com{href}"
            if url in seen:
                continue
            seen.add(url)
            items.append({
                "title": text[:300],
                "url": url,
                "source": "wsj",
                "tags": ["wsj", "oil"],
            })

        new = upsert_news(items)
        await page.close()
        return {"items_found": len(items), "items_new": new}
