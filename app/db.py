"""DuckDB connection + schema + helpers.

Single-file embedded database — no server, no setup. Schema is created on
first connection. All writes go through here; all reads should too.
"""
from __future__ import annotations

import duckdb
from contextlib import contextmanager
from pathlib import Path

from .config import DB_PATH, DATA_DIR


SCHEMA = """
-- Sequences first (DuckDB requires them to exist before referencing tables)
CREATE SEQUENCE IF NOT EXISTS prices_seq START 1;
CREATE SEQUENCE IF NOT EXISTS news_seq START 1;
CREATE SEQUENCE IF NOT EXISTS episodes_seq START 1;
CREATE SEQUENCE IF NOT EXISTS raw_events_seq START 1;
CREATE SEQUENCE IF NOT EXISTS scrape_runs_seq START 1;
CREATE SEQUENCE IF NOT EXISTS analysis_runs_seq START 1;

CREATE TABLE IF NOT EXISTS prices (
    id BIGINT PRIMARY KEY DEFAULT nextval('prices_seq'),
    instrument VARCHAR NOT NULL,
    contract VARCHAR,
    price DOUBLE NOT NULL,
    change DOUBLE,
    change_pct DOUBLE,
    prev_close DOUBLE,
    day_high DOUBLE,
    day_low DOUBLE,
    source VARCHAR NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS news (
    id BIGINT PRIMARY KEY DEFAULT nextval('news_seq'),
    title VARCHAR NOT NULL,
    url VARCHAR NOT NULL UNIQUE,
    source VARCHAR NOT NULL,
    author VARCHAR,
    summary VARCHAR,
    body VARCHAR,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tags VARCHAR[]
);

CREATE TABLE IF NOT EXISTS episodes (
    id BIGINT PRIMARY KEY DEFAULT nextval('episodes_seq'),
    series VARCHAR NOT NULL,
    number INTEGER,
    title VARCHAR NOT NULL,
    url VARCHAR NOT NULL UNIQUE,
    chapter_titles VARCHAR[],
    description VARCHAR,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trades (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    direction VARCHAR NOT NULL,
    instruments VARCHAR[],
    source_anchor VARCHAR,
    source_url VARCHAR,
    rationale VARCHAR,
    status VARCHAR NOT NULL,
    conviction VARCHAR,
    entry_level VARCHAR,
    current_level VARCHAR,
    notes VARCHAR,
    opened_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_events (
    id BIGINT PRIMARY KEY DEFAULT nextval('raw_events_seq'),
    kind VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    payload JSON,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scrape_runs (
    id BIGINT PRIMARY KEY DEFAULT nextval('scrape_runs_seq'),
    scraper VARCHAR NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    items_found INTEGER DEFAULT 0,
    items_new INTEGER DEFAULT 0,
    error VARCHAR,
    success BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id BIGINT PRIMARY KEY DEFAULT nextval('analysis_runs_seq'),
    run_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary VARCHAR,
    body VARCHAR,
    triggered_alert BOOLEAN DEFAULT FALSE,
    model VARCHAR
);

-- Current IBKR account positions snapshot. Truncated + repopulated each tick.
CREATE TABLE IF NOT EXISTS positions (
    symbol VARCHAR NOT NULL,
    local_symbol VARCHAR,
    sec_type VARCHAR NOT NULL,
    exchange VARCHAR,
    currency VARCHAR,
    position DOUBLE NOT NULL,
    avg_cost DOUBLE,
    market_price DOUBLE,
    market_value DOUBLE,
    unrealized_pnl DOUBLE,
    account VARCHAR,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prices_instrument_time ON prices(instrument, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_source_time ON news(source, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_episodes_series ON episodes(series, published_at DESC);
"""


def init_db() -> None:
    """Create the database file + schema if missing. Idempotent."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    try:
        conn.execute(SCHEMA)
    finally:
        conn.close()


@contextmanager
def get_conn():
    """Yield a DuckDB connection. Caller is responsible for committing
    (DuckDB autocommits but we keep this explicit for clarity)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    try:
        yield conn
    finally:
        conn.close()


