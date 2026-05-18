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
    bid DOUBLE,
    ask DOUBLE,
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
    audio_url VARCHAR,
    duration_seconds INTEGER,
    chapter_titles VARCHAR[],
    description VARCHAR,
    transcript VARCHAR,
    transcript_source VARCHAR,
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

CREATE SEQUENCE IF NOT EXISTS trade_ideas_seq START 1;
CREATE TABLE IF NOT EXISTS trade_ideas (
    id BIGINT PRIMARY KEY DEFAULT nextval('trade_ideas_seq'),
    episode_id BIGINT NOT NULL,
    episode_number INTEGER NOT NULL,
    episode_title VARCHAR,
    episode_published_at TIMESTAMP,
    person VARCHAR,
    direction VARCHAR,
    instrument VARCHAR,
    conviction VARCHAR,
    rationale VARCHAR,
    quote VARCHAR,
    executable_on_ibkr BOOLEAN,
    extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_trade_ideas_ep ON trade_ideas(episode_number DESC);

CREATE SEQUENCE IF NOT EXISTS eia_obs_seq START 1;
CREATE TABLE IF NOT EXISTS eia_observations (
    id BIGINT PRIMARY KEY DEFAULT nextval('eia_obs_seq'),
    series VARCHAR NOT NULL,
    label VARCHAR NOT NULL,
    period DATE NOT NULL,
    value DOUBLE NOT NULL,
    unit VARCHAR,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(series, period)
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
    """Create the database file + schema if missing. Idempotent.
    Also runs lightweight migrations for new columns added after v1."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    try:
        conn.execute(SCHEMA)
        # Migration: bid/ask columns added post-v1.
        # Just attempt the ALTER and swallow the "already exists" error.
        for col in ("bid", "ask"):
            try:
                conn.execute(f"ALTER TABLE prices ADD COLUMN {col} DOUBLE")
            except duckdb.CatalogException:
                pass
        # Migration: transcript column on episodes (post-v1 enrichment)
        for col, typ in (("transcript", "VARCHAR"),
                          ("audio_url", "VARCHAR"),
                          ("duration_seconds", "INTEGER"),
                          ("transcript_source", "VARCHAR")):
            try:
                conn.execute(f"ALTER TABLE episodes ADD COLUMN {col} {typ}")
            except duckdb.CatalogException:
                pass
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
                    INSERT INTO episodes (series, number, title, url, audio_url,
                                          duration_seconds, chapter_titles,
                                          description, published_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        item.get("series"),
                        item.get("number"),
                        item.get("title"),
                        item.get("url"),
                        item.get("audio_url"),
                        item.get("duration_seconds"),
                        item.get("chapter_titles") or [],
                        item.get("description"),
                        item.get("published_at"),
                    ],
                )
                new_count += 1
            except duckdb.ConstraintException:
                # Already exists — try to backfill audio_url if missing
                if item.get("audio_url"):
                    conn.execute(
                        """
                        UPDATE episodes
                        SET audio_url = COALESCE(audio_url, ?),
                            duration_seconds = COALESCE(duration_seconds, ?)
                        WHERE url = ?
                        """,
                        [item.get("audio_url"), item.get("duration_seconds"),
                         item.get("url")],
                    )
    return new_count


def insert_price(quote: dict) -> None:
    """Append a price quote. Always inserts (time-series)."""
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO prices (instrument, contract, price, bid, ask, change,
                                change_pct, prev_close, day_high, day_low, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                quote.get("instrument"),
                quote.get("contract"),
                quote.get("price"),
                quote.get("bid"),
                quote.get("ask"),
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
            SELECT DISTINCT ON (instrument) instrument, contract, price, bid, ask,
                   change, change_pct, prev_close, day_high, day_low, source,
                   fetched_at
            FROM prices
            ORDER BY instrument, fetched_at DESC
            """
        ).fetchall()
        cols = ["instrument", "contract", "price", "bid", "ask", "change",
                "change_pct", "prev_close", "day_high", "day_low", "source",
                "fetched_at"]
        return [dict(zip(cols, row)) for row in result]


def latest_spreads(window_minutes: int = 15) -> list[dict]:
    """Derived spreads from latest aligned price snapshots.

    All legs taken from quotes within `window_minutes` of the most recent
    price tick — ensures the spread reflects a single point in time, not a
    mix of stale + fresh quotes. Each spread carries `as_of` = max
    fetched_at of its constituent legs.
    """
    from datetime import datetime, timedelta

    with get_conn() as conn:
        latest_ts = conn.execute(
            "SELECT MAX(fetched_at) FROM prices"
        ).fetchone()[0]
        if latest_ts is None:
            return []
        cutoff = latest_ts - timedelta(minutes=window_minutes)
        rows = conn.execute(
            """
            SELECT DISTINCT ON (instrument) instrument, price, fetched_at
            FROM prices
            WHERE fetched_at >= ?
            ORDER BY instrument, fetched_at DESC
            """,
            [cutoff],
        ).fetchall()

    px = {r[0]: {"price": r[1], "fetched_at": r[2]} for r in rows}

    spreads: list[dict] = []

    def _add(name: str, category: str, value: float, unit: str,
             note: str, legs: list[str]) -> None:
        leg_times = [px[l]["fetched_at"] for l in legs if l in px]
        if not leg_times:
            return
        spreads.append({
            "name": name,
            "category": category,
            "value": round(value, 4),
            "unit": unit,
            "note": note,
            "as_of": max(leg_times),
            "legs": legs,
        })

    def diff(a: str, b: str) -> tuple[float, list[str]] | None:
        pa, pb = px.get(a), px.get(b)
        if (not pa or not pb
                or pa["price"] is None or pb["price"] is None
                or pa["price"] <= 0 or pb["price"] <= 0):
            return None
        return pa["price"] - pb["price"], [a, b]

    # === BRENT (NYMEX BZ) forward curve ===
    for label, b in [
        ("Brent M1–M2 (BZ Jul–Aug)", "BRENT_AUG26"),
        ("Brent M1–M3 (BZ Jul–Sep)", "BRENT_SEP26"),
        ("Brent M1–M6 (BZ Jul–Oct)", "BRENT_OCT26"),
        ("Brent M1–M12 (BZ Jul–Dec)", "BRENT_DEC26"),
    ]:
        d = diff("BRENT_JUL26", b)
        if d is not None:
            _add(label, "Brent forward curve", d[0], "$/bbl",
                 "Positive = backwardation. M1-M12 anchored by OND 'Frozen' (Apr 24) at $27; compression = back-end caught bid.",
                 d[1])

    # === ICE BRENT (COIL) forward curve — user's actual position basis ===
    for label, b in [
        ("ICE Brent M1–M2 (COIL Jul–Aug)", "ICE_BRENT_AUG26"),
        ("ICE Brent M1–M3 (COIL Jul–Sep)", "ICE_BRENT_SEP26"),
        ("ICE Brent M1–M6 (COIL Jul–Oct)", "ICE_BRENT_OCT26"),
        ("ICE Brent M1–M12 (COIL Jul–Dec)", "ICE_BRENT_DEC26"),
    ]:
        d = diff("ICE_BRENT_JUL26", b)
        if d is not None:
            _add(label, "ICE Brent (COIL)", d[0], "$/bbl",
                 "User's #3 short leg + #10 back-end position basis. Same shape as BZ NYMEX clone but on ICE.",
                 d[1])

    # === WTI (CL) forward curve ===
    d = diff("WTI_JUL26", "WTI_AUG26")
    if d is not None:
        _add("WTI M1–M2 (CL Jul–Aug)", "WTI forward curve", d[0], "$/bbl",
             "Front WTI spread.", d[1])
    d = diff("WTI_JUL26", "WTI_DEC26")
    if d is not None:
        _add("WTI M1–M12 (CL Jul–Dec)", "WTI forward curve", d[0], "$/bbl",
             "Full WTI curve. Typically less backwardated than Brent due to Cushing.", d[1])

    # === BRENT-WTI ARB ===
    d = diff("BRENT_JUL26", "WTI_JUL26")
    if d is not None:
        _add("Brent–WTI front (BZ N6 – CL N6)", "Brent-WTI arb", d[0], "$/bbl",
             "Front arb. > +$5 = US export pull strong. Asymmetric to product-export-ban risk per Crosby Ep 93.", d[1])
    d = diff("BRENT_DEC26", "WTI_DEC26")
    if d is not None:
        _add("Brent–WTI back (BZ Z6 – CL Z6)", "Brent-WTI arb", d[0], "$/bbl",
             "Back-end arb. Reflects long-term US export normalization.", d[1])

    # === ICE GASOIL (GOIL) time spreads ===
    d = diff("ICE_GASOIL_JUN26", "ICE_GASOIL_JUL26")
    if d is not None:
        _add("ICE Gasoil M1–M2 (GOIL Jun–Jul)", "ICE Gasoil curve",
             d[0], "$/MT",
             "Crosby Ep 92: 'front + M2-M3 too cheap'. MAY26 expired +$11; this is now the front spread.",
             d[1])
    d = diff("ICE_GASOIL_JUL26", "ICE_GASOIL_AUG26")
    if d is not None:
        _add("ICE Gasoil M2–M3 (GOIL Jul–Aug)", "ICE Gasoil curve",
             d[0], "$/MT",
             "Crosby Ep 92 'cheap directional expression' for the front-spread cheap thesis.", d[1])

    # === NYMEX HO time spreads ===
    d = diff("NYMEX_HO_JUN26", "NYMEX_HO_JUL26")
    if d is not None:
        _add("NYMEX HO M1–M2 (HO Jun–Jul)", "NYMEX HO curve", d[0], "$/gal",
             "Front HO spread; reflects PAD1 distillate tightness.", d[1])
    d = diff("NYMEX_HO_AUG26", "NYMEX_HO_SEP26")
    if d is not None:
        _add("NYMEX HO Q3 (HO Aug–Sep)", "NYMEX HO curve", d[0], "$/gal",
             "Q3 HO time spread; key for #6 HOGO Aug/Sep expression on your book.", d[1])
    d = diff("NYMEX_HO_JUN26", "NYMEX_HO_DEC26")
    if d is not None:
        _add("NYMEX HO M1–M7 (HO Jun–Dec)", "NYMEX HO curve", d[0], "$/gal",
             "Full HO curve. Dec premium over front = back-end HOGO support for #6.", d[1])

    # === HOGO (cross-product, normalized to $/bbl) ===
    # HO $/gal × 42 = $/bbl. Gasoil $/MT ÷ 7.45 ≈ $/bbl (LSGO conversion).
    def _hogo(name: str, ho_key: str, go_key: str, note: str) -> None:
        ho, go = px.get(ho_key), px.get(go_key)
        if ho and go and ho["price"] and go["price"]:
            value = ho["price"] * 42 - go["price"] / 7.45
            spreads.append({
                "name": name,
                "category": "HOGO (HO–Gasoil cross-product)",
                "value": round(value, 3),
                "unit": "$/bbl",
                "note": note,
                "as_of": max(ho["fetched_at"], go["fetched_at"]),
                "legs": [ho_key, go_key],
            })

    _hogo("HOGO front (HOM6 – GOILM6)", "NYMEX_HO_JUN26", "ICE_GASOIL_JUN26",
          "Crosby Ep 91 trade #6 anchor. Entered ~zero; spread rallied to +$11. Front leg exposed to US product-export ban risk.")
    _hogo("HOGO Q3 (HOQ6 – GOILQ6)", "NYMEX_HO_AUG26", "ICE_GASOIL_AUG26",
          "Your HOQ6 long position rides this. Aug-basis structurally cleaner than Jun front for ban risk.")
    _hogo("HOGO Sep (HOU6 – GOIL Aug est)", "NYMEX_HO_SEP26", "ICE_GASOIL_AUG26",
          "Sep HO vs Aug Gasoil (no Sep Gasoil contract). Your HOU6 long.")

    # === CRACKS (against Brent flat) ===
    bz = px.get("BRENT_JUL26")

    # ICE Gasoil/Brent crack — GO M1 in $/MT ÷ 7.45 - Brent $/bbl
    go_front = px.get("ICE_GASOIL_JUN26")
    if bz and go_front and bz["price"] and go_front["price"]:
        crack = go_front["price"] / 7.45 - bz["price"]
        spreads.append({
            "name": "ICE Gasoil/Brent crack (GOM6 vs BZN6)",
            "category": "Cracks (vs Brent)",
            "value": round(crack, 3),
            "unit": "$/bbl",
            "note": "Crosby Ep 92 anchor. Was ~$50.83 May 5; current vs that is the #3 trade scoreboard.",
            "as_of": max(bz["fetched_at"], go_front["fetched_at"]),
            "legs": ["ICE_GASOIL_JUN26", "BRENT_JUL26"],
        })

    # HO/Brent crack
    ho_front = px.get("NYMEX_HO_JUN26")
    if bz and ho_front and bz["price"] and ho_front["price"]:
        crack = ho_front["price"] * 42 - bz["price"]
        spreads.append({
            "name": "NYMEX HO/Brent crack (HOM6 vs BZN6)",
            "category": "Cracks (vs Brent)",
            "value": round(crack, 3),
            "unit": "$/bbl",
            "note": "Distillate margin proxy on the NYMEX side. Reflects PAD1 stocks below 10y lows.",
            "as_of": max(bz["fetched_at"], ho_front["fetched_at"]),
            "legs": ["NYMEX_HO_JUN26", "BRENT_JUL26"],
        })

    # RBOB/Brent crack
    rb_front = px.get("RBOB_JUL26")
    if bz and rb_front and bz["price"] and rb_front["price"]:
        crack = rb_front["price"] * 42 - bz["price"]
        spreads.append({
            "name": "RBOB/Brent crack (RBN6 vs BZN6)",
            "category": "Cracks (vs Brent)",
            "value": round(crack, 3),
            "unit": "$/bbl",
            "note": "US summer gasoline margin. Schuurman Ep 91/93 long RBOB cracks anchor.",
            "as_of": max(bz["fetched_at"], rb_front["fetched_at"]),
            "legs": ["RBOB_JUL26", "BRENT_JUL26"],
        })

    return spreads


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


def unenriched_news(limit: int = 30, sources: tuple[str, ...] | None = None) -> list[dict]:
    """News rows that don't yet have body text. Used by ArticleEnricher."""
    sql = """
        SELECT id, title, url, source
        FROM news
        WHERE (body IS NULL OR LENGTH(body) < 200)
    """
    params: list = []
    if sources:
        placeholders = ",".join("?" for _ in sources)
        sql += f" AND source IN ({placeholders})"
        params.extend(sources)
    sql += " ORDER BY COALESCE(published_at, fetched_at) DESC LIMIT ?"
    params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [{"id": r[0], "title": r[1], "url": r[2], "source": r[3]} for r in rows]


def set_news_body(news_id: int, body: str, summary: str | None = None) -> None:
    """Persist extracted article body (and optional summary) on a news row."""
    with get_conn() as conn:
        if summary is not None:
            conn.execute(
                "UPDATE news SET body = ?, summary = ? WHERE id = ?",
                [body, summary, news_id],
            )
        else:
            conn.execute("UPDATE news SET body = ? WHERE id = ?", [body, news_id])


def insert_trade_ideas(episode_id: int, episode_number: int, episode_title: str,
                       episode_published_at, trades: list[dict],
                       model: str = "claude-cli") -> int:
    """Insert extracted trade ideas for an episode. Returns count inserted."""
    if not trades:
        return 0
    n = 0
    with get_conn() as conn:
        for t in trades:
            try:
                conn.execute(
                    """
                    INSERT INTO trade_ideas
                      (episode_id, episode_number, episode_title,
                       episode_published_at, person, direction, instrument,
                       conviction, rationale, quote, executable_on_ibkr, model)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [episode_id, episode_number, episode_title,
                     episode_published_at,
                     t.get("person"), t.get("direction"), t.get("instrument"),
                     t.get("conviction"), t.get("rationale"), t.get("quote"),
                     t.get("executable_on_ibkr"), model],
                )
                n += 1
            except Exception:  # noqa: BLE001
                pass
    return n


def episodes_needing_extraction(limit: int = 3) -> list[dict]:
    """Sparta episodes with transcripts but no trade-idea extraction yet."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT e.id, e.number, e.title, e.transcript, e.published_at
            FROM episodes e
            LEFT JOIN (SELECT DISTINCT episode_id FROM trade_ideas) ti
              ON ti.episode_id = e.id
            WHERE e.transcript IS NOT NULL
              AND LENGTH(e.transcript) > 5000
              AND ti.episode_id IS NULL
            ORDER BY e.number DESC NULLS LAST
            LIMIT ?
            """,
            [limit],
        ).fetchall()
        return [{"id": r[0], "number": r[1], "title": r[2],
                 "transcript": r[3], "published_at": r[4]} for r in rows]


def trade_ideas_chronological(limit: int = 200, episode_limit: int | None = None) -> list[dict]:
    """All extracted trade ideas, newest episode first.

    `episode_limit`: only include ideas from the most recent N episodes
    (e.g. episode_limit=3 → only Ep 93/92/91). Older episodes stay in DB
    for reference but aren't returned.
    """
    with get_conn() as conn:
        if episode_limit is not None:
            sql = """
                WITH recent_eps AS (
                    SELECT DISTINCT episode_number
                    FROM trade_ideas
                    WHERE episode_number IS NOT NULL
                    ORDER BY episode_number DESC
                    LIMIT ?
                )
                SELECT episode_number, episode_title, episode_published_at,
                       person, direction, instrument, conviction, rationale,
                       quote, executable_on_ibkr, extracted_at
                FROM trade_ideas
                WHERE episode_number IN (SELECT episode_number FROM recent_eps)
                ORDER BY episode_number DESC NULLS LAST,
                         CASE conviction
                           WHEN 'high' THEN 1
                           WHEN 'medium' THEN 2
                           WHEN 'low' THEN 3
                           ELSE 4 END,
                         id
                LIMIT ?
            """
            params = [episode_limit, limit]
        else:
            sql = """
                SELECT episode_number, episode_title, episode_published_at,
                       person, direction, instrument, conviction, rationale,
                       quote, executable_on_ibkr, extracted_at
                FROM trade_ideas
                ORDER BY episode_number DESC NULLS LAST,
                         CASE conviction
                           WHEN 'high' THEN 1
                           WHEN 'medium' THEN 2
                           WHEN 'low' THEN 3
                           ELSE 4 END,
                         id
                LIMIT ?
            """
            params = [limit]
        rows = conn.execute(sql, params).fetchall()
        cols = ["episode_number", "episode_title", "episode_published_at",
                "person", "direction", "instrument", "conviction", "rationale",
                "quote", "executable_on_ibkr", "extracted_at"]
        return [dict(zip(cols, r)) for r in rows]


def upsert_eia_observation(series: str, label: str, period, value: float,
                           unit: str | None = None) -> bool:
    """Insert one EIA weekly observation. Returns True if new row inserted."""
    with get_conn() as conn:
        try:
            conn.execute(
                """
                INSERT INTO eia_observations (series, label, period, value, unit)
                VALUES (?, ?, ?, ?, ?)
                """,
                [series, label, period, value, unit],
            )
            return True
        except duckdb.ConstraintException:
            return False


def latest_eia() -> list[dict]:
    """Most recent observation per EIA series, plus prior-period value for chg calc."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            WITH ranked AS (
                SELECT series, label, period, value, unit,
                       ROW_NUMBER() OVER (PARTITION BY series ORDER BY period DESC) AS rn
                FROM eia_observations
            )
            SELECT
                c.series, c.label, c.period, c.value, c.unit,
                p.value AS prev_value, p.period AS prev_period
            FROM ranked c
            LEFT JOIN ranked p ON p.series = c.series AND p.rn = 2
            WHERE c.rn = 1
            ORDER BY c.series
            """
        ).fetchall()
        cols = ["series", "label", "period", "value", "unit",
                "prev_value", "prev_period"]
        return [dict(zip(cols, r)) for r in rows]


def eia_history(series: str, limit: int = 52) -> list[dict]:
    """Time series of observations for a single EIA series (newest first)."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT period, value
            FROM eia_observations
            WHERE series = ?
            ORDER BY period DESC
            LIMIT ?
            """,
            [series, limit],
        ).fetchall()
        return [{"period": r[0], "value": r[1]} for r in rows]


def episodes_without_transcripts(limit: int = 10) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, series, number, title, url, audio_url, duration_seconds
            FROM episodes
            WHERE transcript IS NULL OR LENGTH(transcript) < 500
            ORDER BY COALESCE(published_at, fetched_at) DESC
            LIMIT ?
            """,
            [limit],
        ).fetchall()
        return [{"id": r[0], "series": r[1], "number": r[2],
                 "title": r[3], "url": r[4], "audio_url": r[5],
                 "duration_seconds": r[6]} for r in rows]


def set_episode_transcript(episode_id: int, transcript: str,
                           source: str = "whisper") -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE episodes SET transcript = ?, transcript_source = ? WHERE id = ?",
            [transcript, source, episode_id],
        )


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
