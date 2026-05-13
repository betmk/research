"""Base class for premium scrapers — uses the persistent Chrome profile
created by scripts/setup_premium_auth.py.

The profile dir auto-persists cookies across runs (this is launch_persistent_context's
job, not ours). Premium scrapers serialize via a shared asyncio lock because
a Chrome user-data-dir can't be opened by two Chromium instances at once.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, async_playwright

from .base import BaseScraper

PROFILE_DIR = Path.home() / ".local/share/claude-research/chrome-profile"

# Serializes all premium scrapes — Chrome's profile can't be opened twice.
_profile_lock = asyncio.Lock()


def profile_ready() -> bool:
    """True iff setup_premium_auth.py has been run and cookies exist."""
    cookies_db = PROFILE_DIR / "Default" / "Cookies"
    return cookies_db.exists() and cookies_db.stat().st_size > 1000


class PremiumScraper(BaseScraper):
    """Subclass and implement scrape_with_ctx(ctx)."""

    async def fetch(self) -> dict[str, Any]:
        if not profile_ready():
            return {
                "items_found": 0, "items_new": 0,
                "skipped": "chrome-profile missing — run scripts/setup_premium_auth.sh",
            }

        async with _profile_lock:
            # Remove leftover SingletonLock / SingletonCookie / SingletonSocket
            # symlinks from any prior Chrome instance — they block headless
            # launches with "ProcessSingleton" errors otherwise.
            for name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                lock_path = PROFILE_DIR / name
                if lock_path.exists() or lock_path.is_symlink():
                    try:
                        lock_path.unlink()
                    except OSError:
                        pass
            async with async_playwright() as p:
                ctx = await p.chromium.launch_persistent_context(
                    user_data_dir=str(PROFILE_DIR),
                    channel="chrome",
                    headless=True,
                    args=[
                        "--no-first-run",
                        "--disable-blink-features=AutomationControlled",
                    ],
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/130.0.0.0 Safari/537.36"
                    ),
                )
                try:
                    return await self.scrape_with_ctx(ctx)
                finally:
                    await ctx.close()

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        raise NotImplementedError