def upsert_news(items: list[dict]) -> int:
    """Insert news items, skipping duplicates by URL. Returns new-row count."""
    if not items:
        return 0
    new_count = 0
    with get_conn() as conn:
        for item in items:
            try:
                conn.execute(
                    """
                    INSERT INTO news (title, url, source, author, summary, body,
                                       published_at, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        item.get("title"),
                        item.get("url"),
                        item.get("source"),
                        item.get("author"),
                        item.get("summary"),
                        item.get("body"),
                        item.get("published_at"),
                        item.get("tags") or [],
                    ],
                )
                new_count += 1
            except duckdb.ConstraintException:
                # Duplicate URL — skip silently
                pass
    return new_count


def upsert_episodes(items: list[dict]) -> int:
    if not items:
        return 0
    new_count = 0
    with get_conn() as conn:
        for item in items:
            try:
                conn.execute(
                    """
                    INSERT INTO episodes (series, number, title, url,
                                          chapter_titles, description,
                                          published_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        item.get("series"),
                        item.get("number"),
                        item.get("title"),
                        item.get("url"),
                        item.get("chapter_titles") or [],
                        item.get("description"),
                        item.get("published_at"),
                    ],
                )
                new_count += 1
            except duckdb.ConstraintException:
                pass
    return new_count


def insert_price(quote: dict) -> None:
    """Append a price quote. Always inserts (time-series)."""
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO prices (instrument, contract, price, change, change_pct,
                                prev_close, day_high, day_low, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                quote.get("instrument"),
                quote.get("contract"),
                quote.get("price"),
                quote.get("change"),
                quote.get("change_pct"),
                quote.get("prev_close"),
                quote.get("day_high"),
                quote.get("day_low"),
                quote.get("source"),
            ],
        )


def latest_prices() -> list[dict]:
    """Most recent quote per instrument."""
    with get_conn() as conn:
        result = conn.execute(
            """
            SELECT DISTINCT ON (instrument) instrument, contract, price, change,
                   change_pct, prev_close, day_high, day_low, source, fetched_at
            FROM prices
            ORDER BY instrument, fetched_at DESC
            """
        ).fetchall()
        cols = ["instrument", "contract", "price", "change", "change_pct",
                "prev_close", "day_high", "day_low", "source", "fetched_at"]
        return [dict(zip(cols, row)) for row in result]


def recent_news(limit: int = 20, source: str | None = None) -> list[dict]:
    """N most recent news items, optionally filtered by source."""
    sql = "SELECT title, url, source, author, summary, published_at, fetched_at FROM news"
    params: list = []
    if source:
        sql += " WHERE source = ?"
        params.append(source)
    sql += " ORDER BY COALESCE(published_at, fetched_at) DESC LIMIT ?"
    params.append(limit)
    with get_conn() as conn:
        result = conn.execute(sql, params).fetchall()
        cols = ["title", "url", "source", "author", "summary", "published_at",
                "fetched_at"]
        return [dict(zip(cols, row)) for row in result]


def recent_episodes(limit: int = 10) -> list[dict]:
    with get_conn() as conn:
        result = conn.execute(
            """
            SELECT series, number, title, url, chapter_titles, description,
                   published_at, fetched_at
            FROM episodes
            ORDER BY COALESCE(published_at, fetched_at) DESC
            LIMIT ?
            """,
            [limit],
        ).fetchall()
        cols = ["series", "number", "title", "url", "chapter_titles",
                "description", "published_at", "fetched_at"]
        return [dict(zip(cols, row)) for row in result]


def log_scrape_run(scraper: str, started_at, finished_at=None,
                   items_found: int = 0, items_new: int = 0,
                   error: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO scrape_runs (scraper, started_at, finished_at,
                                     items_found, items_new, error, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [scraper, started_at, finished_at, items_found, items_new,
             error, error is None],
        )


def latest_scrape_runs(limit: int = 50) -> list[dict]:
    with get_conn() as conn:
        result = conn.execute(
            """
            SELECT scraper, started_at, finished_at, items_found, items_new,
                   error, success
            FROM scrape_runs
            ORDER BY started_at DESC
            LIMIT ?
            """,
            [limit],
        ).fetchall()
        cols = ["scraper", "started_at", "finished_at", "items_found",
                "items_new", "error", "success"]
        return [dict(zip(cols, row)) for row in result]


def current_positions(sec_types: tuple[str, ...] | None = None) -> list[dict]:
    """Latest positions snapshot. Optionally filter by sec_type."""
    sql = """
        SELECT symbol, local_symbol, sec_type, exchange, currency, position,
               avg_cost, market_price, market_value, unrealized_pnl, account,
               updated_at
        FROM positions
    """
    params: list = []
    if sec_types:
        placeholders = ",".join("?" for _ in sec_types)
        sql += f" WHERE sec_type IN ({placeholders})"
        params.extend(sec_types)
    sql += " ORDER BY ABS(market_value) DESC NULLS LAST"
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        cols = ["symbol", "local_symbol", "sec_type", "exchange", "currency",
                "position", "avg_cost", "market_price", "market_value",
                "unrealized_pnl", "account", "updated_at"]
        return [dict(zip(cols, row)) for row in rows]
