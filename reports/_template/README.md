# Tracked topic — template

Copy this directory to `reports/<topic>/` to start tracking a new research topic.

```bash
cp -r reports/_template reports/<topic>
```

Then fill in `methodology.md` first — it's the load-bearing piece.

## Files

- **`methodology.md`** — the topic's per-session anchor. Read FIRST on any refresh.
  Defines source priority, voices to track, refresh workflow, output preferences,
  trade ideas, and what NOT to do. Without this, refreshes drift back to generic
  news framing.
- **`analysis.html`** — live deliverable. Update directly during refreshes.
  Self-contained (embedded CSS, dark/light compatible).
- **`CHANGELOG.md`** — append a dated entry per refresh. Newest first.

## Add to dashboard

After creating the topic, add a card for it to `index.html` so it shows up on the
Research Dashboard.
