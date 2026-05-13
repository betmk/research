"""Base scraper class. All scrapers extend this."""
from __future__ import annotations

import asyncio
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ..db import log_scrape_run


class BaseScraper(ABC):
    """Subclass and implement fetch(). The base handles logging + errors."""

    name: str = "base"

    async def run(self) -> dict[str, Any]:
        """Top-level entry point. Returns summary dict."""
        started = datetime.utcnow()
        try:
            result = await self.fetch()
            finished = datetime.utcnow()
            log_scrape_run(
                scraper=self.name,
                started_at=started,
                finished_at=finished,
                items_found=result.get("items_found", 0),
                items_new=result.get("items_new", 0),
            )
            return {"ok": True, **result}
        except Exception as exc:  # noqa: BLE001
            finished = datetime.utcnow()
            log_scrape_run(
                scraper=self.name,
                started_at=started,
                finished_at=finished,
                error=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[:400]}",
            )
            return {"ok": False, "error": str(exc)}

    @abstractmethod
    async def fetch(self) -> dict[str, Any]:
        """Pull from source, persist to DB. Return {items_found, items_new}."""
        raise NotImplementedError
