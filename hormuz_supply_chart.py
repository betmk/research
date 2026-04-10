"""
Strait of Hormuz Oil Supply Disruption — Interactive Timeline Chart
Generates an interactive Plotly HTML showing supply lost, mitigating factors,
and net shortage evolving from Feb 28 through Jun 30, 2026.

Updated: Apr 8 — Ceasefire in effect Apr 7 (Hormuz still closed, Iran retains control);
reopening modeled as gradual negotiated partial recovery (never reaches 100%);
added demand destruction (IEA: 640K b/d) and OECD commercial inventory drawdown;
GL 134 expires Apr 11 with no extension; well damage threshold crossed Mar 28;
event annotations updated through Apr 8.
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

# Pre-computed critical dates — avoids ~2000 strptime() calls in the main loop
_D = {s: datetime.strptime(s, "%Y-%m-%d") for s in [
    "2026-02-28", "2026-03-01", "2026-03-03", "2026-03-04", "2026-03-05",
    "2026-03-09", "2026-03-10", "2026-03-11", "2026-03-12", "2026-03-20",
    "2026-04-01", "2026-04-07", "2026-04-08", "2026-04-11", "2026-04-15",
    "2026-05-01", "2026-05-07", "2026-05-08", "2026-05-15",
    "2026-06-07",
]}

_DEFAULT_START = "2026-02-28"
_DEFAULT_END   = "2026-06-30"

_parser = argparse.ArgumentParser(description="Generate Hormuz supply disruption chart")
_parser.add_argument("--start", default=_DEFAULT_START, help="Chart start date (YYYY-MM-DD)")
_parser.add_argument("--end",   default=_DEFAULT_END,   help="Chart end date (YYYY-MM-DD)")
_parser.add_argument("--no-browser", action="store_true", help="Skip auto-opening browser")
_args, _ = _parser.parse_known_args()

START = d(_args.start)
END   = d(_args.end)

def date_range(start: datetime, end: datetime) -> list[datetime]:
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]

ALL_DATES = date_range(START, END)

# ---------------------------------------------------------------------------
# Supply disruption & mitigation curves (million barrels per day)
# Negative = supply lost; Positive = supply restored / demand reduced.
# ---------------------------------------------------------------------------

def hormuz_closure(dt: datetime) -> float:
    """Strait of Hormuz transit lost. ~20 mb/d pre-crisis transit."""
    if dt < _D["2026-02-28"]:
        return 0.0
    if dt <= _D["2026-03-01"]:
        return -6.0   # initial 30% still moving
    if dt <= _D["2026-03-04"]:
        return -14.0  # ~70% blocked
    # Mar 5+: full closure (IRGC announcement)
    # Apr 7: ceasefire in effect, but Hormuz still functionally closed
    #         (Iran retains vetting control, mines in water, insurance 5% of hull,
    #          800+ ships stranded, $2M/vessel IRGC fee)
    #
    # Realistic multi-phase reopening model (never reaches 100%):
    #
    # Phase 1 — Apr 7-14: Ceasefire "freeze" period
    #   ~3 ships/day vs 135 normal; 800+ stranded; mines uncleared
    #   Negligible improvement in transit volume
    if dt >= _D["2026-04-07"] and dt < _D["2026-04-15"]:
        return -19.0
    #
    # Phase 2 — Apr 15 - May 7: Tentative reopening (~3 weeks)
    #   Islamabad talks (Apr 10) produce partial framework;
    #   Iran allows trickle of vetted vessels; insurance still 2-5% hull;
    #   mine risk deters most commercial traffic; ~10-20 ships/day
    #   Restore rate: ~0.12 mb/d per day (~0.84 mb/d per week)
    #   Starts from -19 (Phase 1 level), not -20
    if dt >= _D["2026-04-15"] and dt < _D["2026-05-08"]:
        days_in = (dt - _D["2026-04-15"]).days
        restored = 1.0 + days_in * 0.12  # 1.0 = the 1 mb/d already restored in Phase 1
        return -(20.0 - restored)
    #
    # Phase 3 — May 8 - Jun 30: Accelerating but heavily constrained
    #   Transit capacity improving (insurance 1-2%, bilateral deals, 40-60 ships/day)
    #   BUT actual flow limited by:
    #   - Well damage: ~6-7 mb/d of Gulf production IMPAIRED (3-4 month recovery)
    #   - Ras Laffan LNG: ~1.5 mb/d equiv offline for 3-5 YEARS
    #   - Iran retains permanent vetting control + IRGC $2M fee
    #   - Damaged facilities (Mina Al-Ahmadi, Fujairah, Duqm)
    #   Restore rate: ~0.15 mb/d per day, decelerating
    #   Cap: 10 of 20 mb/d restored (-10 mb/d residual through end of chart)
    #     Residual = well damage (~4-5) + Ras Laffan (~1.5) + Iran control/fee (~1)
    #               + facility damage (~1.5) + insurance drag (~1)
    if dt >= _D["2026-05-08"]:
        phase2_restored = 1.0 + 23 * 0.12  # Phase 1 + Phase 2 total
        days_in_p3 = (dt - _D["2026-05-08"]).days
        phase3_restored = days_in_p3 * 0.15
        total_restored = min(phase2_restored + phase3_restored, 10.0)
        return -(20.0 - total_restored)
    return -20.0

def saudi_pipeline(dt: datetime) -> float:
    """Saudi East-West Pipeline (Petroline) net new exports via Yanbu.
    Yanbu loading at ~2.5 mb/d (Sparta, Mar 16) vs 750K pre-crisis.
    Net new export: ~1.75 mb/d. Arab Light only."""
    if dt < _D["2026-03-01"]:
        return 0.0
    if dt < _D["2026-03-11"]:
        return 0.5
    return 1.75

def uae_adcop(dt: datetime) -> float:
    """UAE ADCOP pipeline spare capacity to Fujairah.
    Pipeline at full capacity (~1.8 mb/d, up from ~1.1 pre-crisis); spare = ~0.7 mb/d.
    Fujairah hit 3 times (Mar 9, 14, 16) — loading impaired but not fully halted."""
    if dt < _D["2026-03-01"]:
        return 0.0
    if dt < _D["2026-03-09"]:
        return 0.5
    return 0.7

def iea_spr(dt: datetime) -> float:
    """IEA strategic reserve release — 400M barrels total.
    US: 1.43 mb/d over 120 days (172M bbl). Others: ~0.6 mb/d.
    Total ~2.0 mb/d, starting Mar 12. US portion exhausted by ~Jul 10.
    Country reserves committed: Japan 80M bbl, Germany 19.7M bbl,
    UK 13.5M bbl, + 28 other IEA members."""
    if dt < _D["2026-03-12"]:
        return 0.0
    days_in = (dt - _D["2026-03-12"]).days
    us = 1.43 if days_in < 120 else 0.0
    # Non-US members exhaust faster (smaller reserves, ~100 days)
    others = 0.57 if days_in < 100 else 0.0
    return us + others

def gl134_floating_inventory(dt: datetime) -> float:
    """GL 134 one-time release of stranded Russian oil at sea.
    ~186M bbl total on ~238 laden tankers. 60-70M bbl near India/China.
    Waiver: Mar 12 -> Apr 11 (30 days). STOCK, not FLOW — depletes."""
    if dt < _D["2026-03-12"]:
        return 0.0
    if dt > _D["2026-04-11"]:
        return 0.0  # waiver expired, relief gone
    days_in = (dt - _D["2026-03-12"]).days
    if days_in <= 20:
        return 2.0
    return max(2.0 - (days_in - 20) * 0.2, 0.0)

def russian_production(dt: datetime) -> float:
    """Russian production increase — minimal / near zero.
    Feb 2026 production was FALLING (-56K bpd m/m). ~0.1 mb/d net."""
    if dt < _D["2026-03-03"]:
        return 0.0
    return 0.1

def iranian_exports(dt: datetime) -> float:
    """Iran's own exports through strait it controls.
    ~1.5 mb/d continuing via Iranian-flagged/allied vessels + Jask terminal.
    Almost entirely China-bound (~1.25 mb/d)."""
    if dt < _D["2026-03-01"]:
        return 0.0
    return 1.5

def demand_destruction(dt: datetime) -> float:
    """Demand destruction from high prices.
    IEA raised estimate from 210K to 640K b/d. Ramps up over time as prices
    stay elevated and behavioral/policy changes take effect.
    India ethanol mandates, Japan conservation orders, China trucking restrictions."""
    if dt < _D["2026-03-10"]:
        return 0.0
    if dt < _D["2026-03-20"]:
        return 0.2  # early price response
    if dt < _D["2026-04-01"]:
        return 0.4  # Asian emergency measures kicking in
    if dt < _D["2026-05-01"]:
        return 0.64  # IEA revised estimate (640K b/d)
    # May: demand destruction peaks as crisis is worst
    if dt < _D["2026-05-15"]:
        return 0.8  # peak behavioral/policy response
    # Late May+: as reopening progresses and prices ease, demand destruction
    # STABILIZES then slowly reverses (people resume driving, factories restart)
    # But structural shifts (India ethanol, China EV adoption) are permanent
    weeks_past_may15 = (dt - _D["2026-05-15"]).days / 7
    return max(0.8 - weeks_past_may15 * 0.05, 0.4)  # floors at 0.4 (permanent shifts)

def oecd_commercial_drawdown(dt: datetime) -> float:
    """OECD commercial inventory drawdown.
    ~2.7B bbl commercial stocks; industry holds min ~60 days of demand.
    Draws at ~1.0 mb/d effectively — this is implicit market supply.
    Not unlimited: accelerates the clock toward rationing."""
    if dt < _D["2026-03-05"]:
        return 0.0
    if dt < _D["2026-04-15"]:
        return 1.0  # comfortable draw rate
    if dt < _D["2026-05-15"]:
        return 0.8  # stocks depleting, draw rate slows
    # Beyond mid-May: approaching minimum operating levels
    return 0.5

def infrastructure_repair(dt: datetime) -> float:
    """Production recovery from shut-in wells + repaired facilities.
    ~6-7 mb/d of Gulf production is IMPAIRED (well damage + facility damage).
    Kuwait CEO (Mar 28): 3-4 months to full production POST-WAR.
    Ceasefire began Apr 7 — repair clock starts now, not at crisis start.

    Recovery phases (from Apr 7 ceasefire):
    Month 1 (Apr 7 - May 7):  +0.5-1.0 mb/d — quick restarts, Ras Tanura patching
    Month 2 (May 7 - Jun 7):  +1.0-1.5 mb/d — well reactivation begins (slow due to damage)
    Month 3 (Jun 7 - Jul 7):  +0.5-1.0 mb/d — complex wells, Mina Al-Ahmadi repair
    Month 4+ (Jul+):          long tail — worst-damaged wells, some permanently lost

    Total by Jun 30 (~3 months post-ceasefire): ~2.0-2.5 mb/d recovered
    Total by Sep 30 (~6 months): ~4-5 mb/d recovered
    Ras Laffan LNG: ~1.5 mb/d equiv — NEVER recovers in 2026 (3-5 year timeline)
    Full pre-crisis levels: NOT before Q4 2026 at earliest (excl Ras Laffan)"""
    if dt < _D["2026-03-20"]:
        return 0.0
    # Pre-ceasefire: minimal repair possible (active conflict zone)
    if dt < _D["2026-04-07"]:
        return 0.3  # only Jask-area + Saudi pipeline-connected fields
    # Month 1 post-ceasefire: access restored but structural damage limits speed
    # Quick wins: Ras Tanura (550K b/d, 2-4 week repair = done by ~May 1)
    # Some shallow wells restarted in Saudi (non-water-coning fields)
    if dt < _D["2026-05-07"]:
        days_in = (dt - _D["2026-04-07"]).days
        return 0.3 + days_in * 0.025  # ~0.75 mb/d/month → ~1.05 by May 7
    # Month 2: well reactivation ramp — but water-coned wells are very slow
    # Mina Al-Ahmadi still offline; Iraq Rumaila barely starting
    if dt < _D["2026-06-07"]:
        days_in = (dt - _D["2026-05-07"]).days
        return 1.05 + days_in * 0.02  # ~0.6 mb/d/month → ~1.65 by Jun 7
    # Month 3+: decelerating — the easy wells are done, hard ones remain
    # Some Iraq/Kuwait wells permanently impaired (water coning)
    days_in = (dt - _D["2026-06-07"]).days
    return min(1.65 + days_in * 0.012, 2.5)  # very slow tail; cap 2.5 by late summer

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
demand_series = []
oecd_series = []
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
    dem = demand_destruction(dt)
    oec = oecd_commercial_drawdown(dt)
    rep = infrastructure_repair(dt)

    disruption_series.append(dis)
    saudi_series.append(sau)
    uae_series.append(uae)
    spr_series.append(spr)
    gl134_series.append(gl1)
    russia_series.append(rus)
    iran_series.append(irn)
    demand_series.append(dem)
    oecd_series.append(oec)
    repair_series.append(rep)

    net = dis + sau + uae + spr + gl1 + rus + irn + dem + oec + rep
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
    ("Saudi East-West Pipeline (+1.75)", saudi_series, "rgb(40, 167, 69)", "rgba(40, 167, 69, 0.5)"),
    ("UAE ADCOP Pipeline (+0.7)", uae_series, "rgb(0, 123, 255)", "rgba(0, 123, 255, 0.5)"),
    ("IEA SPR Release (+2.0)", spr_series, "rgb(255, 193, 7)", "rgba(255, 193, 7, 0.5)"),
    ("GL 134 Floating Inventory (expires Apr 11)", gl134_series, "rgb(255, 127, 14)", "rgba(255, 127, 14, 0.5)"),
    ("OECD Commercial Inventory Drawdown", oecd_series, "rgb(52, 152, 219)", "rgba(52, 152, 219, 0.4)"),
    ("Demand Destruction (IEA: 640K b/d+)", demand_series, "rgb(155, 89, 182)", "rgba(155, 89, 182, 0.4)"),
    ("Russian Production (+0.1)", russia_series, "rgb(108, 117, 125)", "rgba(108, 117, 125, 0.5)"),
    ("Iranian Own Exports (+1.5)", iran_series, "rgb(111, 66, 193)", "rgba(111, 66, 193, 0.5)"),
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

# Net shortage (bottom panel)
fig.add_trace(go.Scatter(
    x=ALL_DATES, y=net_shortage_series,
    name="Net Shortage",
    fill="tozeroy",
    fillcolor="rgba(220, 53, 69, 0.2)",
    line=dict(color="rgb(220, 53, 69)", width=3),
    hovertemplate="%{x|%b %d}: %{y:.1f} mb/d<extra>Net Shortage</extra>"
), row=2, col=1)

# ---------------------------------------------------------------------------
# Event annotations (lettered A-N)
# ---------------------------------------------------------------------------
events = [
    ("2026-02-28", "A", -40),
    ("2026-03-01", "B", -70),
    ("2026-03-05", "C", -40),
    ("2026-03-09", "D", -70),
    ("2026-03-11", "E", -40),
    ("2026-03-12", "F", -70),
    ("2026-03-18", "G", -40),
    ("2026-03-19", "H", -70),
    ("2026-03-28", "I", -40),
    ("2026-04-07", "J", -70),
    ("2026-04-08", "K", -40),
    ("2026-04-11", "L", -70),
]

event_legend = [
    ("A", "Feb 28", "US/Israel strike Iran; Supreme Leader Khamenei killed"),
    ("B", "Mar 1",  "Iran retaliates — drone/missile strikes on Saudi, Qatar, UAE, Oman energy infra"),
    ("C", "Mar 5",  "IRGC announces full Hormuz closure to Western-allied ships"),
    ("D", "Mar 9",  "Brent >$100; Mojtaba Khamenei elected Supreme Leader; Fujairah struck"),
    ("E", "Mar 11", "Saudi pipeline activated; IEA 400M bbl SPR release; UNSC Res. 2817"),
    ("F", "Mar 12", "GL 134 issued — 30-day Russian oil waiver (186M bbl, expires Apr 11)"),
    ("G", "Mar 18", "Israel strikes South Pars gas field (phases 3-6); Iran FM proposes Hormuz protocol"),
    ("H", "Mar 19", "Ras Laffan: 3-5 YEAR damage (17% Qatar LNG); Iran 5 salvos at Israel"),
    ("I", "Mar 28", "WELL DAMAGE THRESHOLD CROSSED — 25+ days idle; Kuwait CEO: 3-4 mo recovery"),
    ("J", "Apr 7",  "CEASEFIRE: Trump suspends bombing 2 weeks; Iran SNSC accepts; Russia/China veto UNSC"),
    ("K", "Apr 8",  "Hormuz still closed; 800+ ships stranded; mines uncleared; Brent -15% to ~$95"),
    ("L", "Apr 11", "GL 134 EXPIRES — -2 mb/d cliff; Islamabad talks (Apr 10) outcome pending"),
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
        arrowhead=2, arrowsize=1, arrowwidth=1,
        arrowcolor="rgb(100,100,100)",
        ax=0, ay=ay_offset,
        font=dict(size=10, color="rgb(40,40,40)"),
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="rgb(130,130,130)",
        borderwidth=1, borderpad=4,
        row=1, col=1
    )

# Event key legend
legend_lines = ["<b>Event Key:</b>"]
for letter, date, desc in event_legend:
    legend_lines.append(f"  <b>{letter}</b> ({date}): {desc}")
legend_text = "<br>".join(legend_lines)

fig.add_annotation(
    x=0.0, y=-0.22, xref="paper", yref="paper",
    text=legend_text,
    showarrow=False, align="left",
    font=dict(size=11, color="rgb(40,40,40)", family="monospace"),
    bgcolor="rgba(248,248,248,0.95)",
    bordercolor="rgb(200,200,200)",
    borderwidth=1, borderpad=10,
    xanchor="left", yanchor="top",
)

# Key annotations on the net shortage panel
fig.add_annotation(
    x=d("2026-04-11"), y=-10,
    text="GL 134 expires<br>-2 mb/d cliff",
    showarrow=True, arrowhead=2, ax=40, ay=-30,
    font=dict(size=9, color="rgb(220, 53, 69)", weight="bold"),
    bgcolor="rgba(255,255,255,0.95)",
    bordercolor="rgb(220, 53, 69)", borderwidth=2, borderpad=4,
    row=2, col=1
)

fig.add_annotation(
    x=d("2026-03-28"), y=-15,
    text="Well damage threshold<br>CROSSED (Mar 28)",
    showarrow=True, arrowhead=2, ax=60, ay=-40,
    font=dict(size=9, color="rgb(220, 53, 69)", weight="bold"),
    bgcolor="rgba(255,255,255,0.95)",
    bordercolor="rgb(220, 53, 69)", borderwidth=2, borderpad=4,
    row=2, col=1
)

fig.add_annotation(
    x=d("2026-04-07"), y=-12,
    text="<b>Apr 7: Ceasefire</b><br>Hormuz still closed<br>800+ ships stranded",
    showarrow=True, arrowhead=2, ax=60, ay=-50,
    font=dict(size=9, color="rgb(39, 174, 96)", weight="bold"),
    bgcolor="rgba(255,255,255,0.95)",
    bordercolor="rgb(39, 174, 96)", borderwidth=2, borderpad=4,
    row=1, col=1
)

fig.add_annotation(
    x=d("2026-04-15"), y=-12,
    text="Phase 2: Tentative<br>reopening (~10-20 ships/day)<br>Insurance still 2-5% hull",
    showarrow=True, arrowhead=2, ax=-90, ay=-20,
    font=dict(size=8, color="rgb(100,100,100)"),
    bgcolor="rgba(255,255,255,0.9)", borderpad=3,
    row=1, col=1
)

fig.add_annotation(
    x=d("2026-05-08"), y=-8,
    text="Phase 3: Transit improving<br>but production impaired<br>(6-7 mb/d well damage;<br>Ras Laffan 3-5 yr offline)",
    showarrow=True, arrowhead=2, ax=70, ay=-30,
    font=dict(size=8, color="rgb(100,100,100)"),
    bgcolor="rgba(255,255,255,0.9)", borderpad=3,
    row=1, col=1
)

fig.add_annotation(
    x=d("2026-05-20"), y=-6,
    text="Non-US SPR members<br>begin exhausting",
    showarrow=True, arrowhead=2, ax=0, ay=-40,
    font=dict(size=8, color="rgb(255, 193, 7)"),
    bgcolor="rgba(255,255,255,0.9)", borderpad=3,
    row=2, col=1
)

fig.add_annotation(
    x=d("2026-06-15"), y=-3,
    text="OECD commercial<br>stocks near minimum<br>operating levels",
    showarrow=True, arrowhead=2, ax=0, ay=-35,
    font=dict(size=8, color="rgb(52, 152, 219)"),
    bgcolor="rgba(255,255,255,0.9)", borderpad=3,
    row=2, col=1
)

# "Today" marker
fig.add_vline(
    x=d("2026-04-08").timestamp() * 1000,
    line_dash="dash", line_color="rgba(39,174,96,0.6)", line_width=2,
    row=1, col=1
)
fig.add_vline(
    x=d("2026-04-08").timestamp() * 1000,
    line_dash="dash", line_color="rgba(39,174,96,0.6)", line_width=2,
    row=2, col=1
)
fig.add_annotation(
    x=d("2026-04-08"), y=8, yref="y",
    text="<b>TODAY</b>", showarrow=False,
    font=dict(size=10, color="rgb(39,174,96)"),
    bgcolor="rgba(255,255,255,0.9)", borderpad=3,
    row=1, col=1
)

# --- Layout ---
fig.update_layout(
    height=1100,
    template="plotly_white",
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.12,
        xanchor="center", x=0.5,
        font=dict(size=10)
    ),
    margin=dict(t=160, b=420, l=60, r=30),
    hovermode="x unified",
)

fig.update_yaxes(title_text="Million Barrels / Day", row=1, col=1)
fig.update_yaxes(title_text="mb/d", row=2, col=1)
fig.update_xaxes(
    dtick=7 * 24 * 60 * 60 * 1000,
    tickformat="%b %d",
    tick0="2026-03-01",
    row=2, col=1
)

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
print(f"\nAs of Apr 8, 2026 (Day 40 — ceasefire in effect, Hormuz still largely closed):")
idx_apr8 = (d("2026-04-08") - START).days
print(f"  Hormuz transit lost:  {disruption_series[idx_apr8]:.1f} mb/d")
print(f"  Saudi pipeline:       +{saudi_series[idx_apr8]:.1f} mb/d")
print(f"  UAE ADCOP:            +{uae_series[idx_apr8]:.1f} mb/d")
print(f"  IEA SPR:              +{spr_series[idx_apr8]:.1f} mb/d")
print(f"  GL 134 inventory:     +{gl134_series[idx_apr8]:.1f} mb/d (expires Apr 11)")
print(f"  OECD commercial draw: +{oecd_series[idx_apr8]:.1f} mb/d")
print(f"  Demand destruction:   +{demand_series[idx_apr8]:.1f} mb/d")
print(f"  Russian production:   +{russia_series[idx_apr8]:.1f} mb/d")
print(f"  Iranian own exports:  +{iran_series[idx_apr8]:.1f} mb/d")
print(f"  Infra repair:         +{repair_series[idx_apr8]:.1f} mb/d")
print(f"  {'=' * 35}")
print(f"  NET SHORTAGE:         {net_shortage_series[idx_apr8]:.1f} mb/d")

print(f"\nAs of Apr 12, 2026 (day after GL 134 expires):")
idx_apr12 = (d("2026-04-12") - START).days
print(f"  GL 134 inventory:     +{gl134_series[idx_apr12]:.1f} mb/d")
print(f"  NET SHORTAGE:         {net_shortage_series[idx_apr12]:.1f} mb/d")

print(f"\nCountry strategic reserves (context — not modeled as direct flow):")
print(f"  China:  ~1,400M bbl (~120 days at import rate)")
print(f"  Japan:  80M bbl (committed to IEA SPR above)")
print(f"  Germany: 19.7M bbl (committed to IEA SPR above)")
print(f"  India:  ~7 days coverage only (critically low)")
print(f"  US:     415M bbl SPR pre-release (172M committed)")
print(f"  OECD commercial: ~2,700M bbl (drawing at ~1.0 mb/d)")
