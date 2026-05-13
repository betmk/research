"""WSJ news scraper — uses persistent Chrome profile for subscriber access.

WSJ uses slug-with-hash URLs like /business/energy-oil/some-headline-726e2392.
We crawl multiple relevant sections + search endpoints; articles dedup by URL.

The dedicated /business/energy-oil section yields the densest oil content
(~35 articles); /world/middle-east covers Iran/Hormuz; search endpoints
back-fill keyword-specific results.
"""
from __future__ import annotations

import re
from typing import Any

from playwright.async_api import BrowserContext

from ..db import upsert_news
from .premium_base import PremiumScraper

_WSJ_ARTICLE_RE = re.compile(r"/[\w-]+-[0-9a-f]{8}(?:[/?]|$)")

# Crawl multiple sections — section first, search second for breadth.
# Each entry: (url, section_tag, requires_keyword_filter)
_WSJ_PAGES: list[tuple[str, str, bool]] = [
    # Dense oil/energy section — no filter needed, all relevant
    ("https://www.wsj.com/business/energy-oil", "energy-oil", False),
    # Commodities — most relevant
    ("https://www.wsj.com/news/types/commodities", "commodities", False),
    # Middle East — Iran/Hormuz coverage; filter to oil/energy/iran keywords
    ("https://www.wsj.com/world/middle-east", "middle-east", True),
    # Markets/Economy/Business — broader, must filter
    ("https://www.wsj.com/markets", "markets", True),
    ("https://www.wsj.com/economy", "economy", True),
    ("https://www.wsj.com/business", "business", True),
    # Keyword-specific search endpoints
    ("https://www.wsj.com/search?query=oil", "search-oil", True),
    ("https://www.wsj.com/search?query=hormuz", "search-hormuz", False),
    ("https://www.wsj.com/search?query=brent+crude", "search-brent", False),
    ("https://www.wsj.com/search?query=iran+oil", "search-iran", False),
]

# Keywords for filtering broader sections
_OIL_KEYWORDS = {
    "oil", "crude", "brent", "wti", "opec", "iran", "saudi", "aramco",
    "hormuz", "diesel", "gasoline", "lng", "natgas", "refinery", "barrel",
    "shale", "pipeline", "tanker", "exxon", "chevron", "shell", "petrobras",
    "energy", "petroleum", "fuel", "drilling", "rig",
}


def _is_oil_relevant(title: str, url: str) -> bool:
    text = f"{title.lower()} {url.lower()}"
    return any(kw in text for kw in _OIL_KEYWORDS)


class WSJOil(PremiumScraper):
    name = "wsj_oil"

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        items: list[dict] = []
        seen: set[str] = set()

        for url, section_tag, needs_filter in _WSJ_PAGES:
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                await page.wait_for_timeout(2000)
                # Scroll multiple times for lazy-loaded cards
                for _ in range(3):
                    await page.evaluate(
                        "window.scrollTo(0, document.body.scrollHeight)"
                    )
                    await page.wait_for_timeout(800)

                anchors = await page.evaluate("""() => {
                    const seen = new Set();
                    const out = [];
                    document.querySelectorAll('a[href]').forEach(a => {
                        const href = a.getAttribute('href') || '';
                        const text = (a.innerText || '').trim();
                        if (!text || text.length < 20 || text.length > 300) return;
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
                    # Strip query params for canonical URL
                    canonical = href.split("?")[0]
                    full = canonical if canonical.startswith("http") else f"https://www.wsj.com{canonical}"
                    if full in seen:
                        continue
                    if needs_filter and not _is_oil_relevant(text, full):
                        continue
                    seen.add(full)
                    items.append({
                        "title": text[:300],
                        "url": full,
                        "source": "wsj",
                        "tags": ["wsj", "oil", section_tag],
                    })
            except Exception:  # noqa: BLE001
                pass
            finally:
                await page.close()

        new = upsert_news(items)
        return {"items_found": len(items), "items_new": new}
