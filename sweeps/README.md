# Sweeps

Opt-in landing zone for `/research-social` and `/research-demand` output.

By default, sweep results render in chat and are NOT persisted. If you ask Claude
to save a sweep, it lands here using the convention:

```
YYYY-MM-DD_<topic>_<social|demand>.md
```

Examples:
- `2026-04-28_copper-futures-positioning_social.md`
- `2026-05-01_natgas-storage_demand.md`

## When to save

- Topic is broad and you'll want the snapshot to reference later
- Findings include voices/accounts/blogs you want to add to a tracked topic's methodology
- Sentiment is shifting and you want a baseline

## Graduating to a tracked topic

If a topic warrants ongoing weekly+ tracking, copy `reports/_template/` to
`reports/<topic>/` and pull relevant sweep findings into the new `methodology.md`.
