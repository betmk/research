"""Article body enrichment — fetches each unenriched news URL, extracts
full article text with trafilatura, saves to news.body.

Routes free-source URLs through httpx (fast). Routes premium-source URLs
(wsj, bloomberg, hfi_subscriber) through Playwright with the persistent
Chrome profile (for paywall-protected content).
"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx
import trafilatura

from ..db import set_news_body, unenriched_news
from .base import BaseScraper
from .premium_base import PROFILE_DIR, _profile_lock, profile_ready

PREMIUM_SOURCES = {"wsj", "bloomberg", "hfi_subscriber"}
MAX_BODY_CHARS = 12_000  # keep tokens bounded for synthesis

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)


def _extract_body(html: str) -> str | None:
    """Run trafilatura on raw HTML. Returns plain-text body or None."""
    if not html:
        return None
    body = trafilatura.extract(html, include_comments=False, include_tables=False,
                                favor_recall=True)
    if not body or len(body) < 200:
        return None
    return body[:MAX_BODY_CHARS]


async def _enrich_free(rows: list[dict]) -> int:
    """Enrich free-source URLs via httpx. Returns count enriched."""
    if not rows:
        return 0
    count = 0
    async with httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        for row in rows:
            try:
                resp = await client.get(row["url"])
                if resp.status_code != 200:
                    continue
                body = _extract_body(resp.text)
                if body:
                    set_news_body(row["id"], body)
                    count += 1
            except Exception:  # noqa: BLE001
                pass
    return count


async def _enrich_premium(rows: list[dict]) -> int:
    """Enrich premium URLs via Playwright + persistent Chrome profile."""
    if not rows or not profile_ready():
        return 0
    from playwright.async_api import async_playwright

    count = 0
    async with _profile_lock:
        # Remove leftover locks
        for n in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
            lock = PROFILE_DIR / n
            if lock.exists() or lock.is_symlink():
                try:
                    lock.unlink()
                except OSError:
                    pass

        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                channel="chrome",
                headless=True,
                args=["--no-first-run", "--disable-blink-features=AutomationControlled"],
                user_agent=USER_AGENT,
            )
            try:
                for row in rows:
                    page = await ctx.new_page()
                    try:
                        await page.goto(row["url"], wait_until="domcontentloaded",
                                          timeout=25000)
                        await page.wait_for_timeout(2500)
                        # Scroll to trigger lazy-loaded content if any
                        await page.evaluate(
                            "window.scrollTo(0, document.body.scrollHeight)"
                        )
                        await page.wait_for_timeout(1000)
                        html = await page.content()
                        body = _extract_body(html)
                        if body:
                            set_news_body(row["id"], body)
                            count += 1
                    except Exception:  # noqa: BLE001
                        pass
                    finally:
                        try:
                            await page.close()
                        except Exception:  # noqa: BLE001
                            pass
            finally:
                await ctx.close()
    return count


class ArticleEnricher(BaseScraper):
    """Run after each scrape pass — fetches bodies for new news rows."""

    name = "enrich_articles"

    async def fetch(self) -> dict[str, Any]:
        rows = unenriched_news(limit=30)
        free = [r for r in rows if r["source"] not in PREMIUM_SOURCES]
        premium = [r for r in rows if r["source"] in PREMIUM_SOURCES]

        # Free first (fast), premium second (single browser launch)
        free_count = await _enrich_free(free)
        premium_count = await _enrich_premium(premium)

        return {
            "items_found": len(rows),
            "items_new": free_count + premium_count,
            "free_enriched": free_count,
            "premium_enriched": premium_count,
        }
