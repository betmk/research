"""Bloomberg Energy news scraper — uses persistent Chrome profile for subscriber access.

Matches /news/articles/ AND /news/features/ — both are article URLs on Bloomberg.
"""
from __future__ import annotations

import re
from typing import Any

from playwright.async_api import BrowserContext

from ..db import upsert_news
from .premium_base import PremiumScraper

_BBG_ARTICLE_RE = re.compile(r"/news/(?:articles|features)/")

# Oil/energy keywords — energy section has plenty of non-oil content too
_OIL_KEYWORDS = {
    "oil", "crude", "brent", "wti", "opec", "iran", "saudi", "aramco",
    "hormuz", "diesel", "gasoline", "lng", "natgas", "refinery", "barrel",
    "shale", "pipeline", "tanker", "exxon", "chevron", "shell",
    "energy", "petroleum", "fuel", "gas", "gulf",
}


def _is_oil_relevant(title: str, url: str) -> bool:
    text = f"{title.lower()} {url.lower()}"
    return any(kw in text for kw in _OIL_KEYWORDS)


class BloombergEnergy(PremiumScraper):
    name = "bloomberg_oil"
    URL = "https://www.bloomberg.com/energy"

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        page = await ctx.new_page()
        try:
            await page.goto(self.URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2500)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

            title = await page.title()
            if "robot" in title.lower() or "captcha" in title.lower():
                return {"items_found": 0, "items_new": 0,
                        "skipped": "bot challenge — needs manual nav in setup script"}

            anchors = await page.evaluate("""() => {
                const seen = new Set();
                const out = [];
                document.querySelectorAll('a[href]').forEach(a => {
                    const href = a.getAttribute('href') || '';
                    const text = (a.innerText || '').trim();
                    if (!text || text.length < 20 || text.length > 250) return;
                    if (seen.has(href)) return;
                    seen.add(href);
                    out.push({href, text});
                });
                return out;
            }""")

            items: list[dict] = []
            seen: set[str] = set()
            for a in anchors:
                href = a["href"]
                text = a["text"]
                if not _BBG_ARTICLE_RE.search(href):
                    continue
                full = href if href.startswith("http") else f"https://www.bloomberg.com{href}"
                if full in seen:
                    continue
                if not _is_oil_relevant(text, full):
                    continue
                seen.add(full)
                items.append({
                    "title": text[:300],
                    "url": full,
                    "source": "bloomberg",
                    "tags": ["bloomberg", "energy"],
                })

            new = upsert_news(items)
            return {"items_found": len(items), "items_new": new}
        finally:
            await page.close()
