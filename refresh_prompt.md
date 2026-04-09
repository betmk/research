# Hormuz Report Refresh Prompt

This file is read by the desktop launcher to drive an automated report refresh.
Claude Code runs this prompt in print mode to update the report.

---

Refresh the Strait of Hormuz Crisis research report. Working directory: /Users/mikemadden/Desktop/Claude Projects/research

## Step 1: Read current report state
Read `hormuz_research_report.md` to understand the current date, day count, and last-updated prices.

## Step 2: Research latest developments
Run web searches for ALL of these (use WebSearch tool):
- "Strait of Hormuz" latest news today
- Brent crude oil price today
- WTI crude oil price today
- "AAA gas prices" today (gasoline + diesel)
- "TTF European gas price" today
- "JKM Asian LNG" price today
- BWET tanker ETF price today
- Iran ceasefire Hormuz negotiations latest
- Iran war military strikes latest
- GL 134 Russian oil waiver status

## Step 3: Update the markdown report (`hormuz_research_report.md`)
- Update the **Date** line and **Day count** (days since Feb 28, 2026)
- Update the **executive summary**: lead with newest developments, keep to ~500 words
- **Timeline**: add new rows for any developments since the last update date. CONDENSE older entries:
  - Feb 28 - Mar 17 entries: merge into 1-2 line summaries each (these are established history now)
  - Mar 18 - 2 weeks ago: keep moderate detail (2-3 lines each)
  - Last 2 weeks: full detail
- Update all **price tables** (Oil, LNG/Gas, Insurance/Shipping)
- Update **Diplomatic & Military** section with latest developments
- Update **What to Watch**: remove items that have been resolved or are no longer actionable; add new catalysts
- Refresh **Market Intelligence** if new data available (social sweep not required — just update price-based signals)
- Source-attribute ALL new data points with footnotes

## Step 4: Regenerate HTML (`hormuz_research_report.html`)
Read the existing HTML file to understand the exact styling and structure. Then regenerate it from the updated markdown, preserving:
- All CSS styles (the `:root` variables, `.exec-summary`, `.stat-row`, `.clock-card`, etc.)
- The bi-directional footnote system (`[N]` superscripts with `id` anchors)
- The data freshness badges (LIVE / POLICY / STRUCTURAL)
- The stat cards grid at the top
- The critical threshold clock cards

## Step 5: Update the chart (if needed)
If supply/mitigation data has materially changed (new pipeline capacity, SPR changes, GL 134 extension/expiry, new mitigations), update `hormuz_supply_chart.py` and run it:
```
python3 hormuz_supply_chart.py --no-browser
```

## Step 6: Update CHANGELOG.md
Add a new entry at the top of CHANGELOG.md summarizing what changed in this refresh.

## Step 7: Generate PDF
Generate a PDF of the finished report using Chrome headless:
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-sandbox --print-to-pdf="/Users/mikemadden/Desktop/Hormuz Research Reports/hormuz_research_report.pdf" --print-to-pdf-no-header "file:///Users/mikemadden/Desktop/Claude%20Projects/research/hormuz_research_report.html"
```

## Step 8: Open report
Open both the HTML in browser and the PDF:
```
open hormuz_research_report.html
open "/Users/mikemadden/Desktop/Hormuz Research Reports/hormuz_research_report.pdf"
```

## Style rules
- Lead with what is NEW. Recent developments first.
- Condense anything 2+ weeks old — it's background now, not breaking news.
- Keep the executive summary punchy. Cut filler.
- Flag any data you couldn't verify with a note like "(unverified)" or "(data unavailable)".
- Do NOT fabricate data. If a price can't be found, note it as "data unavailable as of [date]".
