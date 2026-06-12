---
name: project-launchd-tcc-desktop
description: "research dashboard launchd service can't start uvicorn from ~/Desktop (macOS TCC) — how to launch + the durable fix"
metadata: 
  node_type: memory
  type: project
  originSessionId: d139001c-a672-440f-8f4c-600522423e81
---

The `com.research.research` launchd agent **fails to start uvicorn** with `Operation not permitted` / `getcwd: cannot access parent directories` (exit 78 = EX_CONFIG). Root cause: macOS **TCC** blocks launchd-spawned processes from exec'ing binaries under `~/Desktop` (a protected folder) without Full Disk Access. The service ran fine until ~2026-05-18 — likely a macOS update or the 2026-05-17 venv rebuild reset the grant.

**Masking symptom:** an orphaned `python -m http.server 8530` (reparented to launchd, PPID=1) serves the static dir and returns HTTP 200, so the dashboard *looks* up while the real app is down. Always verify the real app with `curl http://127.0.0.1:8530/api/health` (only uvicorn has it) and `lsof -i :8530` (uvicorn-python vs `http.server`).

**To launch now** (an interactive Claude/terminal context DOES have Desktop TCC access): `preview_start research-http`. On 2026-05-20 I repointed `.claude/launch.json`'s `research-http` config from the stale v1 `python -m http.server 8530` to `.venv/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8530 --app-dir <repo root>`. So `preview_start research-http` now launches the real FastAPI app, not the static server.

**Durable fix** (needs a GUI action only the user can do): System Settings → Privacy & Security → Full Disk Access → add the venv python (`/Users/mikemadden/Desktop/Claude Projects/research/.venv/bin/python3`) or `/bin/sh`, then re-bootstrap: `launchctl bootout gui/$(id -u)/com.research.research; launchctl bootstrap gui/$(id -u) launchd/com.research.research.plist`. Until then the launchd job flaps every ~10s (KeepAlive) but is harmless to a manually/preview-launched uvicorn. Alternative durable fix: move the project out of `~/Desktop`.

**Cross-project (2026-05-20):** the same exit-78 TCC failure also kills `com.citrini.daily` and `com.denver-rent-tracker.scraper` — all three project launchd jobs live under `~/Desktop/Claude Projects/` and all flap harmlessly every ~10s. Durable fix options: **B1** = grant Full Disk Access to the venv python (GUI, no move) or **B2** = move the projects off `~/Desktop` (e.g. `~/Claude Projects`). On 2026-05-20 the user **declined the move for now** ("don't want to disrupt other more important processes"). So the dashboard runs on a session-scoped manual launch (`preview_start research-http`) and **won't survive a reboot** until B1 or B2 is done. Only `research` has a `.venv` (others use relative paths); a live stale worktree `jolly-albattani-e56b4f` should be removed before any move.

**Resolved 2026-05-20 (commit 69a8abf):** `/refresh-hormuz` + project `CLAUDE.md` rewritten from the archived static-report workflow (`reports/hormuz/analysis.html`, now `reports/_archive/hormuz_static_v1/`) to the live pipeline; `.claude/launch.json` `research-http` now runs uvicorn (was the stale `python -m http.server`). Live deliverable is the dashboard + synthesis. See [[feedback-claude-md-attention]].
