"""Bloomberg news scraper — fresh context + filtered cookies + stealth.

Strategy: Bloomberg uses PerimeterX bot detection (cookies _pxhd / _px3 /
reese84). Our persistent profile got flagged after repeated headless hits.
Workaround: launch a NEW browser context for each scrape, import only the
auth cookies (session_id, octagon-jwtToken, DJSESSION-equivalent) from the
persistent profile, and let PerimeterX issue fresh anti-bot cookies in the
new context. Combined with playwright-stealth.

If still blocked, falls back to feeds.bloomberg.com RSS for whatever
sparse content is available there.
"""
from __future__ import annotations

import asyncio
import random
import re
from datetime import datetime
from typing import Any

import feedparser
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from ..db import get_conn, upsert_news
from .base import BaseScraper
from .premium_base import PROFILE_DIR, _profile_lock, profile_ready

_BBG_ARTICLE_RE = re.compile(r"/news/(?:articles|features|newsletters)/")

_BBG_PAGES: list[tuple[str, str]] = [
    ("https://www.bloomberg.com/energy", "energy"),
    ("https://www.bloomberg.com/markets/commodities/energy", "commodities-energy"),
    ("https://www.bloomberg.com/middleeast", "middle-east"),
]

_BBG_RSS_FEEDS = [
    ("https://feeds.bloomberg.com/markets/news.rss", "markets-rss"),
    ("https://feeds.bloomberg.com/economics/news.rss", "economics-rss"),
    ("https://feeds.bloomberg.com/politics/news.rss", "politics-rss"),
    ("https://feeds.bloomberg.com/green/news.rss", "green-rss"),
]

_OIL_KEYWORDS = {
    "oil", "crude", "brent", "wti", "opec", "iran", "saudi", "aramco",
    "hormuz", "diesel", "gasoline", "lng", "natgas", "refinery", "barrel",
    "shale", "pipeline", "tanker", "exxon", "chevron", "shell",
    "energy", "petroleum", "fuel", "gulf",
}

# Auth-shaped cookie names we WANT to import from the persistent profile.
# Anything not in this list (especially _pxhd / _px3 / reese84) stays behind.
_BBG_AUTH_COOKIE_NAMES = {
    "session_id", "session_key", "_session_id_backup",
    "octagon-jwtToken", "_user-token",
    "_breg-uid", "geo_info", "usnatUUID",
    "_reg-csrf-token", "_uetsid",
}


def _is_oil_relevant(title: str, url: str, summary: str = "") -> bool:
    text = f"{title.lower()} {summary.lower()} {url.lower()}"
    return any(kw in text for kw in _OIL_KEYWORDS)


def _read_bloomberg_auth_cookies() -> list[dict]:
    """Read only auth cookies from the persistent Chrome profile's Cookies DB."""
    import sqlite3
    import shutil
    import tempfile

    profile_cookies = PROFILE_DIR / "Default" / "Cookies"
    if not profile_cookies.exists():
        return []

    out: list[dict] = []
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        shutil.copy2(profile_cookies, tmp.name)
        conn = sqlite3.connect(tmp.name)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT host_key, name, value, path, expires_utc, is_secure,
                       is_httponly, samesite
                FROM cookies
                WHERE host_key LIKE '%bloomberg%' OR host_key LIKE '%bbg%'
                """
            )
            for host, name, value, path, expires, secure, httponly, samesite in cur.fetchall():
                if name not in _BBG_AUTH_COOKIE_NAMES:
                    continue
                # Chrome stores some values encrypted; we can't decrypt those
                # outside Chrome, so skip non-readable ones
                if not value:
                    continue
                # Convert Chrome epoch to Unix epoch
                if expires and expires > 0:
                    unix_expires = expires / 1_000_000 - 11644473600
                else:
                    unix_expires = -1
                out.append({
                    "name": name,
                    "value": value,
                    "domain": host,
                    "path": path or "/",
                    "expires": unix_expires,
                    "httpOnly": bool(httponly),
                    "secure": bool(secure),
                    "sameSite": {0: "None", 1: "Lax", 2: "Strict"}.get(samesite, "Lax"),
                })
        finally:
            conn.close()
    return out


async def _rss_fallback() -> list[dict]:
    """Pull oil-relevant items from Bloomberg's open RSS feeds."""
    items: list[dict] = []
    for url, tag in _BBG_RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception:  # noqa: BLE001
            continue
        for e in feed.entries[:30]:
            title = e.get("title", "")
            link = e.get("link", "")
            summary = e.get("summary", "") or e.get("description", "")
            if not _is_oil_relevant(title, link, summary):
                continue
            pub = None
            if e.get("published_parsed"):
                try:
                    pub = datetime(*e.published_parsed[:6])
                except Exception:  # noqa: BLE001
                    pass
            items.append({
                "title": title[:300],
                "url": link.split("?")[0],
                "source": "bloomberg",
                "summary": summary[:500] if summary else None,
                "published_at": pub,
                "tags": ["bloomberg", tag],
            })
    return items


