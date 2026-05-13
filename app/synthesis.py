"""Periodic synthesis job — reads latest DB state, writes a markdown summary
into analysis_runs. Fires macOS notification on material changes.

v1 is rule-based (no LLM call). Adding a Claude API call later is a one-line
swap inside `_generate_summary` — keep the interface stable.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from .config import ALERT_THRESHOLDS
from .db import (
    current_positions,
    get_conn,
    latest_prices,
    latest_spreads,
    recent_episodes,
    recent_news,
)
from .notifications import notify

logger = logging.getLogger(__name__)


def _generate_summary() -> tuple[str, str, bool]:
    """Build (short_summary, full_body_md, triggered_alert).

    short_summary is the 1-2 line "what changed" headline.
    body is full markdown for the analysis panel.
    triggered_alert is True if any material-change threshold tripped.
    """
    prices = latest_prices()
    spreads = latest_spreads()
    episodes = recent_episodes(limit=3)
    news = recent_news(limit=10)
    positions = current_positions(sec_types=("FUT", "OPT"))

    # Headline = biggest absolute change in the watchlist
    biggest = None
    for p in prices:
        if p.get("change_pct") is None:
            continue
        if biggest is None or abs(p["change_pct"]) > abs(biggest["change_pct"]):
            biggest = p

    headline_parts = []
    triggered = False
    if biggest:
        sign = "+" if biggest["change_pct"] > 0 else ""
        headline_parts.append(
            f"{biggest['instrument']} {sign}{biggest['change_pct']:.2f}% "
            f"(${biggest['price']:.2f})"
        )
        if abs(biggest["change_pct"]) >= ALERT_THRESHOLDS["brent_pct_move"]:
            triggered = True

    if episodes and episodes[0].get("number", 0) and episodes[0]["number"] >= 93:
        headline_parts.append(f"Ep {episodes[0]['number']} dropped")
        triggered = True

    headline = " · ".join(headline_parts) if headline_parts else "No material change."

    # Body markdown
    body_lines = [
        f"# Live snapshot — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Prices",
    ]
    for p in prices:
        chg = (f"{p['change_pct']:+.2f}%" if p.get("change_pct") is not None
               else "—")
        body_lines.append(
            f"- **{p['instrument']}** ({p.get('contract', '')}): "
            f"${p['price']:.4f} ({chg}) [close ${p.get('prev_close') or 0:.4f}]"
        )

    if spreads:
        body_lines += ["", "## Spreads"]
        for s in spreads:
            body_lines.append(
                f"- **{s['name']}**: {s['value']:+.3f} {s['unit']} — {s['note']}"
            )

    if positions:
        body_lines += ["", "## Open positions (FUT + OPT)"]
        for p in positions[:20]:
            pnl = (f"{p['unrealized_pnl']:+,.0f}" if p.get("unrealized_pnl")
                   is not None else "—")
            body_lines.append(
                f"- **{p['symbol']}** {p.get('local_symbol', '')} "
                f"({p['sec_type']}): qty {p['position']:g}, unr P&L {pnl}"
            )

    if episodes:
        body_lines += ["", "## Latest podcast episodes"]
        for e in episodes:
            body_lines.append(
                f"- Ep {e.get('number', '?')}: {e['title']}"
            )

    if news:
        body_lines += ["", "## Recent news"]
        for n in news[:10]:
            body_lines.append(f"- [{n['source']}] {n['title']}")

    return headline, "\n".join(body_lines), triggered


async def run_synthesis() -> dict[str, Any]:
    """Run the synthesis pass. Writes to analysis_runs. Returns the row."""
    headline, body, triggered = _generate_summary()

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO analysis_runs (summary, body, triggered_alert, model)
            VALUES (?, ?, ?, ?)
            """,
            [headline, body, triggered, "rule-based-v1"],
        )

    if triggered:
        await notify("Research — material change", headline)

    logger.info("synthesis ok: %s (alert=%s)", headline, triggered)
    return {"headline": headline, "triggered_alert": triggered}


def latest_analysis() -> dict | None:
    """Most recent synthesis row."""
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT run_at, summary, body, triggered_alert, model
            FROM analysis_runs
            ORDER BY run_at DESC
            LIMIT 1
            """
        ).fetchone()
        if not row:
            return None
        return {
            "run_at": row[0],
            "summary": row[1],
            "body": row[2],
            "triggered_alert": row[3],
            "model": row[4],
        }
