"""EIA Weekly Petroleum Status Report scraper.

EIA publishes weekly stocks data every Wednesday 10:30 ET. We pull the
public XLS files (no API key needed) for the 5 series the trade book
cares about and store the full historical series.

Wednesday + Thursday print days, this scraper should run every ~15 min;
other days it can idle (data won't change). Scheduler interval handles
that — the scraper is idempotent via UNIQUE(series, period).
"""
from __future__ import annotations

import io
from datetime import date
from typing import Any

import httpx
import pandas as pd

from ..db import upsert_eia_observation
from .base import BaseScraper

# Series label → EIA weekly XLS code + display unit
EIA_SERIES = {
    "crude_excl_spr_mbbl": ("WCESTUS1w", "Crude (excl SPR)", "k bbl"),
    "spr_mbbl":            ("WCSSTUS1w", "Strategic Petroleum Reserve", "k bbl"),
    "gasoline_mbbl":       ("WGTSTUS1w", "Gasoline stocks", "k bbl"),
    "distillate_mbbl":     ("WDISTUS1w", "Distillate stocks", "k bbl"),
    "refinery_util_pct":   ("WPULEUS3w", "Refinery utilization", "%"),
}

BASE_URL = "https://www.eia.gov/dnav/pet/hist_xls/"


class EIAWeekly(BaseScraper):
    name = "eia_weekly"

    async def fetch(self) -> dict[str, Any]:
        items_found = 0
        items_new = 0

        async with httpx.AsyncClient(
            timeout=25.0,
            follow_redirects=True,
            headers={"User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
            )},
        ) as client:
            for label, (series_id, display, unit) in EIA_SERIES.items():
                try:
                    response = await client.get(f"{BASE_URL}{series_id}.xls")
                    if response.status_code != 200:
                        continue
                    xl = pd.ExcelFile(io.BytesIO(response.content))
                    sheet = next(
                        (s for s in xl.sheet_names if "Data" in s),
                        xl.sheet_names[-1],
                    )
                    df = pd.read_excel(
                        io.BytesIO(response.content),
                        sheet_name=sheet,
                        header=2,
                    ).dropna()
                    if len(df) == 0:
                        continue
                    # Insert the last 60 weeks for a useful chart history
                    for _, row in df.tail(60).iterrows():
                        period_raw = row.iloc[0]
                        value = row.iloc[1]
                        if pd.isna(period_raw) or pd.isna(value):
                            continue
                        period = (
                            period_raw.date()
                            if hasattr(period_raw, "date")
                            else period_raw
                        )
                        if not isinstance(period, date):
                            continue
                        items_found += 1
                        if upsert_eia_observation(
                            series=label, label=display,
                            period=period, value=float(value), unit=unit,
                        ):
                            items_new += 1
                except Exception:  # noqa: BLE001
                    pass

        return {"items_found": items_found, "items_new": items_new}
