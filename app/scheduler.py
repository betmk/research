"""Background scheduler — runs all scrapers on their configured intervals.

Registered with FastAPI's startup event so it runs alongside the web server.
"""
from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import INTERVALS
from .scrapers.hfi_public import HFIPublic
from .scrapers.oil_not_dead import OilNotDead
from .scrapers.prices import Prices
from .scrapers.sparta_podbean import SpartaPodbean

logger = logging.getLogger(__name__)

# Scraper registry — keys must match INTERVALS keys in config.py.
SCRAPERS = {
    "sparta_podbean": SpartaPodbean,
    "hfi_public": HFIPublic,
    "oil_not_dead": OilNotDead,
    "prices": Prices,
}


_scheduler: AsyncIOScheduler | None = None


async def _run_scraper(key: str) -> None:
    scraper = SCRAPERS[key]()
    result = await scraper.run()
    if not result.get("ok"):
        logger.warning("scraper %s failed: %s", key, result.get("error"))
    else:
        logger.info("scraper %s ok: %s", key, result)


def start_scheduler() -> AsyncIOScheduler:
    """Initialize and start the scheduler. Returns the scheduler instance."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = AsyncIOScheduler()
    for key, scraper_cls in SCRAPERS.items():
        interval_min = INTERVALS.get(key, 30)
        _scheduler.add_job(
            _run_scraper,
            trigger=IntervalTrigger(minutes=interval_min),
            args=[key],
            id=f"scrape_{key}",
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,
        )
    _scheduler.start()
    logger.info("scheduler started with %d jobs", len(SCRAPERS))
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None


async def run_all_once() -> dict[str, dict]:
    """One-off pass — useful for first-run / manual triggers."""
    results = {}
    for key in SCRAPERS:
        results[key] = await _run_scraper(key)
    return results


async def run_one(key: str) -> dict:
    """Manually trigger a single scraper. Returns its result dict."""
    if key not in SCRAPERS:
        raise ValueError(f"unknown scraper: {key!r}")
    scraper = SCRAPERS[key]()
    return await scraper.run()
