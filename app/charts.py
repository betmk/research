"""Plotly time-series charts for the dashboard. Reads from DuckDB."""
from __future__ import annotations

from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.offline import plot

from .db import get_conn

# Bloomberg-terminal-ish chart styling
_LAYOUT = dict(
    template="plotly_dark",
    plot_bgcolor="#0b1019",
    paper_bgcolor="#0b1019",
    font=dict(family="JetBrains Mono, monospace", size=11, color="#a5b0c2"),
    margin=dict(l=50, r=20, t=30, b=40),
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=10)),
    xaxis=dict(gridcolor="#1a2234", zerolinecolor="#1a2234"),
    yaxis=dict(gridcolor="#1a2234", zerolinecolor="#1a2234"),
)


def _series(instrument: str, since_hours: int = 48) -> tuple[list, list]:
    """Return (timestamps, prices) for an instrument over the last N hours."""
    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT fetched_at, price
            FROM prices
            WHERE instrument = ? AND fetched_at >= ? AND price IS NOT NULL
            ORDER BY fetched_at
            """,
            [instrument, cutoff],
        ).fetchall()
    return [r[0] for r in rows], [r[1] for r in rows]


def _build_fig(traces: list[tuple[str, str]], title: str, height: int = 280,
               yaxis_title: str = "") -> str:
    """Build a Plotly chart and return its HTML div fragment."""
    fig = go.Figure()
    for instrument, label in traces:
        x, y = _series(instrument)
        if not x:
            continue
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines", name=label,
            line=dict(width=1.5),
            hovertemplate=label + ": %{y:.3f}<extra></extra>",
        ))
    fig.update_layout(title=title, height=height, yaxis_title=yaxis_title,
                       **_LAYOUT)
    return plot(fig, output_type="div", include_plotlyjs=False,
                 config={"displayModeBar": False})


def brent_curve_html() -> str:
    """Brent forward curve (Jul-Dec) over recent history."""
    return _build_fig(
        traces=[
            ("BRENT_JUL26", "BZ Jul"),
            ("BRENT_AUG26", "BZ Aug"),
            ("BRENT_SEP26", "BZ Sep"),
            ("BRENT_OCT26", "BZ Oct"),
            ("BRENT_DEC26", "BZ Dec"),
        ],
        title="Brent (BZ) forward curve — last 48h",
        yaxis_title="$/bbl",
    )


def ho_curve_html() -> str:
    return _build_fig(
        traces=[
            ("NYMEX_HO_JUN26", "HO Jun"),
            ("NYMEX_HO_JUL26", "HO Jul"),
            ("NYMEX_HO_AUG26", "HO Aug"),
            ("NYMEX_HO_SEP26", "HO Sep"),
            ("NYMEX_HO_DEC26", "HO Dec"),
        ],
        title="NYMEX HO forward curve — last 48h",
        yaxis_title="$/gal",
    )


def gasoil_curve_html() -> str:
    return _build_fig(
        traces=[
            ("ICE_GASOIL_JUN26", "GO Jun"),
            ("ICE_GASOIL_JUL26", "GO Jul"),
            ("ICE_GASOIL_AUG26", "GO Aug"),
        ],
        title="ICE Gasoil (GOIL) forward curve — last 48h",
        yaxis_title="$/MT",
    )


def spreads_html() -> str:
    """Derived spread time series. Reconstructed from prices table."""
    cutoff = datetime.utcnow() - timedelta(hours=48)
    fig = go.Figure()
    with get_conn() as conn:
        # Brent M1-M12
        rows = conn.execute(
            """
            SELECT a.fetched_at, a.price - b.price AS spread
            FROM prices a JOIN prices b
              ON a.fetched_at = b.fetched_at
            WHERE a.instrument = 'BRENT_JUL26'
              AND b.instrument = 'BRENT_DEC26'
              AND a.fetched_at >= ?
            ORDER BY a.fetched_at
            """,
            [cutoff],
        ).fetchall()
        if rows:
            fig.add_trace(go.Scatter(
                x=[r[0] for r in rows], y=[r[1] for r in rows],
                mode="lines", name="Brent M1–M12 ($/bbl)",
                line=dict(width=1.5),
            ))
        # Brent-WTI Jul
        rows = conn.execute(
            """
            SELECT a.fetched_at, a.price - b.price
            FROM prices a JOIN prices b
              ON a.fetched_at = b.fetched_at
            WHERE a.instrument = 'BRENT_JUL26'
              AND b.instrument = 'WTI_JUL26'
              AND a.fetched_at >= ?
            ORDER BY a.fetched_at
            """,
            [cutoff],
        ).fetchall()
        if rows:
            fig.add_trace(go.Scatter(
                x=[r[0] for r in rows], y=[r[1] for r in rows],
                mode="lines", name="Brent-WTI Jul ($/bbl)",
                line=dict(width=1.5),
            ))
    fig.update_layout(
        title="Key Spreads — last 48h",
        height=280, yaxis_title="$/bbl",
        **_LAYOUT,
    )
    return plot(fig, output_type="div", include_plotlyjs=False,
                 config={"displayModeBar": False})


def all_charts_html() -> str:
    """Render all charts stacked. Plotly.js is loaded once in the page."""
    return "\n".join([
        brent_curve_html(),
        ho_curve_html(),
        gasoil_curve_html(),
        spreads_html(),
    ])
