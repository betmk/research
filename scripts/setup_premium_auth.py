#!/usr/bin/env python3
"""Interactive auth setup for premium scrapers.

Opens a Playwright-controlled Chrome window. You log into the four premium
sites (passkeys + Touch ID work in headed mode). When you close the window,
the script saves the session state (cookies + localStorage) to
~/.local/share/claude-research/auth_state.json — the premium scrapers
read from there.

When sessions expire, just re-run this script. No credentials are stored;
only opaque session tokens that the sites themselves issue.

Usage:
  cd ~/Desktop/Claude\\ Projects/research
  .venv/bin/python scripts/setup_premium_auth.py

Or via the wrapper:
  ./scripts/setup_premium_auth.sh
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

REPO_ROOT = Path("/Users/mikemadden/Desktop/Claude Projects/research")
AUTH_DIR = Path.home() / ".local/share/claude-research"
PROFILE_DIR = AUTH_DIR / "chrome-profile"
STATE_FILE = AUTH_DIR / "auth_state.json"

SITES = [
    ("WSJ", "https://www.wsj.com/news/business/oil-gas",
     "Log in via Sign In (top right). Passkey / Touch ID supported."),
    ("Bloomberg", "https://www.bloomberg.com/energy",
     "Log in via Sign In. If 'Are you a robot' shows, complete it."),
    ("HFI Research", "https://www.hfir.com/",
     "Log in via Sign In (top right). Substack login flow."),
    ("Sparta Commodities", "https://www.spartacommodities.com/login",
     "Log in to the Knowledge platform if you have a subscription."),
]


async def main() -> int:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 72)
    print("Premium auth setup")
    print("=" * 72)
    print()
    print("A Chrome window will open with tabs for each premium site.")
    print("Log into the ones you have subscriptions for.")
    print("When done, CLOSE THE WINDOW — the script saves your session state.")
    print()
    print("Sites:")
    for name, url, hint in SITES:
        print(f"  - {name}: {hint}")
    print()
    input("Press Enter to launch the browser...")

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
            no_viewport=True,
            args=[
                "--no-first-run",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=site-per-process",
            ],
        )

        # Open one tab per site
        first_page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await first_page.goto(SITES[0][1], wait_until="domcontentloaded")
        for name, url, _hint in SITES[1:]:
            page = await ctx.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except Exception:
                # Don't block if one site is slow — user can navigate manually
                pass

        print()
        print("Browser open. Log in to each tab. Close the window when done.")
        print("(Detection: this script polls every 2s; exits when no pages remain.)")
        print()

        # Wait for window to close (all pages closed by user)
        try:
            while True:
                await asyncio.sleep(2)
                if not ctx.pages:
                    break
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

        # Capture state before context auto-closes
        try:
            state = await ctx.storage_state()
            STATE_FILE.write_text(__import__("json").dumps(state, indent=2))
            os.chmod(STATE_FILE, 0o600)
            print(f"\nSaved auth state → {STATE_FILE} ({STATE_FILE.stat().st_size:,} bytes)")
            print(f"  Cookies captured: {len(state.get('cookies', []))}")
            print(f"  LocalStorage origins: {len(state.get('origins', []))}")
        except Exception as exc:
            print(f"\nERROR saving state: {exc}")
            return 1

        try:
            await ctx.close()
        except Exception:
            pass

    print()
    print("Done. Premium scrapers will use this state on next scheduler tick.")
    print("Re-run this script if/when sessions expire.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
