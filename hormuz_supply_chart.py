"""
Strait of Hormuz Oil Supply Disruption — Interactive Timeline Chart
Generates an interactive Plotly HTML showing supply lost, mitigating factors,
and net shortage evolving from Feb 28 through May 31, 2026.

Updated: Mar 17 — GL 134 floating inventory modeled as separate depleting factor;
UAE ADCOP at +0.7 (Sparta: pipeline at 1.8 mb/d despite Fujairah damage);
Russian production revised to +0.1; stranded inventory 186M bbl (Sparta).
Iran selective blockade: ~1.5 mb/d own exports continuing.
Iraq shut-in revised to ~2.9 mb/d (largest single-country cut).
Insurance/shipping data added to annotations.
"""

import argparse
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import webbrowser

# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------
def d(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")

# Defaults for the Hormuz crisis scenario — override via CLI args
_DEFAULT_START = "2026-02-28"
_DEFAULT_END   = "2026-05-31"

_parser = argparse.ArgumentParser(description="Generate Hormuz supply disruption chart")
_parser.add_argument("--start", default=_DEFAULT_START, help="Chart start date (YYYY-MM-DD)")
_parser.add_argument("--end",   default=_DEFAULT_END,   help="Chart end date (YYYY-MM-DD)")
_parser.add_argument("--no-browser", action="store_true", help="Skip auto-opening browser")
_args, _ = _parser.parse_known_args()

START = d(_args.start)
END   = d(_args.end)

def date_range(start: datetime, end: datetime) -> list[datetime]:
    """Daily date range inclusive."""
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]

ALL_DATES = date_range(START, END)

# ---------------------------------------------------------------------------
# Supply disruption & mitigation curves (million barrels per day)
# Each function returns the mb/d contribution for a given date.
# Negative = supply lost; Positive = supply restored.
# ---------------------------------------------------------------------------

def hormuz_closure(dt: datetime) -> float:
    """Strait of Hormuz transit lost. ~20 mb/d pre-crisis transit."""
    if dt < d("2026-02-28"):
        return 0.0
    if dt <= d("2026-03-01"):
        return -6.0   # initial 30% still moving
    if dt <= d("2026-03-04"):
        return -14.0  # ~70% blocked
    # Mar 5+: full closure (IRGC announcement)
    if dt >= d("2026-04-15"):
        # Scenario: gradual reopening over 4 weeks (ING base case)
        weeks_open = (dt - d("2026-04-15")).days / 7
        restored = min(weeks_open * 5.0, 20.0)
        return -(20.0 - restored)
    return -20.0

def saudi_pipeline(dt: datetime) -> float:
    """Saudi East-West Pipeline (Petroline) net new exports via Yanbu.
    Yanbu loading at ~2.5 mb/d (Sparta, Mar 16) vs 750K pre-crisis.
    Net new export: ~1.75 mb/d. Arab Light only."""
    if dt < d("2026-03-01"):
        return 0.0
    if dt < d("2026-03-11"):
        return 0.5  # existing flow, partial ramp
    return 1.75  # Sparta-verified: 2.5 mb/d throughput minus 750K pre-crisis

def uae_adcop(dt: datetime) -> float:
    """UAE ADCOP pipeline spare capacity to Fujairah.
    Pipeline at full capacity (~1.8 mb/d, up from ~1.1 pre-crisis); spare = ~0.7 mb/d.
    Fujairah hit 3 times (Mar 9, 14, 16) — loading impaired but not fully halted."""
    if dt < d("2026-03-01"):
        return 0.0
    if dt < d("2026-03-09"):
        return 0.5  # ramping spare capacity before first Fujairah strike
    # Post-Fujairah strikes: pipeline still flowing at 1.8 mb/d (Sparta)
    return 0.7

def iea_spr(dt: datetime) -> float:
    """IEA strategic reserve release — 400M barrels total.
    US: 1.43 mb/d over 120 days (172M bbl). Others: ~0.6 mb/d.
    Total ~2.0 mb/d, starting Mar 12. US portion exhausted by ~Jul 10."""
    if dt < d("2026-03-12"):
        return 0.0
    days_in = (dt - d("2026-03-12")).days
    us = 1.43 if days_in < 120 else 0.0
    others = 0.57 if days_in < 100 else 0.0
    return us + others

