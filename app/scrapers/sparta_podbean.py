"""Sparta Commodities — Trade with Conviction podcast (Podbean RSS).

Free / no auth required. Episodes drop ~weekly. Ep 92 was May 7; Ep 93
expected May 13-14.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import feedparser
import httpx

from ..config import SOURCES
from ..db import upsert_episodes
from .base import BaseScraper


_EP_NUMBER_RE = re.compile(r"Episode\s+(\d+)", re.IGNORECASE)


class SpartaPodbean(BaseScraper):
    name = "sparta_podbean"

    async def fetch(self) -> dict[str, Any]:
        url = SOURCES["sparta_podbean"]
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            feed_xml = response.text

        feed = feedparser.parse(feed_xml)
        items: list[dict] = []

        for entry in feed.entries[:20]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            description = entry.get("summary", "") or entry.get("description", "")
            published = None
            if entry.get("published_parsed"):
                published = datetime(*entry.published_parsed[:6])

            # Try to extract episode number from title or description
            number = None
            for source_text in (title, description):
                match = _EP_NUMBER_RE.search(source_text)
                if match:
                    number = int(match.group(1))
                    break

            items.append({
                "series": "sparta_trade_with_conviction",
                "number": number,
                "title": title,
                "url": link,
                "chapter_titles": [],  # not in RSS; pulled separately from page
                "description": description[:2000] if description else None,
                "published_at": published,
            })

        new_count = upsert_episodes(items)
        return {
            "items_found": len(items),
            "items_new": new_count,
            "latest": items[0]["title"] if items else None,
        }
