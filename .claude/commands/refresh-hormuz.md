---
description: Refresh Hormuz crisis trade-book and analysis with overnight delta
---

Refresh the Hormuz analysis with overnight/intraday delta.

Workflow (follow `reports/hormuz/methodology.md` for source priority):
1. Pull priority sources in PARALLEL (Sparta Podbean for Ep 93 status, Sparta insights for new Deep Dives, HFI archive, Oil Not Dead archive, Brent JUL26 + ICE Gasoil + HO live levels, WebSearch overnight Iran/Hormuz news).
2. Read current `reports/hormuz/analysis.html` subtitle + Industry Views + Watch sections.
3. Make targeted edits in parallel: subtitle (date bump + delta summary), top callout (prepend new day block + archive previous day with subheader), HFI/OND/Industry sections (prepend new pieces), Watch items (bump dates).
4. Prepend new entry to `reports/hormuz/CHANGELOG.md`.
5. Commit + push from main repo absolute path; post-commit hook auto-pushes.
6. Brief user-facing summary with sources at the end.

Hard constraints (do not violate):
- Write to main repo absolute paths (`/Users/mikemadden/Desktop/Claude Projects/research/...`) regardless of cwd.
- No Singapore-only trade recommendations (user has no Singapore IB access).
- No allocation percentages — directional conviction only.
- Build trade book fresh — don't carry forward stale tiers from prior refreshes.
- No infrastructure callouts (worktree, MCP, injections) in user-facing chat unless they actually block work.
- Do not propose plans before simple work — execute directly.
- Brief summaries only at end; lead the response with what changed, not what you're about to do.