def gl134_floating_inventory(dt: datetime) -> float:
    """GL 134 one-time release of stranded Russian oil at sea.
    ~186M bbl total on ~238 laden tankers. 60-70M bbl near India/China
    deliverable within the 30-day window = ~2.0 mb/d effective flow.
    Waiver: Mar 12 -> Apr 11 (30 days). This is a STOCK, not a FLOW —
    it depletes and vanishes after expiration unless extended."""
    if dt < d("2026-03-12"):
        return 0.0
    if dt > d("2026-04-11"):
        return 0.0  # waiver expired, relief gone
    # Model as 2.0 mb/d for first 20 days (immediate India/China delivery),
    # tapering to 1.0 mb/d as nearby inventory depletes, then 0 at expiration
    days_in = (dt - d("2026-03-12")).days
    if days_in <= 20:
        return 2.0  # 60-70M bbl near India/China at ~2 mb/d
    # Days 21-30: depleting (distant barrels, slower delivery)
    return max(2.0 - (days_in - 20) * 0.2, 0.0)

def russian_production(dt: datetime) -> float:
    """Russian production increase — minimal / near zero.
    Feb 2026 production was FALLING (-56K bpd m/m). Russia may be forced
    to CUT 300K bpd by Apr due to storage saturation (Rystad).
    Net incremental new global supply: ~0.1 mb/d."""
    if dt < d("2026-03-03"):
        return 0.0
    return 0.1

def iranian_exports(dt: datetime) -> float:
    """Iran's own exports through strait it controls.
    ~1.5 mb/d continuing via Iranian-flagged/allied vessels + Jask terminal.
    Almost entirely China-bound (~1.25 mb/d)."""
    if dt < d("2026-03-01"):
        return 0.0
    return 1.5

def infrastructure_repair(dt: datetime) -> float:
    """Production recovery from shut-in wells + repaired facilities.
    Gradual ramp starting ~2 weeks after facilities are fixed.
    Major risk: wells shut >4 weeks may have permanent damage (water coning)."""
    if dt < d("2026-03-20"):
        return 0.0
    if dt < d("2026-04-01"):
        return 0.3
    if dt < d("2026-04-15"):
        return 0.8
    weeks_since_apr15 = (dt - d("2026-04-15")).days / 7
    return min(0.8 + weeks_since_apr15 * 0.5, 3.0)

# ---------------------------------------------------------------------------
# Compute daily totals
# ---------------------------------------------------------------------------
disruption_series = []
saudi_series = []
uae_series = []
spr_series = []
gl134_series = []
russia_series = []
iran_series = []
repair_series = []
net_shortage_series = []

for dt in ALL_DATES:
    dis = hormuz_closure(dt)
    sau = saudi_pipeline(dt)
    uae = uae_adcop(dt)
    spr = iea_spr(dt)
    gl1 = gl134_floating_inventory(dt)
    rus = russian_production(dt)
    irn = iranian_exports(dt)
    rep = infrastructure_repair(dt)

    disruption_series.append(dis)
    saudi_series.append(sau)
    uae_series.append(uae)
    spr_series.append(spr)
    gl134_series.append(gl1)
    russia_series.append(rus)
    iran_series.append(irn)
    repair_series.append(rep)

    net = dis + sau + uae + spr + gl1 + rus + irn + rep
    net_shortage_series.append(net)

# ---------------------------------------------------------------------------
# Build the chart
# ---------------------------------------------------------------------------
fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.7, 0.3],
    shared_xaxes=True,
    vertical_spacing=0.08,
    subplot_titles=(
        "Strait of Hormuz Crisis: Oil Supply Disruption & Mitigating Factors (mb/d)",
        "Net Global Oil Shortage (mb/d)"
    )
)

# --- Top chart: stacked area showing disruption + mitigations ---

# Disruption (negative, red)
fig.add_trace(go.Scatter(
    x=ALL_DATES, y=disruption_series,
    name="Hormuz Transit Lost",
    fill="tozeroy",
    fillcolor="rgba(220, 53, 69, 0.4)",
    line=dict(color="rgb(220, 53, 69)", width=2),
    hovertemplate="%{x|%b %d}: %{y:.1f} mb/d<extra>Hormuz Transit Lost</extra>"
), row=1, col=1)

# Mitigations (positive, stacked)
mitigation_colors = [
    ("Saudi East-West Pipeline", saudi_series, "rgb(40, 167, 69)", "rgba(40, 167, 69, 0.5)"),
    ("UAE ADCOP Pipeline", uae_series, "rgb(0, 123, 255)", "rgba(0, 123, 255, 0.5)"),
    ("IEA SPR Release", spr_series, "rgb(255, 193, 7)", "rgba(255, 193, 7, 0.5)"),
    ("GL 134 Floating Inventory (one-time)", gl134_series, "rgb(255, 127, 14)", "rgba(255, 127, 14, 0.5)"),
    ("Russian Production (+0.1)", russia_series, "rgb(108, 117, 125)", "rgba(108, 117, 125, 0.5)"),
    ("Iranian Own Exports", iran_series, "rgb(111, 66, 193)", "rgba(111, 66, 193, 0.5)"),
    ("Infrastructure Repair/Restart", repair_series, "rgb(23, 162, 184)", "rgba(23, 162, 184, 0.5)"),
]

