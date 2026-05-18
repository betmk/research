"""FastAPI app — live dashboard + API endpoints.

UI is HTMX-driven Jinja2 templates: fragment swaps, no JS framework.
Auto-refresh sections via HTMX polling on data-heavy panels.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import HOST, PORT, STATIC_DIR, TEMPLATES_DIR
from .db import (
    current_positions,
    eia_history,
    init_db,
    latest_eia,
    latest_prices,
    latest_scrape_runs,
    latest_spreads,
    recent_episodes,
    recent_news,
    trade_ideas_chronological,
)
from .scheduler import run_all_once, run_one, start_scheduler, stop_scheduler
from .synthesis import latest_analysis, run_synthesis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Init DB + start scheduler on startup; clean up on shutdown."""
    init_db()
    start_scheduler()
    # Fire one immediate scrape pass so first dashboard load has data
    asyncio.create_task(run_all_once())
    yield
    stop_scheduler()


app = FastAPI(title="Research", lifespan=lifespan)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ===== Page routes =====

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"now": datetime.utcnow()},
    )


# ===== HTMX fragment routes (auto-refreshed panels) =====

@app.get("/fragments/prices", response_class=HTMLResponse)
async def fragment_prices(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/prices.html",
        {
            "prices": latest_prices(),
            "spreads": latest_spreads(),
            "now": datetime.utcnow(),
        },
    )


@app.get("/fragments/news", response_class=HTMLResponse)
async def fragment_news(request: Request, source: str | None = None, limit: int = 20):
    return templates.TemplateResponse(
        request,
        "partials/news.html",
        {"news": recent_news(limit=limit, source=source),
         "filter_source": source},
    )


@app.get("/fragments/episodes", response_class=HTMLResponse)
async def fragment_episodes(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/episodes.html",
        {"episodes": recent_episodes(limit=10)},
    )


@app.get("/fragments/scrape-status", response_class=HTMLResponse)
async def fragment_scrape_status(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/scrape_status.html",
        {"runs": latest_scrape_runs(limit=20)},
    )


@app.get("/fragments/positions", response_class=HTMLResponse)
async def fragment_positions(request: Request, sec_type: str | None = None):
    """Account positions. ?sec_type=FUT,OPT to filter."""
    from .trades import annotate_positions
    types = tuple(sec_type.split(",")) if sec_type else None
    positions = annotate_positions(current_positions(sec_types=types))
    return templates.TemplateResponse(
        request,
        "partials/positions.html",
        {"positions": positions},
    )


@app.get("/fragments/analysis", response_class=HTMLResponse)
async def fragment_analysis(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/analysis.html",
        {"analysis": latest_analysis()},
    )


@app.get("/fragments/eia", response_class=HTMLResponse)
async def fragment_eia(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/eia.html",
        {"observations": latest_eia()},
    )


@app.get("/fragments/charts", response_class=HTMLResponse)
async def fragment_charts(request: Request):
    from .charts import all_charts_html
    return HTMLResponse(all_charts_html())


@app.get("/fragments/sparta-trades", response_class=HTMLResponse)
async def fragment_sparta_trades(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/sparta_trades.html",
        {"trades": trade_ideas_chronological(limit=300)},
    )


@app.post("/api/synthesis/run")
async def api_run_synthesis():
    result = await run_synthesis()
    return JSONResponse(result)


# ===== JSON API =====

@app.get("/api/prices")
async def api_prices():
    return {"prices": latest_prices()}


@app.get("/api/news")
async def api_news(source: str | None = None, limit: int = 20):
    return {"news": recent_news(limit=limit, source=source)}


@app.get("/api/episodes")
async def api_episodes(limit: int = 10):
    return {"episodes": recent_episodes(limit=limit)}


@app.post("/api/scrape/all")
async def api_scrape_all():
    results = await run_all_once()
    return JSONResponse({"results": results})


@app.post("/api/scrape/{scraper}")
async def api_scrape_one(scraper: str):
    try:
        result = await run_one(scraper)
        return JSONResponse(result)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=404)


@app.get("/api/health")
async def health():
    return {"status": "ok", "now": datetime.utcnow().isoformat()}
