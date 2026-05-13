"""Base class for premium scrapers — uses the saved Playwright auth state."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright, BrowserContext

from .base import BaseScraper

AUTH_STATE_FILE = Path.home() / ".local/share/claude-research/auth_state.json"


def auth_state_available() -> bool:
    return AUTH_STATE_FILE.exists() and AUTH_STATE_FILE.stat().st_size > 100


class PremiumScraper(BaseScraper):
    """Subclass and implement scrape_with_ctx(ctx)."""

    async def fetch(self) -> dict[str, Any]:
        if not auth_state_available():
            return {"items_found": 0, "items_new": 0,
                    "skipped": "auth_state.json missing — run scripts/setup_premium_auth.py"}

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                channel="chrome",
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            try:
                ctx = await browser.new_context(
                    storage_state=str(AUTH_STATE_FILE),
                    user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/130.0.0.0 Safari/537.36"),
                )
                return await self.scrape_with_ctx(ctx)
            finally:
                await browser.close()

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        raise NotImplementedError