for name, series, line_color, fill_color in mitigation_colors:
    fig.add_trace(go.Scatter(
        x=ALL_DATES, y=series,
        name=name,
        stackgroup="mitigations",
        line=dict(color=line_color, width=1),
        fillcolor=fill_color,
        hovertemplate="%{x|%b %d}: +%{y:.1f} mb/d<extra>" + name + "</extra>"
    ), row=1, col=1)

# --- Bottom chart: net shortage ---
fig.add_trace(go.Scatter(
    x=ALL_DATES, y=net_shortage_series,
    name="Net Shortage",
    fill="tozeroy",
    fillcolor="rgba(220, 53, 69, 0.2)",
    line=dict(color="rgb(220, 53, 69)", width=3),
    hovertemplate="%{x|%b %d}: %{y:.1f} mb/d<extra>Net Shortage</extra>"
), row=2, col=1)

# --- Key event annotations (lettered for readability) ---
events = [
    ("2026-02-28", "A", -40),
    ("2026-03-01", "B", -70),
    ("2026-03-05", "C", -40),
    ("2026-03-07", "D", -70),
    ("2026-03-09", "E", -40),
    ("2026-03-11", "F", -70),
    ("2026-03-12", "G", -40),
    ("2026-03-14", "H", -70),
    ("2026-03-16", "I", -40),
    ("2026-03-17", "J", -70),
]

# Full descriptions for the footnote legend
event_legend = [
    ("A", "Feb 28", "US/Israel launch strikes on Iran; Supreme Leader Ali Khamenei killed"),
    ("B", "Mar 1",  "Iran retaliates — drone/missile strikes on Saudi, Qatar, UAE, Oman energy infrastructure"),
    ("C", "Mar 5",  "IRGC announces full Strait of Hormuz closure to US/Western-allied ships"),
    ("D", "Mar 7",  "Kuwait declares force majeure; combined Gulf production cuts reach ~6.7 mb/d"),
    ("E", "Mar 9",  "Fujairah first strike; Mojtaba Khamenei elected Supreme Leader (IRGC-backed)"),
    ("F", "Mar 11", "Saudi East-West Pipeline at full capacity; IEA releases 400M bbl (record); UNSC Res. 2817"),
    ("G", "Mar 12", "OFAC issues GL 134 — 30-day Russian oil waiver (~186M bbl floating inventory)"),
    ("H", "Mar 14", "US strikes 90+ military targets on Kharg Island (oil infrastructure deliberately spared); Fujairah 2nd strike"),
    ("I", "Mar 16", "First non-Iran transits: Pakistani tanker + Saudi tanker (India) + 2 Indian LPG carriers"),
    ("J", "Mar 17", "Larijani + Soleimani killed (40+ officials total); Germany, Japan, UK, Italy, Romania, Spain, Australia decline escort coalition"),
]

for date_str, letter, ay_offset in events:
    fig.add_vline(
        x=d(date_str).timestamp() * 1000,
        line_dash="dot", line_color="rgba(100,100,100,0.3)", line_width=1,
        row=1, col=1
    )
    fig.add_annotation(
        x=d(date_str),
        y=-20,
        yref="y",
        text=f"<b>{letter}</b>",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1,
        arrowcolor="rgb(100,100,100)",
        ax=0,
        ay=ay_offset,
        font=dict(size=10, color="rgb(40,40,40)"),
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="rgb(130,130,130)",
        borderwidth=1,
        borderpad=4,
        row=1, col=1
    )

# Build footnote legend text (two columns for compactness)
legend_lines = ["<b>Event Key:</b>"]
for letter, date, desc in event_legend:
    legend_lines.append(f"  <b>{letter}</b> ({date}): {desc}")
legend_text = "<br>".join(legend_lines)

fig.add_annotation(
    x=0.0,
    y=-0.22,
    xref="paper",
    yref="paper",
    text=legend_text,
    showarrow=False,
    align="left",
    font=dict(size=12, color="rgb(40,40,40)", family="monospace"),
    bgcolor="rgba(248,248,248,0.95)",
    bordercolor="rgb(200,200,200)",
    borderwidth=1,
    borderpad=10,
    xanchor="left",
    yanchor="top",
)

