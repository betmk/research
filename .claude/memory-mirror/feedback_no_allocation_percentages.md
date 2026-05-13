---
name: No exact allocation percentages
description: Skip explicit allocation %s in the trade book — user is not following them; wants directional guidance based on expert input instead
type: feedback
originSessionId: ffab3716-767f-4057-9da9-1ec01fe922ca
---
Do not include exact allocation percentages (e.g., "15%", "8% allocation", "scale to 12%") on any trade in the analysis. The user is not sizing positions to those numbers and they create false precision.

**Why:** User explicit 2026-05-11. The trade book is consumed as directional guidance derived from Sparta / HFI / Crosby / Goh / Molinero expert input — not as a model portfolio with sizing prescriptions. Allocation %s implied I was modeling specific sizes, which doesn't match how the user uses the report.

**How to apply:**

- Replace allocation %s with **directional conviction language**: "high conviction long", "directional short", "watch-only pending access", "monitor for confirmation".
- Replace "Tier 1 / Tier 2 / Tier 3" tier rankings (which had been correlated with %s) with **expert-anchored conviction language**: "Crosby Ep 92 explicit", "Goh framework supports", "secondary mechanism", "watch-only".
- Replace the "Allocation Summary" callout entirely with a "This week's expert-anchored directional ideas" summary that lists trades by source + direction + conviction, no numbers.
- Keep concrete market data: spread levels, swap quotes, crack levels (these are factual market prices, not allocation suggestions).
- For position-sizing logic that's genuinely useful (e.g., "R/R 1:0.5 means front-month entry now has compressed asymmetric upside vs back-end"), preserve the R/R framing but don't translate it into an allocation %.
