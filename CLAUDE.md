# Research

## Overview
Equity research reports and analysis tools. Primary output is styled HTML briefings with interactive Plotly charts, auto-opened in the browser on completion.

## Error Handling
- All web fetches (APIs, scrapers) must have try/except with meaningful messages.
- Graceful degradation: if a data source fails, note it in the report rather than crashing.
- Financial calculations must handle missing data, None values, and division by zero.

## Tech Stack
- Python 3.12+, Plotly (interactive charts), Requests
- Output: self-contained HTML files (embedded CSS/JS, no external dependencies)
- Data sources: web research, social media sweeps, Google Trends

## Project Structure
- `hormuz_research_report.md` — Markdown source for the Hormuz crisis briefing
- `hormuz_research_report.html` — Generated HTML report (styled, with footnotes)
- `hormuz_supply_chart.py` — Plotly chart generator for supply disruption timeline
- `hormuz_supply_chart.html` — Generated interactive chart (embedded Plotly)

## Key Conventions
- Reports are generated as styled HTML with embedded CSS (dark/light compatible).
- Charts use Plotly with `include_plotlyjs=True` for self-contained output.
- All data points must be source-attributed with footnotes.
- When updating reports: update the .md source first, then regenerate HTML.
- Auto-open the finished report in the default browser on completion.
