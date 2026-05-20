---
description: Refresh the Hormuz oil/distillate trade book — drive the pipeline's scrape + synthesis and surface the delta
---

The live deliverable is the FastAPI dashboard on **port 8530** (`app/`), NOT a static HTML file — the old `reports/hormuz/analysis.html` was archived to `reports/_archive/hormuz_static_v1/`. Source priority, Sparta voices, and the hard constraints below live in `app/config.py`.

Workflow:
1. **Service up.** `preview_start research-http` (runs uvicorn), then `curl http://127.0.0.1:8530/api/health`. If it won't bind, the launchd job is likely TCC-blocked under `~/Desktop` — the preview launch covers the session. See project `CLAUDE.md`.
2. **Fresh data.** IBKR prices need IB Gateway on 4001 (`nc -z 127.0.0.1 4001`). The running service scrapes on intervals; check freshness via `/api/prices` (`fetched_at`) and `/fragments/scrape-status`. Don't fire `/api/scrape/all` while startup's `run_all_once` is still running (IBKR clientId clash). Force one source with `POST /api/scrape/{scraper}`.
3. **Regenerate.** `POST /api/synthesis/run` → `{headline, triggered_alert, model}`. Confirm `model == "claude-cli"`; if it fell back to `rule-based-v1`, retry once (the CLI cold-starts).
4. **Verify.** `GET /fragments/analysis` shows the new claude-cli run; screenshot the dashboard for the user.
5. **(Optional) Cross-check.** Pull overnight Iran/Hormuz headlines via WebSearch to sanity-check the synthesis narrative against primary reporting.
6. **Surface.** Lead the response with what materially changed — price/spread deltas, EIA print, Sparta Ep N calls — sources inline (`[wsj]`, `[hfi_subscriber]`, `Sparta Ep N transcript`).

Hard constraints (load-bearing; mirrored in `app/config.py` TRADE_CONSTRAINTS / DONT_LIST):
- Sparta is the primary source — don't start from others' framing.
- No Singapore-only trade recommendations (user has no Singapore IB access) — framework-only, but still enumerate them.
- No allocation percentages — directional conviction only.
- Rebuild the trade book fresh — don't carry forward stale tiers from prior refreshes.
- Write to main-repo absolute paths (`/Users/mikemadden/Desktop/Claude Projects/research/...`) regardless of cwd.
- No infrastructure callouts (worktree, MCP, injections) in user-facing chat unless they actually block work.
- Do not propose a plan before simple work — execute directly. Brief summary only at the end, leading with what changed.
