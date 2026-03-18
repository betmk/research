# Changelog

## 2026-03-18 — `report-2026-03-18`
**Bi-directional footnotes, data freshness badges, research refresh**

### Report (`hormuz_research_report.html` / `.md`)
- Added bi-directional footnote system: inline `[N]` superscripts jump to numbered citations with yellow highlight; `↑` back-arrow in each citation returns to the in-text reference
- Added data freshness badges (`LIVE` / `POLICY` / `STRUCTURAL`) throughout to distinguish daily market prices from policy actions and stable infrastructure data
- 54 numbered sources, replacing the previous flat unlinked list
- Corrected VLCC spot rates: $170K/day → ~$440K/day (Poten & Partners, Mar 16 AG/Far East); prior figure reflected pre-crisis time charter averages, not current spot
- Updated BWET YTD: +243% → ~+470%; noted Mar 18 -5.2% intraday move (futures curve softening)
- Expanded coalition decline list: added Italy, Romania, Spain, UK
- Added Mojtaba Khamenei's first public statement (Mar 16): "Strait must continue to be used as leverage"; rejected ceasefire from two intermediary states; has not appeared in person since election
- Updated UAE production cut to "almost half" per Bloomberg (Mar 16)
- Clarified Jask terminal: only 5th VLCC loading in 5 years — not a meaningful large-scale bypass
- Confirmed GL 134 no-extension signals via Baker McKenzie legal analysis
- Updated to Day 19 (March 18, 2026)

---

## 2026-03-17 — `report-2026-03-17`
**Full research refresh with social sweep and web research**

### Report (`hormuz_research_report.html` / `.md`)
- Full refresh of all data points with live web research and social media sweep
- Added Fintwit/X, Reddit, HackerNews, and YouTube sentiment sections
- Added trading signals table (bull/bear cases by signal)
- Added country-level vulnerability analysis with color-coded risk ratings
- Added Iran leadership succession table
- Added GL 134 Russian oil waiver analysis (cliff risk Apr 11)
- Added flow rate constraints section (SPR announced vs. deliverable)
- Styled HTML report with timeline, stat cards, critical threshold clocks, and callout boxes

### Chart (`hormuz_supply_chart.py` / `.html`)
- Fixed cross-platform output path using `Path(__file__).parent`
- Added auto-open behavior for both report and chart on script completion
- Windows desktop shortcut (`Hormuz Research Report.lnk`) configured for one-click launch

---

## 2026-03-17 — Initial setup
- Created research project structure
- Initial Hormuz crisis briefing (`hormuz_research_report.md` / `.html`)
- Plotly supply disruption chart (`hormuz_supply_chart.py`)
