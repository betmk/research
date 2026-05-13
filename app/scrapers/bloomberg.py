"""Bloomberg news scraper — uses persistent Chrome profile + playwright-stealth
to defeat the bot challenge that Bloomberg serves to vanilla Playwright.

Bloomberg flagged my profile after rapid requests, so we:
  1) Apply playwright-stealth to mask automation fingerprints
  2) Use a realistic viewport, locale, geolocation
  3) Jitter between page loads
  4) Crawl multiple sections to amortize the per-session cost
  5) Retry once on bot challenge with extra warm-up time
"""
from __future__ import annotations

import asyncio
import random
import re
from typing import Any

from playwright.async_api import BrowserContext, Page
from playwright_stealth import Stealth

from ..db import upsert_news
from .premium_base import PremiumScraper

_BBG_ARTICLE_RE = re.compile(r"/news/(?:articles|features)/")

_BBG_PAGES: list[tuple[str, str]] = [
    ("https://www.bloomberg.com/energy", "energy"),
    ("https://www.bloomberg.com/markets/commodities/energy", "commodities-energy"),
    ("https://www.bloomberg.com/middleeast", "middle-east"),
]

_OIL_KEYWORDS = {
    "oil", "crude", "brent", "wti", "opec", "iran", "saudi", "aramco",
    "hormuz", "diesel", "gasoline", "lng", "natgas", "refinery", "barrel",
    "shale", "pipeline", "tanker", "exxon", "chevron", "shell",
    "energy", "petroleum", "fuel", "gas", "gulf",
}


def _is_oil_relevant(title: str, url: str) -> bool:
    text = f"{title.lower()} {url.lower()}"
    return any(kw in text for kw in _OIL_KEYWORDS)


async def _is_bot_blocked(page: Page) -> bool:
    title = (await page.title()).lower()
    return "robot" in title or "captcha" in title or "are you" in title


async def _warm_up(page: Page) -> None:
    """Visit homepage first to look more human, then go to target."""
    try:
        await page.goto("https://www.bloomberg.com/", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(random.uniform(2000, 3500))
    except Exception:  # noqa: BLE001
        pass


class BloombergEnergy(PremiumScraper):
    name = "bloomberg_oil"

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        # Apply stealth to every page in this context
        stealth = Stealth()
        await stealth.apply_stealth_async(ctx)

        items: list[dict] = []
        seen: set[str] = set()
        bot_hit = False

        for idx, (url, section_tag) in enumerate(_BBG_PAGES):
            page = await ctx.new_page()
            try:
                if idx == 0:
                    await _warm_up(page)

                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(random.uniform(2500, 4000))

                if await _is_bot_blocked(page):
                    # One retry with longer warm-up
                    await _warm_up(page)
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(random.uniform(3500, 5500))
                    if await _is_bot_blocked(page):
                        bot_hit = True
                        continue

                # Scroll to trigger lazy load
                for _ in range(3):
                    await page.evaluate(
                        "window.scrollTo(0, document.body.scrollHeight)"
                    )
                    await page.wait_for_timeout(random.uniform(700, 1100))

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
                    if not _BBG_ARTICLE_RE.search(href):
                        continue
                    canonical = href.split("?")[0]
                    full = canonical if canonical.startswith("http") else f"https://www.bloomberg.com{canonical}"
                    if full in seen:
                        continue
                    if not _is_oil_relevant(text, full):
                        continue
                    seen.add(full)
                    items.append({
                        "title": text[:300],
                        "url": full,
                        "source": "bloomberg",
                        "tags": ["bloomberg", "energy", section_tag],
                    })
            except Exception:  # noqa: BLE001
                pass
            finally:
                try:
                    await page.close()
                except Exception:  # noqa: BLE001
                    pass
                # Polite jitter between sections
                await asyncio.sleep(random.uniform(1.5, 3.0))

        new = upsert_news(items)
        result: dict[str, Any] = {"items_found": len(items), "items_new": new}
        if bot_hit:
            result["partial_bot_block"] = True
        return result
