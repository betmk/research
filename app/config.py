"""Project configuration — sources, intervals, constants.

Ported from the v1 methodology.md trade-book + source list. The constraints
here (no Singapore-only, no allocations, source priority) are load-bearing
and mirrored in .claude/CRITICAL.md.
"""
from __future__ import annotations

from pathlib import Path

# Repo root — never use cwd, always anchor to this absolute path.
REPO_ROOT = Path("/Users/mikemadden/Desktop/Claude Projects/research")
APP_DIR = REPO_ROOT / "app"
DATA_DIR = REPO_ROOT / "data"
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

# DuckDB single-file store. Gitignored.
DB_PATH = DATA_DIR / "research.duckdb"

# Credentials file (chmod 600, gitignored, never committed).
CREDS_PATH = Path.home() / ".local/share/claude-research/creds.json"

# Web service.
HOST = "127.0.0.1"
PORT = 8530

# Scrape intervals (minutes). Premium sources slower to respect rate limits.
INTERVALS = {
    "ibkr_prices": 1,      # IBKR Gateway snapshot — fast, no scrape cost
    "ibkr_positions": 5,   # account positions
    "sparta_podbean": 30,  # podcast episodes
    "sparta_insights": 30, # written Deep Dives
    "hfi_public": 30,
    "hfi_paid": 60,        # subscriber content, slower
    "oil_not_dead": 60,
    "wsj_oil": 30,         # WSJ oil section, subscriber
    "bloomberg_oil": 30,   # Bloomberg energy
    "x_twitter": 15,       # Goh + HFI
}

# Synthesis run interval (hours) — generates the AI analysis layer.
SYNTHESIS_INTERVAL_HOURS = 4

# Free / public source URLs.
SOURCES = {
    "sparta_podbean": "https://spartacommodities.podbean.com/feed.xml",
    "sparta_insights_distillate": "https://www.spartacommodities.com/insights/markets/distillate/",
    "sparta_insights_all": "https://www.spartacommodities.com/insights/",
    "hfi_archive": "https://www.hfir.com/archive",
    "oil_not_dead": "https://theoilbandit.substack.com/archive?sort=new",
    "brent_jul26": "https://www.barchart.com/futures/quotes/CBN26",
    "ice_gasoil_front": "https://www.barchart.com/futures/quotes/IGO*1",
    "nymex_ho_front": "https://www.investing.com/commodities/heating-oil",
    "murban": "https://www.investing.com/commodities/murban-oil",
    "eia_today": "https://www.eia.gov/todayinenergy/",
}

# Twitter handles (when X creds provided).
X_HANDLES = ["JuneGoh_Sparta", "SpartaCommo", "HFIResearch", "AndurandPierre",
             "JavierBlas", "gbrew24", "ed_fin", "RoryJohnston"]

# Premium source URLs (require login).
PREMIUM_SOURCES = {
    "wsj_oil": "https://www.wsj.com/news/business/oil-gas",
    "bloomberg_energy": "https://www.bloomberg.com/energy",
    "hfi_subscriber": "https://www.hfir.com/",
}

# === Trade-book constraints (load-bearing from feedback memory files) ===
# Mirror these in any AI synthesis prompt.
TRADE_CONSTRAINTS = {
    "no_singapore_only": (
        "User has no Singapore market access on IB. Singapore Gasoil swap, "
        "Sing LSFO, Sing Jet, Singapore Regrade are framework support only — "
        "never recommended as executable trades."
    ),
    "no_allocation_percentages": (
        "Trade book uses directional conviction only (working/passed/add candidate). "
        "Never assign allocation percentages."
    ),
    "fresh_each_refresh": (
        "Re-evaluate the trade book at each refresh; don't carry forward stale "
        "tiers from prior sessions."
    ),
    "main_paths_only": (
        "Write to absolute paths under /Users/mikemadden/Desktop/Claude Projects/research/ "
        "regardless of cwd."
    ),
}

# Material-change thresholds for notifications.
ALERT_THRESHOLDS = {
    "brent_pct_move": 1.0,           # % move from prior close
    "ice_go_pct_move": 1.5,
    "new_sparta_episode": True,      # always alert
    "new_hfi_wctw": True,
    "new_sparta_deep_dive": True,
    "news_keywords": [
        "Hormuz closed", "Hormuz reopened", "ceasefire", "Project Freedom",
        "Kharg", "Iran rejected", "Iran accepted", "Aramco", "OPEC", "EIA",
    ],
}

# Sparta team — voices to track (from methodology.md).
SPARTA_VOICES = {
    "Felipe Elink Schuurman": "CEO & Co-founder — strategic analysis",
    "June Goh": "Commodity Owner Singapore — Asian leg, refinery mechanics",
    "Neil Crosby": "AVP Oil Analytics — distillate briefs, ICE Gasoil",
    "James Noel-Beswick": "Commodity Owner — HOGO, European distillates, India flows",
    "Phil Jones-Lux": "Senior Analyst — gasoline/diesel",
    "Jorge Molinero": "Analyst — cross-product",
    "Michael Ryan": "Commodity Owner Freight — NWE CPP, USGC MR",
    "Abhishek Kumar": "Commodity Owner — European distillates / jet",
    "Carrie Ho": "Commodity Owner APAC — gasoil + jet briefings",
    "Nadia Riaz": "Pricing Analyst Arabian Gulf — Cross Barrel",
}

# What NOT to do (from methodology.md + memory feedback files).
DONT_LIST = [
    "Do not start with Gemini's framing — Sparta is the primary source.",
    "Do not conflate Singapore diesel crack with the E/W spread.",
    "Do not assume IBKR ticker symbology matches exchange symbols — verify.",
    "Do not present spread ranges too wide to be actionable.",
    "Do not skip the freight constraint.",
    "Do not treat the ceasefire as resolution.",
    "Do not recommend standalone Claude CLI — user uses Claude Desktop.",
    "Do not surface worktree/MCP/injection callouts unless they block work.",
]