async def _scrape_with_filtered_cookies() -> tuple[list[dict], bool]:
    """Use a fresh non-persistent context with only auth cookies imported."""
    if not profile_ready():
        return [], False

    auth_cookies = _read_bloomberg_auth_cookies()

    items: list[dict] = []
    bot_hit = False

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--no-first-run", "--disable-blink-features=AutomationControlled"],
        )
        try:
            ctx = await browser.new_context(
                viewport={"width": 1440, "height": 900},
                locale="en-US",
                timezone_id="America/New_York",
                user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/130.0.0.0 Safari/537.36"),
            )
            if auth_cookies:
                # Playwright add_cookies needs the right fields
                normalized = []
                for c in auth_cookies:
                    nc = {
                        "name": c["name"], "value": c["value"],
                        "domain": c["domain"], "path": c["path"],
                        "secure": c["secure"], "httpOnly": c["httpOnly"],
                        "sameSite": c["sameSite"],
                    }
                    if c["expires"] > 0:
                        nc["expires"] = c["expires"]
                    normalized.append(nc)
                try:
                    await ctx.add_cookies(normalized)
                except Exception:  # noqa: BLE001
                    pass

            stealth = Stealth()
            await stealth.apply_stealth_async(ctx)

            for idx, (url, section_tag) in enumerate(_BBG_PAGES):
                page = await ctx.new_page()
                try:
                    # Warm-up on homepage first run
                    if idx == 0:
                        try:
                            await page.goto("https://www.bloomberg.com/",
                                              wait_until="domcontentloaded",
                                              timeout=20000)
                            await page.wait_for_timeout(random.uniform(2500, 4000))
                        except Exception:  # noqa: BLE001
                            pass

                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(random.uniform(2500, 4000))

                    title = (await page.title()).lower()
                    if "robot" in title or "captcha" in title:
                        bot_hit = True
                        continue

                    for _ in range(3):
                        await page.evaluate(
                            "window.scrollTo(0, document.body.scrollHeight)"
                        )
                        await page.wait_for_timeout(random.uniform(700, 1100))

                    anchors = await page.evaluate("""() => {
                        const s = new Set(); const o = [];
                        document.querySelectorAll('a[href]').forEach(a => {
                            const h = a.getAttribute('href') || '';
                            const t = (a.innerText||'').trim();
                            if (!t || t.length<20 || t.length>300 || s.has(h)) return;
                            s.add(h); o.push({h, t});
                        });
                        return o;
                    }""")

                    seen: set[str] = set()
                    for a in anchors:
                        href = a["h"]
                        text = a["t"]
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
                            "tags": ["bloomberg", section_tag],
                        })
                except Exception:  # noqa: BLE001
                    pass
                finally:
                    try:
                        await page.close()
                    except Exception:  # noqa: BLE001
                        pass
                    await asyncio.sleep(random.uniform(1.5, 3.0))

            await ctx.close()
        finally:
            await browser.close()

    return items, bot_hit


class BloombergEnergy(BaseScraper):
    """Bloomberg scraper — tries fresh-cookie scrape first, falls back to RSS."""

    name = "bloomberg_oil"

    async def fetch(self) -> dict[str, Any]:
        # Try fresh-context scraping (best content) under the profile lock
        async with _profile_lock:
            scraped, bot_hit = await _scrape_with_filtered_cookies()

        # Always also try RSS — extra free coverage that's bot-immune
        rss_items = await _rss_fallback()

        # Dedup combined list
        all_items: list[dict] = []
        seen: set[str] = set()
        for src in (scraped, rss_items):
            for item in src:
                u = item["url"]
                if u in seen:
                    continue
                seen.add(u)
                all_items.append(item)

        new = upsert_news(all_items)
        result: dict[str, Any] = {
            "items_found": len(all_items),
            "items_new": new,
            "scraped": len(scraped),
            "rss": len(rss_items),
        }
        if bot_hit:
            result["partial_bot_block"] = True
        return result
