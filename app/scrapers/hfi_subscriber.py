"""HFI Research subscriber feed — pulls full post list from logged-in archive."""
from __future__ import annotations

from typing import Any

from playwright.async_api import BrowserContext

from ..db import upsert_news
from .premium_base import PremiumScraper


class HFISubscriber(PremiumScraper):
    name = "hfi_paid"
    URL = "https://www.hfir.com/archive"

    async def scrape_with_ctx(self, ctx: BrowserContext) -> dict[str, Any]:
        page = await ctx.new_page()
        await page.goto(self.URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2500)

        # Scroll a few times to trigger archive lazy-load
        for _ in range(4):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(800)

        # Substack archive: anchors with /p/<slug>
        anchors = await page.evaluate("""() => {
            const s = new Set();
            const out = [];
            document.querySelectorAll('a[href*=\"/p/\"]').forEach(a => {
                const h = (a.getAttribute('href')||'').split('?')[0].split('#')[0];
                const t = (a.innerText||'').trim();
                if (!h || !t || t.length<5) return;
                if (s.has(h)) return;
                s.add(h);
                out.push({h, t: t.slice(0,300)});
            });
            return out.slice(0, 60);
        }""")

        items: list[dict] = []
        for a in anchors:
            href = a['h']
            url = href if href.startswith("http") else f"https://www.hfir.com{href}"
            items.append({
                "title": a['t'],
                "url": url,
                "source": "hfi_subscriber",
                "tags": ["hfi", "subscriber", "oil"],
            })

        new = upsert_news(items)
        await page.close()
        return {"items_found": len(items), "items_new": new}
