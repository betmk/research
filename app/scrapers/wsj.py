"""WSJ Oil & Gas news scraper — uses persistent Chrome profile for subscriber access.

WSJ uses slug-with-hash URLs like /world/some-headline-726e2392 (no /articles/
path prefix). Selector matches any anchor whose href ends in 8-hex-char hash.
"""
from __future__ import annotations

import re
from typing import Any

from playwright.async_api import BrowserContext

from ..db import upsert_news
from .premium_base import PremiumScraper

# Article URLs are /section/slug-<8hex>, optionally followed by ?mod=... query.
_WSJ_ARTICLE_RE = re.compile(r"/[\w-]+-[0-9a-f]{8}(?:[/?]|$)")

# Oil/energy keywords to filter from broader sections (oil-gas landing page is
# light right now; we scrape /news/markets too to get more candidates).
_OIL_KEYWORDS = {
    "oil", "crude", "brent", "wti", "opec", "iran", "saudi", "aramco",
    "hormuz", "diesel", "gasoline", "lng", "natgas", "refinery", "barrel",
    "shale", "pipeline", "tanker", "exxon", "chevron", "shell",
    "energy", "petroleum", "fuel",
}

# Pages to scrape in order — first one with results wins, then continue.
_WSJ_PAGES = [
    "https://www.wsj.com/news/business/oil-gas",
    "https://www.wsj.com/news/markets",
    "https://www.wsj.com/news/business",
]


def _is_oil_relevant(title: str, url: str) -> bool:
    text = f"{title.lower()} {url.lower()}"
    return any(kw in text for kw in _OIL_KEYWORDS)


class WSJOil(PremiumScraper):
    name = "wsj_oil"

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        items: list[dict] = []
        seen: set[str] = set()

        for url in _WSJ_PAGES:
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)
                # Scroll to trigger lazy-loaded cards
                await page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )
                await page.wait_for_timeout(1500)

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

                for a in anchors:
                    href = a["href"]
                    text = a["text"]
                    if not _WSJ_ARTICLE_RE.search(href):
                        continue
                    full = href if href.startswith("http") else f"https://www.wsj.com{href}"
                    if full in seen:
                        continue
                    if not _is_oil_relevant(text, full):
                        continue
                    seen.add(full)
                    items.append({
                        "title": text[:300],
                        "url": full,
                        "source": "wsj",
                        "tags": ["wsj", "oil"],
                    })
            except Exception as exc:  # noqa: BLE001
                # Don't bail — other pages may still work
                pass
            finally:
                await page.close()

        new = upsert_news(items)
        return {"items_found": len(items), "items_new": new}
