"""Pydantic data models. Source of truth for all DB rows + API responses."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TradeStatus(str, Enum):
    WORKING = "working"
    PASSED = "passed"              # entry window closed
    CLOSED_WINNER = "closed_winner"
    CLOSED_LOSER = "closed_loser"
    KILLED = "killed"              # never triggered
    APPENDIX = "appendix"
    ADD_CANDIDATE = "add_candidate"


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"
    SPREAD = "spread"
    OPTION = "option"


class PriceQuote(BaseModel):
    """Live price for an instrument."""
    instrument: str                 # e.g. "BRENT_JUL26"
    contract: Optional[str] = None  # e.g. "CBN26"
    price: float
    change: Optional[float] = None
    change_pct: Optional[float] = None
    prev_close: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    source: str                     # e.g. "barchart"
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class NewsItem(BaseModel):
    """A news article / wire / blog post."""
    title: str
    url: str
    source: str                     # e.g. "wsj", "bloomberg", "hfi_public"
    author: Optional[str] = None
    summary: Optional[str] = None
    body: Optional[str] = None      # full text when accessible
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list)


class Episode(BaseModel):
    """Podcast episode (Sparta primarily)."""
    series: str                     # "sparta_trade_with_conviction"
    number: Optional[int] = None
    title: str
    url: str
    chapter_titles: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class Trade(BaseModel):
    """A trade idea — replaces the narrative trade-book section."""
    id: str                         # stable slug
    name: str                       # e.g. "Long ICE GO/Brent crack"
    direction: Direction
    instruments: list[str]          # legs
    source_anchor: str              # e.g. "Crosby Ep 91"
    source_url: Optional[str] = None
    rationale: str
    status: TradeStatus
    conviction: str                 # 'high' | 'medium' | 'low' — directional, NOT %
    entry_level: Optional[str] = None
    current_level: Optional[str] = None
    notes: Optional[str] = None
    opened_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None


class RawEvent(BaseModel):
    """Catch-all for things that don't fit elsewhere (Tweets, FOMC, etc.)."""
    kind: str                       # 'tweet' | 'fed' | 'opec' | 'eia' | etc.
    source: str
    payload: dict
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class ScrapeRun(BaseModel):
    """Audit log — every scraper run."""
    scraper: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    items_found: int = 0
    items_new: int = 0
    error: Optional[str] = None
    success: bool = True
