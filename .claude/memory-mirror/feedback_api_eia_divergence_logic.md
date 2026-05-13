---
name: API vs EIA weekly inventory divergence — catch-up logic
description: When API and EIA diverge in one week, the next week is typically catch-up, not continuation
type: feedback
originSessionId: 24120cc3-1e39-4296-b816-84a715ccea04
---
When API and EIA crude inventory weekly prints diverge significantly in one week, **the following week's API number reflects catch-up on the missed barrels**, not incremental draw/build on top of the prior pattern. Don't pattern-match "EIA was bigger last week → EIA will be bigger this week" — that's lazy.

**Concrete example (corrected May 5, 2026):**
- Wk ending Apr 24: API &minus;1.79M vs EIA &minus;6.233M = **API undercounted by 4.44M**
- Wk ending May 1: API &minus;8.1M
- HFI direct call: today's &minus;8.1M is API catch-up on those 4.44M barrels EIA already captured last week. EIA Wed expected ~&minus;4 to &minus;5M, NOT bigger than API.

**Why:** API's survey panel has narrower coverage and slower reporting than EIA's mandatory data; when API misses barrels in one week, they show up in the following week's API number even though EIA already counted them. So a big API divergence in week N gets unwound in week N+1.

**How to apply:**
- When a user asks about an upcoming EIA print after a big API number, anchor on the *cumulative* drawdown trajectory across both series, not the headline gap.
- If API undercounted EIA the prior week, expect this week's API to be partial catch-up → EIA likely smaller, not bigger.
- If asked "will EIA print bigger or smaller", answer with the catch-up logic rather than extrapolating last week's gap direction forward.

**Why it was saved:** I made the lazy pattern-match error in the May 5 Hormuz refresh — claimed "EIA likely larger than API given pattern of last 3 weeks" without considering the catch-up dynamic. User pushed back. HFI Research (user's direct contact) confirmed catch-up reading. This entry exists to prevent repeating it.