# GL 134 expiration annotation
fig.add_annotation(
    x=d("2026-04-11"),
    y=-10,
    text="GL 134 expires<br>-2 mb/d cliff",
    showarrow=True,
    arrowhead=2,
    ax=40, ay=-30,
    font=dict(size=9, color="rgb(220, 53, 69)", weight="bold"),
    bgcolor="rgba(255,255,255,0.95)",
    bordercolor="rgb(220, 53, 69)",
    borderwidth=2,
    borderpad=4,
    row=2, col=1
)

# 4-week well damage threshold annotation
fig.add_annotation(
    x=d("2026-03-28"),
    y=-15,
    text="4-week shut-in threshold<br>Permanent well damage risk",
    showarrow=True,
    arrowhead=2,
    ax=60, ay=-40,
    font=dict(size=9, color="rgb(220, 53, 69)", weight="bold"),
    bgcolor="rgba(255,255,255,0.95)",
    bordercolor="rgb(220, 53, 69)",
    borderwidth=2,
    borderpad=4,
    row=2, col=1
)

# Scenario annotation
fig.add_annotation(
    x=d("2026-04-15"),
    y=-10,
    text="Scenario: gradual<br>Hormuz reopening",
    showarrow=True,
    arrowhead=2,
    ax=-80, ay=0,
    font=dict(size=9, color="rgb(100,100,100)"),
    bgcolor="rgba(255,255,255,0.9)",
    borderpad=3,
    row=1, col=1
)

# SPR exhaustion annotation
fig.add_annotation(
    x=d("2026-05-20"),
    y=-8,
    text="Non-US SPR members<br>begin exhausting",
    showarrow=True,
    arrowhead=2,
    ax=0, ay=-40,
    font=dict(size=8, color="rgb(255, 193, 7)"),
    bgcolor="rgba(255,255,255,0.9)",
    borderpad=3,
    row=2, col=1
)

# --- Layout ---
fig.update_layout(
    height=1100,
    template="plotly_white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.12,
        xanchor="center",
        x=0.5,
        font=dict(size=11)
    ),
    margin=dict(t=160, b=380, l=60, r=30),
    hovermode="x unified",
)

fig.update_yaxes(title_text="Million Barrels / Day", row=1, col=1)
fig.update_yaxes(title_text="mb/d", row=2, col=1)
fig.update_xaxes(
    dtick=7 * 24 * 60 * 60 * 1000,  # weekly ticks (ms)
    tickformat="%b %d",
    tick0="2026-03-01",
    row=2, col=1
)

# Zero line
fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1, row=1, col=1)
fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1, row=2, col=1)

# --- Save ---
output_path = Path(__file__).parent / "hormuz_supply_chart.html"
fig.write_html(str(output_path), include_plotlyjs=True)
if not output_path.exists() or output_path.stat().st_size == 0:
    raise RuntimeError(f"Chart write failed — {output_path} is missing or empty")
print(f"Chart saved to: {output_path} ({output_path.stat().st_size / 1024:.0f} KB)")
if not _args.no_browser:
    webbrowser.open(output_path.as_uri())

# Print summary stats
print(f"\nAs of Mar 17, 2026:")
idx_mar17 = (d("2026-03-17") - START).days
print(f"  Hormuz transit lost:  {disruption_series[idx_mar17]:.1f} mb/d")
print(f"  Saudi pipeline:       +{saudi_series[idx_mar17]:.1f} mb/d")
print(f"  UAE ADCOP:            +{uae_series[idx_mar17]:.1f} mb/d (spare activated; Fujairah impaired)")
print(f"  IEA SPR:              +{spr_series[idx_mar17]:.1f} mb/d")
print(f"  GL 134 inventory:     +{gl134_series[idx_mar17]:.1f} mb/d (one-time, expires Apr 11)")
print(f"  Russian production:   +{russia_series[idx_mar17]:.1f} mb/d")
print(f"  Iranian own exports:  +{iran_series[idx_mar17]:.1f} mb/d")
print(f"  Infra repair:         +{repair_series[idx_mar17]:.1f} mb/d")
print(f"  {'=' * 29}")
print(f"  NET SHORTAGE:         {net_shortage_series[idx_mar17]:.1f} mb/d")

print(f"\nAs of Apr 12, 2026 (day after GL 134 expires):")
idx_apr12 = (d("2026-04-12") - START).days
print(f"  GL 134 inventory:     +{gl134_series[idx_apr12]:.1f} mb/d")
print(f"  NET SHORTAGE:         {net_shortage_series[idx_apr12]:.1f} mb/d")
