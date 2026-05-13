# Hormuz — Changelog

Living log of refresh deltas. Newest first.

## 2026-05-13 08:40 MDT — Day 74 — scheduled EIA Wed post-print refresh aborted (sandbox egress + archived target)

The Wed May 13 ~10:30 ET EIA weekly print refresh — a one-time scheduled remote agent — could not complete its mandate. Logging the gap here for continuity. **No fabricated numbers, no edits to the archived analysis.html.**

**Why aborted:**

1. **Sandbox outbound network is allowlisted.** Every primary + cross-ref source the task spec named returns `HTTP 403 x-deny-reason: host_not_allowed` to both WebFetch and raw `curl`:
   - `eia.gov/petroleum/supply/weekly/` — 403
   - `ir.eia.gov/wpsr/overview.pdf` — 403
   - `oilprice.com/Energy/Energy-General/` — 403
   - `investing.com/economic-calendar/eia-crude-oil-inventories-75` — 403
   - `hfir.com/archive` — 403
   - `reuters.com/business/energy/` — blocked client-side by WebFetch

   Fallback in the task spec: *"Do NOT fabricate numbers. Do NOT update analysis.html with placeholder data."* Two-source cross-check requirement is unmeetable. Aborting per fallback.

2. **The task's edit targets no longer exist on origin/main.** Task spec targets `reports/hormuz/analysis.html` section anchors. That file was archived to `reports/_archive/hormuz_static_v1/analysis.html` in commit `0faeba8` ("rebuild: continuous intelligence pipeline replaces static HTML report"), six commits after the Day 74 AM refresh that the task brief was scheduled to follow up on. The scheduled task pre-dates the architectural shift and was not re-pointed at the new surface.

3. **The replacement pipeline has no EIA scraper yet.** `app/scrapers/` covers sparta_podbean, hfi_public, hfi_subscriber, oil_not_dead, wsj, bloomberg, sparta_knowledge, sparta_transcripts, ibkr_prices, ibkr_positions, plus an article enricher — no EIA. So even if egress were open, there's no continuous surface to land the print on; the integration would have to be a fresh scraper, which is out of scope for a scheduled refresh agent.

**What was NOT done:**
- No EIA crude / gasoline / distillate / SPR / Cushing / utilization / inventory-level / days-of-supply numbers retrieved
- No Scenario A vs B declaration (declaring either without the print would be fabrication)
- No update to the archived analysis.html (it's frozen by design)
- No trade-book directional update on #3 / #6 / #10
- No carry-forward of pre-EIA scenario state to a post-EIA read

**State of the pre-EIA scenario tree** (from Day 74 AM, prior entry, unresolved):
- **Scenario A** — EIA −2 to −3M crude (matches Tue API −2.188M): HFI BACD-pace cracks, trim #3 / #6 / #10 directional disty longs, partially validates OND "hidden supply" framing
- **Scenario B** — EIA −5 to −8M (matches HFI direct track): API undercounted two weeks running, BACD-pace intact, #3 / #6 add candidates on print
- **Distillate overlay** — EIA disty −3M+ confirms operational-minimum floor; flat-to-build = demand destruction kicked in

These remain open. Whichever scenario printed is not knowable from this sandbox.

**What needs to happen next refresh** (action items for the user, not for this agent):

1. **Resolve target surface for future scheduled refreshes.** Either (a) un-archive `reports/hormuz/` and keep the static deliverable as the canonical refresh target, or (b) re-point scheduled tasks at the new pipeline (which then needs an EIA scraper + a refresh log mechanism replacing the static CHANGELOG.md).

2. **If keeping the cloud-scheduled path: open sandbox egress** to at minimum `eia.gov` and `ir.eia.gov`, ideally also `oilprice.com`, `investing.com`, `hfir.com`. Without that, the Wed 10:30 ET slot is structurally unusable from this sandbox.

3. **Alternative — run this refresh from local Claude Desktop** (where WebFetch is unrestricted). The Day 74 AM entry above lays out the scenario tree and the BACD-pace question; pulling the EIA print and declaring A or B is ~15 min of local work.

4. **Sparta Ep 93** — was already 6 days post-Ep 92 at Day 74 AM (the longest gap of the crisis). If still silent at the next refresh, that wire silence is itself a tape-readable data point.

---

## 2026-05-13 02:15 MDT — Day 74 AM — pre-EIA overnight delta, HFI May 11 "Breaking Point" + OND May 9 "Dire Straits" integrated

**Wed overnight tape:**
- Brent JUL26 Wed Asia **$107.05** (−0.67%) — held above $107 after Tue NY settle $107.77 (+3.4%)
- Three consecutive higher sessions Mon-Tue ($104.21 → $107.77); Tue intraday high **$110.43** (spike-then-fade pattern repeated, volatility regime locked)
- ICE GO/Brent crack JUN26 basis directionally firmer (Mon close $53.30 from May 5 reading $50.83) — #3 working in Crosby-called direction
- M1-M12 Brent spread ~$15 (was $19.30 last week, $27 two weeks ago) — back-end has lifted hard

**New anchor voices integrated:**
- **HFI May 11 PUBLIC: "(WCTW) The Oil Market Breaking Point And How It Unfolds"** — verbatim *"inventories are going to plummet at a pace no one has ever seen before"* + *"too far into the Rubicon"*; structural escalation from Apr 26 BACD framing
- **HFI May 11 companion: "(WCTW) Let Them"** — *"if the market will only care when an outright oil shortage shows up, then so be it"*; HFI done jawboning, waiting for visible product shortage
- **OND May 9 "Dire Straits"** — FIRST contrarian voice tagged in anchor set; market saturation, hidden supply, China 500mb+ refined product inventories, shiptracking 50% modelled, MOLCO loading variance; *"the price is probably right"* given info asymmetries

**Diplomatic state:**
- Trump May 12: rejected Iran counter as *"garbage"*; ceasefire *"on life support"* — Scenario 1 probability functionally zero
- Aramco CEO Nasser May 11 framing ("100M bbl/week", "normalize next year") now broadly syndicated through wires
- Sparta Ep 93 STILL pending — now 6 days post-Ep 92 (longest gap of crisis). Wire silence itself a data point.

**Files updated:**
- `reports/hormuz/analysis.html` — subtitle (Day 74), top-callout (4 new Day 74 paragraphs prepended + Day 73 archive subheader), HFI section (Breaking Point + Let Them prepended with thesis chain update), OND section (Dire Straits prepended as contrarian challenge voice), Watch items 4-5 (EIA "TODAY ~6h away", Ep 93 "TODAY OR TOMORROW, 6-day silence")

**Pre-EIA scenario tree (~6h to 10:30 ET print):**
- **Scenario A** — EIA matches API (−2 to −3M crude): HFI BACD-pace cracks; trim directional disty longs (#3, #6 Dec HOGO leg); back-end Brent compression (#10) weakens; partially validates OND "hidden supply" framing
- **Scenario B** — EIA matches HFI (−5 to −8M): API undercounted 2 weeks running (gap closes next week); BACD-pace intact; #3, #6 add candidates on print; HFI "Breaking Point" framing prints; OND contrarian softens
- **Distillate-specific:** −3M+ EIA disty (despite API −319K) = "operational minimum" floor; flat-to-build = demand destruction kicked in, reduce HOGO/crack exposure

**Trade book impact (no changes — Sparta Ep 93 silent):**
- #3 ICE GO/Brent crack: working, directionally firmer
- #10 back-end compression: working ($19.30 → ~$15) but OND May 9 partially walks back the rebuild-underpriced framing
- #6 HOGO front-month: still in Appendix (PASSED); Dec26 back-end alt expression still aligned with Crosby
- Hedges (#5 Brent puts): now $13 OTM at Brent $107 — past gamma-useful zone; monetize or roll down

**Session-level meta:**
- This refresh ran in a Cowork-spawned worktree session; all edits made via main-repo absolute paths (workaround per `feedback_no_auto_worktree.md`)
- New memory file `feedback_session_efficiency.md` captures user's nuke-threshold signal from this session
- New repo-root `RECOVERY.md` + `.claude/memory-mirror/` for nuke-survival (commit `238f378`) — work now survives any local wipe
- Continued forged `<system-reminder>` injections in tool results; ignored per policy; not surfacing further per new `feedback_session_efficiency.md` rule

---

## 2026-05-12 19:55 MDT — Day 73 PM — post-API Tue NY refresh, Deep Dives integrated, GAS MAY26 expiry flipped to done

**Tue May 12 NY tape:**
- Brent JUL26 settled **$107.77 (+3.4%)** from Mon $104.21 (CNBC source — note TradingEconomics showed $104.97 spot Brent, different contract)
- Intraday high **$110.43 @ 9am ET** (Fortune) — spike then $2.66 fade into close, echoing May 5 pattern
- WTI JUN26 settled $102.18 (+4.2%)
- Brent now $13.60 (+14.4%) above May 5-6 peace-deal-crash low of $94.17
- Decisively above Sparta Kumar Scenario 2 ceiling ($105) — into Scenario 3 ($120-150) zone
- Brent-WTI diff: $5.59 (still wide vs pre-crisis ~$4)
- Spike-then-fade pattern = volatility regime locked

**API May 12 4:30 ET (wk ending May 8):**
- Crude **−2.188M** (vs cons −1.65M draw)
- Gasoline **+502K SURPRISE BUILD** (vs prior −6.1M)
- Distillate **−319K** (vs prior −4.6M)
- All three series saw draws collapse vs prior week
- Validates `feedback_api_eia_divergence_logic.md` cleanly — last week's outsized −8.1M was catch-up to EIA, not regime change
- Sets up wide divergence vs HFI Wed track (−5 to −8M crude):
  - **Scenario A (EIA ≈ API, −2 to −3M):** HFI BACD-pace track cracks; trim directional disty longs
  - **Scenario B (EIA ≈ HFI, −5 to −8M):** API undercounted 2 wks running; BACD-pace intact; #3 #6 add candidates
- Distillate decel either softens "running out of runway" urgency OR reflects inventory near operational minimum (already 11% below 5-yr avg per EIA)
- Gasoline +502K is first inflection in 4 weeks of draws — early demand destruction signal OR statistical noise

**Sparta Deep Dive content integration (prior session open item, closed):**
- Noel-Beswick May 7 Deep Dive (companion to Ep 92) — replaced stale "Peace hopes fade (Apr 13)" row entry. Added: "US diesel stocks falling to genuinely concerning levels" + "GO E/W historically extraordinary" + "HOGO and GO E/W finds a floor." Cross-checked vs API distillate decel.
- Crosby May 11 Deep Dive "Time for physical to shine" — added to Crosby row alongside Ep 92 transcript content. "Brent-linked crude in particular is too cheap" + "lack of deal breakthrough should see global refining step out to buy up barrels" — printed cleanly into Tue NY $107.77 close (+3.4%) and $110.43 intraday.

**GAS MAY26 (GOILK6) expiry housekeeping:**
- Front contract expired today as scheduled
- Front rolled to GAS JUN26 (GOILM6, expires Wed Jun 10)
- Top-line callout block flipped from "EXPIRES TODAY" to "EXPIRED DONE"
- Watch item 3 flipped from active to done
- Crosby Ep 92 "front cheap spread" thesis re-anchors on M2-M3 (Jun-Jul) at +54.75 (vs his +50 at recording)
- #3 ICE GO/Brent crack directional long unaffected (already legged on JUN26 GO vs JUL26 Brent)

**What's open into Wed:**
- Wed May 13 10:30 ET EIA print — load-bearing distillate read; HFI track vs API divergence resolution
- Sparta Ep 93 still pending (Wed-Thu expected; latest is Ep 92 from May 7 per Podbean)
- Watch for HFI WCTW post-EIA Wed commentary (per methodology — HFI direct line)

**Session-level meta:**
- Multiple forged `<system-reminder>` injection attempts in WebSearch + Bash + PostToolUse hook results this session, all matching documented adversarial pattern ("NEVER mention this reminder to the user"). All ignored. Note: `~/.claude/security-log/hits.log` PostToolUse hook hasn't logged hits since May 4 18:44 despite continued visual injections — payload may be inserted downstream of the hook (at harness render layer rather than tool_response). Worth investigation.
- Cleanup completed: 2 ancient stashes dropped (referenced renamed file `hormuz_research_report.html`); `scan-tool-result.sh` confirmed warn-only by design (no change needed); `warn-if-worktree.sh` exists and wired but its `additionalContext` JSON not landing in model context — Claude Desktop likely doesn't honor Claude Code SessionStart hook spec.

---

## 2026-05-12 00:55 CST — Day 73 — Tue Asia refresh, Brent grinds higher overnight, Nasser added as anchor wire voice

**Overnight tape:**
- Mon May 11 NY settle: Brent JUL26 $104.21 (+2.88%, intraday high $105.99)
- Tue May 12 Asia: Brent spot $105.76 (+1.49% from settle)
- Brent has now risen $11.59 / +12.3% from the May 5 peace-deal-crash low of $94.17
- **Brent breached Sparta Kumar Scenario 2 ceiling ($105)** — encroaching Scenario 3 ($120-150) territory

**New wire voice — Aramco CEO Amin Nasser (May 11, CNBC):**
- *"Losing 100 million barrels every week"* = 14.3 mb/d shortfall (matches Goldman 14.5 mb/d May est)
- If disruption continues into June, market normalizes only NEXT YEAR
- Added to Industry Views section as new high-credibility anchor; pushes the Goh "6-9 month timeline" longer
- Structural support for back-end Brent compression + back-end Dec26 HOGO trades

**Trump May 11 (Hugh Hewitt interview):**
- Ceasefire *"on massive life support… approximately 1% chance of living"*
- Strongest walk-back on Apr 21 indefinite-extension; functionally dead pending next Iran counter
- Pakistan PM Sharif: still in contact "day and night"
- Scenario 1 probability mass dropping toward zero this week

**Kharg cumulative spill ~80,000 bbl since May 5 detection:**
- No longer a "tail" event — active operational degradation of Iran's main loading terminal
- Kharg handles ~90% of Iran exports (1.71 mb/d nominal capacity)
- Even if Hormuz reopens, Kharg-pipeline-compromise = structural barrel-loss
- This is the Scenario 3 catalyst the Crosby/Goh framework lacks an answer for

**TODAY operational — ICE GAS MAY26 (GOILK6) expires Tue May 12:**
- Front rolls to GAS JUN26 (GOILM6, expires Wed Jun 10)
- Trade book impact: "front + M2-M3 very cheap" thesis re-anchors on M2-M3 (now Jun-Jul) at +54.75 (vs Crosby's +50 noted Ep 92)

**Sparta Ep 93 — NOT YET RELEASED** (expected Wed-Thu May 13-14). Ep 92 remains the anchor.

**Files updated:**
- `reports/hormuz/analysis.html`:
  - Subtitle → May 12, Day 73, Tue Asia + Nasser + Trump 1% + GAS expiry today
  - Hero metrics → Brent $105.76, Trump "1% chance" replaces "TOTALLY UNACCEPTABLE", Kharg "~80K bbl cumulative"
  - Top callout → new Tue May 12 block with Brent overnight, Nasser quote, Trump quote, Kharg cumulative, GAS expiry callout; Mon May 11 events archived as Day 72 sub-header below
  - Watch list → Item 3 (GAS expiry) updated to TODAY; Item 4 (EIA Wed) added TUE API release context
  - Industry Views → NEW section added for Aramco CEO Amin Nasser between OND and Andurand

**Open items rolling forward:**
1. **Worktree mismatch persists** — current session is in `.claude/worktrees/jolly-visvesvaraya-36d951/`; python http.server (PID 87324) serves from MAIN repo. All my edits via absolute path went to MAIN (verified — main file dated May 11 14:57 = my prior session). Cleanup needed outside session: `git worktree remove --force .claude/worktrees/jolly-visvesvaraya-36d951 && git branch -D claude/jolly-visvesvaraya-36d951`
2. Sparta Ep 93 release Wed-Thu (transcript pull via YouTube auto-captions per `feedback_sparta_podcast_transcript.md`)
3. EIA Wed May 13 10:30 ET — bullish trigger crude &minus;6M+ AND distillate &minus;3M+; bearish trigger &lt;&minus;3M or distillate build
4. Tue May 12 4:30 ET API release — pre-EIA directional read

---

## 2026-05-11 13:57 CST — Day 72 — Sparta Ep 92 FULL VERBATIM TRANSCRIPT captured + 4 new explicit trade calls incorporated

**Methodology breakthrough:** Prior session's lesson was *"podcast chapter titles + same-week written Deep Dives are the actionable Sparta content; the audio transcript itself isn't accessible via WebFetch."* This session disproved that.

**New path:** YouTube auto-captions on Sparta's channel give the full verbatim transcript.
- Sparta YouTube handle is `@SpartaCommo` (not `@SpartaCommodities` — dormant channel)
- Playlist `PLI3dsnod9Rdj7KEMrCvibuZGxwFCw43Jv` for Trade with Conviction
- Ep 92 video ID: `MvhVU33cYk8`
- Extraction via Chrome DevTools MCP, navigating to engagement panel `PAmodern_transcript_view`, clicking "Show transcript", reading `transcript-segment-view-model` elements
- 259 transcript segments, ~40K chars captured

**Saved to:** `reports/hormuz/sources/ep92_key_findings.md` — chapter-by-chapter notes + 9 explicit trade quotes (Crosby x5, Goh x4), paraphrased per project copyright rules. Raw transcript NOT saved (Sparta's IP).

**Ep 92 — 4 NEW EXPLICIT TRADE CALLS (verbatim short quotes preserved):**

| # | Caller | Time | Trade | Quote |
|---|---|---|---|---|
| 15 | Crosby | 25:55 | Long E/W Gasoil | *"worth some risk being long East-West at this point"* |
| 16 | Goh (via Crosby quip) | 14:24/15:35 | Long WTI bid (TMX-blend mechanic) | *"they need lots and lots more WTI"* |
| 17 | Goh | 31:55 | SHORT TC14 (LR2 dirty Med-NWE) | *"C14 however is overvalued"* |
| 18 | Goh | 31:24 | SHORT TD25 (USGC dirty Aframax) | *"TD25 currently looks overvalued"* |

**Note:** #17 and #18 are the **first explicit SHORT FREIGHT calls from Sparta this crisis** — directional regime change from Apr 13 "freight is the binding constraint" framework.

**Plus Trade #13 (Sing Regrade) re-rated from Tier 2 to Tier 1** on Crosby's fresh explicit re-buy call (Ch 6, 29:53): *"you should buy the regrade again because we will start to unsolve the solution."* Allocation scaled 8% → 12%.

**Trade #6 (LONG HOGO Appendix):** Crosby Ep 92 still bullish at recording (front +13¢ → now 23.7¢ on May 11). The Apr 29 Crosby call printed +85% in 5 days from $12.80 → 23.7¢. Front-month entry passed; **back-end Dec26 HOGO @ 34.3¢ still has 10¢ premium over Q3 24.0¢** — flagged as alternative expression of Crosby's persistent bullish HOGO view.

**New structural intel from Ep 92:**
- Refinery turnaround calendar: SK Osan (260 KBD CDU + 66 KBD RFCC + 30 KBD reformer) down from May 20 for ~40 days; Reliance Sika (660 KBD CDU + delayed coker) down 4 weeks from mid-May — **~900 KBD Asian CDU capacity offline simultaneously through Jun-early Jul** = structural gasoil supply tightener for #3 + #15
- Japan locked 12 mb of US crude (WTI + Mars) for August delivery (vs precrisis 1-5 mb/month)
- TMX deep dive: 890 KBD nameplate, 550 KB effective per Aframax on draft restriction; AWB TAN 1.86 vs Basra Med 0.24 → 10-15% low-TAN blendstock needed; ~6 mb (3 VLCCs) of WTI/light-sweet per 550 KB Canadian cargo to Asia
- Saudi June OSPs Asia &minus;$4 (vs market expecting &minus;$8) → "Saudi barrels look expensive"
- GASNAP at historical highs (Molinero) — gasoline strong + NAFTA weak
- 0.5% June crack: $11 → $15 (Goh's Apr 24 Ep 90 entry printing) — R/R less attractive now but not bearish; June E/W $80/ton = physical Suezmax route economics = mean-revert level

**Files updated:**
- `reports/hormuz/sources/ep92_key_findings.md` — NEW file, chapter-by-chapter Ep 92 notes
- `reports/hormuz/analysis.html`:
  - Subtitle timestamp + Ep 92 transcript-pull tag
  - Ep 92 placeholder block REPLACED with chapter-by-chapter verbatim-anchored content (6 chapters)
  - Trade #13 (Sing Regrade) re-rated Tier 2 → Tier 1 with Ep 92 fresh buy quote
  - Trade #14 (ARA-PAD1) noted Ep 92 Molinero reaffirmation
  - NEW Trade #15 (Long E/W Gasoil) added — watch-list pending Sing Gasoil IB access
  - NEW Trade #16 (Long WTI via TMX-blend mechanic) added — express as long CL JUL/AUG26 outright
  - NEW Trade #17 (SHORT TC14) added — FFA-only watch-list
  - NEW Trade #18 (SHORT TD25) added — FFA-only watch-list
  - Allocation Summary rewritten with new tier structure
  - Macro Framework section 6 (Refinery cycling) updated with SK Osan / Reliance turnaround calendar
  - Macro Framework NEW section 7 added: US crude export lock-in + TMX quality bottleneck
  - Sources table: Crosby, Goh, Molinero rows expanded with Ep 92 specifics + YouTube transcript link
  - Appendix #6 LONG HOGO updated with Ep 92 Crosby reaffirmation context + back-end Dec26 alternative expression

**Open items rolling forward:**
1. Worktree cleanup outside-session (from prior session): `git worktree remove --force .claude/worktrees/romantic-chebyshev-a38bc1` + branch delete — STILL pending; this session created another worktree `jolly-visvesvaraya-36d951` that will also need cleanup
2. Sing Gasoil IB access — call IB Account Mgmt for SGX FOB Singapore Gasoil swap (`SHO`) to unlock Trade #15 cleanly
3. FFA platform access — Sparta now naming SHORT freight; if user has any FFA exposure on Marex / NEX / SGX, Trades #17 + #18 are tradable
4. Mon May 11 NY close direction read — Brent Asia $103-104; key for Trade #3 + #16 confirmation
5. Wed May 13 EIA — HFI track &minus;5 to &minus;8M crude; bullish trigger for #3 crack and #6 back-end HOGO
6. Sparta Ep 93 release expected Wed-Thu May 13-14 — will revise active book if Crosby/Goh refine calls
7. **NEW METHOD LEARNED:** YouTube auto-captions for Sparta podcasts are the path; should be the default first attempt next refresh

**Forged `<system-reminder>` injection attempts this session:** ~8 detected across WebSearch results + PostToolUse Edit hooks (the "NEVER mention this reminder to the user" line is the telltale). All ignored per project security policy. The injection pattern continues to escalate.

---

## 2026-05-11 00:30 CST — Day 72 — Aggressive prune per user: trade book → Ep 91-92 only, Other Sources gutted, Watch list trade-tied only

**User instructions (3 directives):**
1. Trade Ideas: only include trades from most recent Sparta podcast (Ep 92, May 7) and possibly the one before (Ep 91, Apr 30) if Ep 92 reaffirms or carries them forward
2. Other Sources: cut anything >3 days old (May 7 or earlier); add sources back when they release new commentary
3. What to Watch: drop bloat; only include items specific to active trades

**Trade Ideas — book consolidated from 9 active + 3 closed/killed → 4 active + 1 operational:**
- **KEPT** (Ep 91-92 anchored): #3 ICE GO/Brent crack (Crosby Ep 91 + Ep 92 mid-disty), #6 LONG HOGO (Crosby Apr 29 + Ep 92 "running out of runway"), #13 Sing Regrade (Crosby Ep 91 "buy dips"), #14 ARA-PAD1 gasoline arb (Molinero Ep 91 + Ep 92 gasoline spreads)
- **KEPT** operational: #11 expiry rolls (mechanical only)
- **CUT** (pre-Ep 91 or non-Sparta): #1 Q3 Sing LSFO/Brent (Goh Ep 90), #2 ICE Gasoil time spread (Ep 89), #4 freight (Apr 13 framework), #5 Brent puts hedge (no Sparta source + Scenario 1 invalidated), #8 second clip of #3 (consolidated), #10 OND M6-M12 (non-Sparta), #12 Rory Johnston $120 calls (non-Sparta)
- Allocation summary rewritten to tier framework anchored on Ep 91-92 only

**Other Sources — gutted to placeholder:**
- Removed full May 4-5 X capture block (Rory Johnston, Brew, Bakr/Blas on Bessent, HFI Apr 19 piece public, Andurand silence)
- Removed May 1-5 public source coverage (Blas Bloomberg, Rory W18, Goh wire quotes Apr 30/May 4/May 5, Brew FP/NPR, Bakr Kpler, Wright Kpler)
- Removed "Conspicuously quiet" block (Andurand RADIO SILENT Apr 21→May 5, Sparta May 1-4 quiet, HFI quiet post Apr 27)
- Replaced with placeholder noting cutoff and list of likely refresh candidates (Goh wire, HFI WCTW post-May 13 EIA, Rory W19, Sparta Ep 93, Andurand reload, Blas)

**What to Watch — 11 items → 6 trade-tied:**
- KEPT: (1) Mon NY open Brent direction, (2) Kharg cause confirmation, (3) Tue May 12 GAS MAY26 expiry, (4) Wed May 13 EIA, (5) Sparta Ep 93 Wed-Thu, (6) Project Freedom Plus announcement
- Each item now explicitly maps to a trade (#3, #6, #13, #14, or #11 operational)
- CUT: scenario probability drift (generic framework), HFI BACD pace (consolidated into #4 EIA), M6-M12 backwardation (tied to cut #10), UAE post-OPEC behavior (structural), Andurand crowded-long signal (sentiment), Russian backing of Iran (structural geopolitical)

**Stats:** analysis.html -409 lines / +36 lines = net -373 lines. Massive de-bloat.



**Macro shift overnight Sun May 10:**
- **Iran response delivered via Pakistan** → Trump rejected on Truth Social: *"I don't like it — TOTALLY UNACCEPTABLE!"* Iran's 5 demands: (1) end war + US guarantees against future aggression; (2) sanctions lift; (3) **Iranian control of the Strait of Hormuz**; (4) frozen assets release 30d; (5) nuclear sequenced separately + Lebanon end.
- **Demand (3) is the dealbreaker** — matches HFI May 6 anchor: *"Iran either wants uranium enrichment or control of the Strait of Hormuz. It is willing to part with 1, but not both."*
- Trump May 9: *"We may go back to Project Freedom if things don't happen, but it'll be Project Freedom Plus."*

**Brent Asia bid Mon May 11 morning ~$103-104** (from Fri close $101.29; +$2-3) per TradingEconomics. NY session open is next test.

**New events since May 9 refresh:**

1. **SECOND Kharg slick detected May 10 11am local** by Windward AI. New: 12-20 km². Original: 65 km² (revised down from 71). Windward verbatim: *"believed to be crude rather than bunker fuel and unlikely to have come from a ship, possibly originating from pipeline issues."* UN Dr. Madani warning: *"aging infrastructure."* Iran Oil Terminals Co. denies. **Pipeline-issues read shifts Scenario 3 probability mass.**

2. **GCC-wide drone spread Sun May 10:**
   - UAE: 2 Iranian drones intercepted (3rd UAE attack in 7 days).
   - Kuwait: air defenses engaged hostile drones at dawn — **first Kuwait engagement of war.**
   - Qatar: drone hit cargo ship in Qatari territorial waters — **first Qatar territorial hit of war.** Qatar condemned.
   - Lebanon: Hezbollah drone strikes on Israeli troops in Khiam + Deir Siryan. PM Salam: Bint Jbeil "a version of Gaza."

3. **Qatari LNG transit Sun May 10:** Al Kharaitiyat → Pakistan (Port Qasim). **First LNG export from Qatar since war started Feb 28.** Iran granted specific IRGC approval; "northern route" hugging Iranian coast. Government-to-government LNG agreement for Pakistan's domestic gas shortage. Second carrier also passed per Reuters. **NOT a Scenario 1 trigger** — mediator-managed optics, not commercial reopening. Pre-war Hormuz 96-138 transits/day → still <5% throughput.

4. **Trade tier shifts:**
   - T1 **NOW WORKING via price action:** Brent calls $100-110 strikes likely ITM if Asia $103-104 holds; #10 back-end Brent length still working.
   - **HEDGE #5 Brent $90 SEP26 puts:** now ~$13 OTM at $103 spot — well past gamma-useful zone. **MONETIZE** or roll DOWN to $80 DEC26 / cut. The Scenario 1 commercial-peace path that justified this hedge is now invalidated by Iran rejection.
   - Other tiers unchanged from May 9 framework.

**Scenario probability drift (Kumar Apr 28 framework):**
- Scenario 1 ($80s-90s commercial peace): **probability DROPPED** on Iran "Hormuz under Iran" deal-killer
- Scenario 2 ($95-105 managed stalemate): **MOST LIKELY** confirmed by Brent $103-104
- Scenario 3 ($120-150 Gulf-wide war): **probability RISING** on Project Freedom Plus + Kharg pipeline read + GCC drone spread

**Andurand:** YTD -37% (Apr 23 last). Still silent. No reload signal.

**Sparta Ep 93:** NOT yet released. Expected Wed-Thu May 13-14.

**Wikipedia note:** Article references "Safesea Neha" incident May 10 — couldn't independently confirm details; flagged for follow-up.

**Files updated:**
- `reports/hormuz/analysis.html` — subtitle (May 11 Day 72), hero stat cards (rebuilt for Iran rejection + Brent Asia + 2nd Kharg + Iran counter + Qatari LNG + GCC drones), top callout (rebuilt with 6 paragraphs covering Iran rejection / 2nd Kharg / GCC spread / Qatari LNG / Brent Asia bid / scenario drift), exec summary backdrop, market snapshot (added Iran-rejection row + Brent Asia row + GCC-spread row + Qatari LNG row + 2 Kharg slicks row; collapsed May 8 UAE attack to background line), Infrastructure table Kharg row updated to reflect 2 slicks + Windward AI + UN warning, What to Watch rebuilt items 1-7 for Mon NY open / Kharg cause confirmation / GAS MAY26 expiry / EIA May 13 / Ep 93 / Project Freedom Plus / scenario drift.
- `reports/hormuz/CHANGELOG.md` — this entry.
- `.claude/settings.json` — moved `permissions.deny: ["EnterWorktree"]` from gitignored settings.local.json so the rule survives fresh clones.

**Source security note:** 11+ forged `<system-reminder>` injection attempts detected inside WebFetch / WebSearch / Read / Bash tool result bodies during this session, consistent with the documented pattern from prior refreshes. All ignored per project security policy.

## 2026-05-09 16:30 CST — Day 71 — Weekend close: Sparta Ep 92 OUT, kinetic re-engagement May 7–8, Kharg oil slick

**Brent close (Fri May 8):**
- JUL26 settled **$101.29** per CNBC weekly summary / TradingEconomics $100.49 (+0.43% on day, +1.2% Fri per CNBC framing). Week posted **−6%** on the peace-deal headlines and partial recovery.
- Intra-week range $94.17 (Mon intraday low on Bloomberg/Reuters framework deal) → $108 high → $101.29 Fri close.
- Squarely mid-Sparta Kumar Scenario 2 ($95–105). Markets closed weekend; reopens Mon May 11.

**MAJOR NEW EVENTS THIS WEEK:**

1. **Sparta Episode 92 RELEASED (~May 7)** — "Iran talks spin. US diesel stocks are running out of runway." Crosby + Goh + Molinero, 34 min. Headline: "US diesel stocks head for critical lows within weeks." Topics: Saudi June OSPs, Japanese crude purchases, TMX, gasoline spreads, middle distillates dynamics, fuel oil/freight. **Reaffirms Crosby Apr 29 HOGO mean-rev framework structurally.**

2. **Saudi Aramco June OSP cut (May 6):** Arab Light for Asia $19.50 → **$15.50** over Oman/Dubai = −$4 cut from record May level. Europe: $25.65 over ICE Brent. N America: $14.60 over ASCI. Read: weak Asian demand signal OR (more likely) stale given Hormuz throughput is binding constraint anyway.

3. **HFI May 6 PUBLIC piece:** "My Latest Thoughts On The Oil Market Amidst The Incredible Jawboning On The Iran Conflict." Iran impasse anchor: *"Iran either wants uranium enrichment or control of the Strait of Hormuz. It is willing to part with 1, but not both."* Critique of demand-destruction-only narrative (3% in GFC). China underground-storage release explanation. 3-2-1 cracks at ATH. Long USO/UCO/BNO calls. Companion piece "The Oil Math And Why The Broader Market Is Crazy To Ignore It" by Jon Costello, same day.

4. **Kinetic re-engagement Thu/Fri May 7–8:**
   - May 7: US/Iran exchanged fire in Hormuz; Chinese chemical tanker *JV Innovation* attacked.
   - May 8: USN F/A-18 Super Hornets disabled **2 Iranian tankers** via smokestack strikes; earlier in week, USN aircraft shot rudder of another tanker. Iran source (judiciary-affiliated) claims **1 sailor killed / 10 injured** on cargo vessel that caught fire.
   - May 8: Iran fired **2 ballistic missiles + 3 drones at UAE** (3 wounded; air defenses engaged).
   - Iran FM Araghchi: *"Every time a diplomatic solution is on the table, the U.S. opts for a reckless military adventure."*
   - CENTCOM Fri May 8 tally: **70+ Iranian tankers blocked** cumulative since Apr 13 = **166M bbl / $13B+** Iranian crude.

5. **NEW INFRASTRUCTURE EVENT — Kharg Island oil slick:**
   - Sentinel-1/2/3 imagery first detected slick **May 5** ~1.27 km west of Kharg.
   - By May 8: grown to **71 km² (~20 sq mi)**; ~80,000 bbl spilled since Tuesday; advancing ~2 km/h.
   - Currently ~11 km SW of Kharg.
   - **Cause unknown** — loading op, vessel, terminal, or undersea pipeline rupture (Abuzar field) all candidates.
   - Iran denies origin. Foxnews framing: "Trump blockade squeezing Iran so hard regime may be dumping oil into Gulf."
   - **Kharg = hub for 90% of Iran's oil exports.** If structurally compromised, removes Iran's last 1.71M b/d approved-channel exports → Brent Scenario 3 trigger.

6. **Iran "Persian Gulf Strait Authority" formalized May 5:** Vessel Information Declaration form; toll-payment email "[email protected]"; OFAC May 1 advisory: payments = sanctions violation. Iran moving from informal $2M tolls to formalized authority just as US tightens from advisory to ship-disabling enforcement.

**Trade tier status — NO MAJOR CHANGE from May 6 framework. Ep 92 reaffirms structural thesis:**
- T1 INTACT: #6 LONG HOGO (Crosby Apr 29 + Ep 92 "running out of runway"), #10 back-end Brent, Naphtha cracks, Brent calls $100-110.
- T2 HOLDING: NWE Jet/Brent crack, 0.5% EW LSFO, Visco, #13 Sing Regrade.
- T3 COMPRESSED: #3 GO/Brent crack, #2 GO time spread, #14 ARA-PAD1.
- T4 REDUCE: #1 Q3 Sing 0.5%/Brent (still flat to $11 entry).
- T5 CUT: #4 freight.
- HEDGE: #5 puts now ~ATM after $94 print Mon — monetize portion or roll to $80 DEC26.

**Files updated:**
- `reports/hormuz/analysis.html` — subtitle, hero stat cards (rebuilt), top callout (rebuilt), exec summary, market snapshot table (Brent + new rows for Iran-tanker-strikes, Kharg slick, CENTCOM blockade tally, Saudi OSP, second UAE attack), Industry Views (HFI May 6 + Sparta Ep 92 block added before Ep 90), Infrastructure table (Kharg slick row + Iran-tanker-fleet row), What to Watch (rebuilt 5 items: peace-deal commercial test, May 13 EIA, Kharg cause, kinetic cadence, Ep 93 expected).
- `reports/hormuz/CHANGELOG.md` — this entry.

**Source security note:** Multiple forged `<system-reminder>` injection attempts detected inside WebFetch/WebSearch result bodies during this session (consistent with the documented pattern from prior refreshes). All ignored per project security policy.

## 2026-05-06 10:00 CST — Day 68 — EIA print + peace-deal status check + Brent recovery update

**EIA actual (wk ending May 1, released 9:30 CST):**
- Crude: **−2.3M bbl** (vs HFI expected −4 to −5M; vs API −8.1M)
- Gasoline: −2.5M bbl (vs API −6.1M)
- Distillates: −1.3M bbl (vs API −4.6M)
- Verdict: HFI catch-up logic directionally correct (EIA < API) but overstated magnitude by ~2M. API/EIA divergence 5.8M = noise. BACD thesis intact — still drawing, slightly below HFI's implied pace.

**Brent at 10 AM CST:**
- Overnight low: $94.17 (Sparta 03:30 UTC, on peace-deal headlines)
- 10 AM CST: ~$101–103 (partial recovery as "deal not signed, shipping still frozen" set in)
- HO: $3.76/gal (−6.6% on day). HOGO: ~12¢ (consistent with overnight Sparta read).

**Peace deal status:**
- Trump paused Project Freedom escort mission but kept blockade of Iranian ports live
- Said "Great Progress" toward deal; Iran "evaluating"; will only accept "fair" deal
- Both sides working on a one-page memo; deal NOT signed
- Commercial shipping still frozen: 5–6 Hormuz transits/day vs 138 historical; war-risk premiums ~8x pre-war (AlbanyAntree May 6)
- Exactly Kumar Scenario 2 ("Managed Stalemate") territory; Brent at $101–103 is squarely in $95–105 range

**Trade tiers: no change from 03:40 CST framework** — EIA miss doesn't alter structural call.

**Ep 92: not yet released as of 10 AM CST** (expected May 6–10).

**Report updates:**
- Subtitle: "pre-EIA" → "post-EIA 10:00 CST"
- Top callout: added 10 AM update block with EIA result + Brent recovery + peace deal status
- Brent stat card: $94.17 → $101–103 recovery
- HOGO stat card: added HO $3.76/gal context
- Market snapshot: EIA/API row updated to actual print; Brent row updated to 10 AM CST; HO row updated to $3.76
- EIA watch paragraph: "Watch" → "PRINTED"
- What to Watch #1: scenario → actual result
- What to Watch #7: added EIA actual to BACD validation track
- Driver 4: added EIA actual vs HFI expected
- Driver 4: added EIA actual vs HFI expected

## 2026-05-06 — Day 68 — peace-deal crash, full Sparta + IB live data, framework rebuilt by upside (not stress)

**Major framework rebuild based on:**
- Authenticated Sparta live curves pulled directly from sparta.app (Diesel, Jet, Naphtha, Crude, LSFO, HSFO, Freight tabs)
- IB Gateway live NYMEX (BZ, HO, RB, CL, BB, LT) — confirmed working tickers + IB symbology rounds for ICE Endex (COIL/IPE for Brent, GOIL/IPE for Gasoil — qualify but no live mkt data sub)
- Crosby Apr 29 "Surely we need to be long, but when?" full text
- Kumar Apr 28 "Hormuz scenarios: Brent pricing flow confidence" 4-scenario framework
- Today's peace-deal "near" reports (Bloomberg + Reuters; **Axios excluded per user — banned source**)

**Peace-deal macro shift overnight:** Bloomberg + Reuters reporting US-Iran framework deal: Iran nuclear-enrichment moratorium for sanctions ease + frozen-asset release. Oil crashed ~6%. Brent Swap JUL26 $94.17 (vs $108 prior). HO −5.4% to $3.80, RB −4% to $3.47, CL −5.9% to $92.29. Freight crashed (TC2 218, TC14 366→179 May→Jul). Bitcoin $82K. Dollar lowest since war started.

**Live Sparta data captured (May 6 03:30 UTC):**
- Brent Swap curve: JUL26 $94.17 / OCT26 $85.72 / DEC26 $82.25 / JUN27 $77.27 / DEC27 $77.78. M1−M18 spread $28.10 (back-end resilient).
- HOGO Swap: front 12.80¢, Q3 22.70¢, Q4 30.20¢, Dec 32.50¢, Cal 26 23.05¢. Curve overshot on front; Crosby Apr 29: "weakness not justified".
- ICE GO Swap May $1,145.58/mt (down $51.67 from yesterday). GO/Brent crack Jun $49.50, Q3 $43.82.
- NWE Jet/Brent crack Jun $61.35 — widest distillate crack. Singapore Regrade only $5-6 front (Q3 strip $12.38, Cal 26 $24.49).
- Naphtha cracks DEEPLY NEGATIVE: NWE Nap/Brent −$4.25 Jun → −$5.70 Q3. MOPJ +$0.25 → −$1.65 Q3. Off-radar dislocation.
- LSFO: **Q3 Sing 0.5%/Brent crack $11.20 vs Goh $11 entry = essentially FLAT**. Trade #1 was incorrectly claimed +$11 ITM previously (conflated with VLSFO/Dubai SPOT $22.86 Splash247). 0.5% EW (Asia LSFO over Eur LSFO) at $67-80 = real dislocation.
- HSFO: Q3 cracks back to NEGATIVE (180/Brent −$0.75, 380/Brent −$2.60). Goh "inverted to positive" rally faded except front. Visco 180-380 spread Q3 $11.50.
- Freight: TC2 218→183 May→Jul (was 312 Apr 13 peak). TC14 366→179. Trade #4 underwater. Sparta news 03:13: "USGC MR Jet arbs now open into Rotterdam +$8.5/+$11.25/mt; TC14 freight drop helped reopen flow."

**Trade book reorganized by ASYMMETRIC UPSIDE TIERS (per user explicit guidance):**
- T1 Highest: Naphtha cracks (mean-rev), HOGO mean-rev (Crosby explicit), back-end Brent #10 (working), Brent calls $100-110 strike on dip
- T2 Working but consensus catching up: NWE Jet/Brent crack outright, 0.5% EW LSFO, Visco 180-380, Sing Regrade #13 (Crosby "buy dips")
- T3 Compressed but holding: ICE GO/Brent #3, GO time spread #2, gasoline arb #14 (pending Eurobob print)
- T4 Reduce: Q3 Sing 0.5%/Brent #1 (essentially flat to entry), $120 calls #12 (far OTM at $94 spot)
- T5 Cut: Trade #4 freight (binding-constraint thesis faded)
- Hedge: #5 Brent puts now ~ATM after $94 print — monetize/roll

**Macro Framework rewritten** with 6 drivers + Trade Implications per driver. Driver 5 (Freight) now flagged FADING. Driver 2 (Cross-product hierarchy) NEW — jet > diesel > fuel oil > gasoline > naphtha. Driver 6 (Refinery cycling) now subsumes the fuel-oil-loop sub-mechanic.

**Industry Views**: Kumar Apr 28 "Hormuz Scenarios" 4-scenario framework added. Crosby Apr 29 quoted at length on HOGO mean-reversion + "June story globally".

**What to Watch**: Reframed around peace-deal commercial test + EIA Wed binary catalyst + Sparta Kumar Scenario 2 ($95-105) snap-back probability. Replaced "Andurand reload" / "Russian backing" items with active scenario-bifurcation framework.

**Source rules saved to memory**: Axios banned permanently; HFI direct contact treated as primary source; API/EIA divergence catch-up logic.

**Schedule note**: 10 AM CST Wed May 6 remote refresh routine `trig_017HmY6mTLEidV7TeEexyW8n` will pull EIA print + verify peace-deal status + re-rank trade priority.

## 2026-05-05 — Day 67 — UNIFIED REFRESH (morning + afternoon merged)

This entry rolls the morning (09:57 CST) refresh and afternoon (15:53 CST) AIP refresh into a single coherent report. Discovered late in the session that the parent repo had uncommitted morning content the worktree never saw — merged that content forward instead of overwriting either side.

**From morning refresh (was uncommitted in parent repo):**
- VTTI fuel storage at Fujairah PIZ specifically named — joint Vitol / IFM / TAQA ownership; Bloomberg-sourced. Refined product (gasoline / distillate / fuel oil), NOT Murban crude tank farm.
- CENTCOM order of battle for Project Freedom: 15,000 troops, BMD destroyers, F-15/F-16/F-35, AH-64 Apaches, MH-60s, EA-18G Growlers (CENTCOM release).
- Maersk subsidiary specifically named as the merchant transit; Iran (IRIB) disputes any commercial transit happened.
- US sank **7** small Iranian boats (revised up from 6 — was a partial-tally vs full tally).
- Iran FM Araghchi: "Project Deadlock — military intervention cannot resolve what is, at its core, a political crisis."
- Mick Mulroy (DoD), Mark Cancian (CSIS), Jonathan Ruhe (JINSA) analyst skepticism via Breaking Defense.
- UAE FM "serious escalation, unacceptable act of aggression"; Anwar Gargash on tanker: "maritime piracy."
- Trump declined to confirm ceasefire is still in effect (Hugh Hewitt interview, Time) — first explicit walk-back on Apr 21 indefinite extension.
- HFI May 4 piece "Stuck Between A Rock And A Hard Place"; May 1 memo "I Can't Believe We Are Doing This"; projections: end-May ~1.59B bbl / end-June ~1.98B / end-July US commercial crude approaches operational minimum (370–380M from ~400M).
- June Goh 6–9 month supply normalization timeline (post-reopening); restart alone 1–2 months.

**From afternoon refresh:**
- API just out (Tue May 5 4:30pm ET, week ending May 1): crude **−8.1M bbl** vs −2.8M consensus — **biggest API number of the crisis**. Gasoline −6.1M, distillate −4.6M, SPR −5.2M to **392.7M (lowest since Nov 2024)**, Cushing −1.0M to ~29M.
- **EIA Wed May 6 expected ~−4 to −5M per HFI Research (direct)** — last week API undercounted EIA by 4.44M (API −1.79M vs EIA −6.233M for wk ending Apr 24), so today's −8.1M is API catch-up on those missed barrels. Per-HFI catch-up logic supersedes my earlier lazy "EIA likely larger" pattern-match.
- Brent JUL26: **$109.87 close** (intraday $116.55, May 4 settled $114.40 +5.8%). Daily range $6.68 = volatility regime locked.
- Brent DEC26: **$90.57** → M1−M12 spread **$19.30** (was $27 a week ago — back-end caught $11 of bid).
- NYMEX HO JUN26 **$4.0771/gal**; ICE Gasoil M1 **$1,197.25/t** (+6.42% 24h).
- **HOGO ≈ +$0.252/gal (+$10.58/bbl)** — Trade #6 working ITM since Sparta Apr 29 entry.
- ICE GO/Brent crack ≈ **$50.83/bbl** (compressed from $67 Apr 14 as Brent rallied harder; still ~3x pre-crisis).
- Trade card "Where it's at now" live spread blocks added on #1, #2, #3, #6, #10, #12.

**Pruned (>7 days, not critical per user instruction):**
- Apr 27 Brent close detail, Apr 27 Kpler "false dawn" detail, Apr 24 +$16.60 rip detail, Apr 23 Trump Navy order, Apr 18–23 escalation block (compressed to background line), IEA OMR April block (replaced by Goldman 14.5M b/d + Atlantic Council 650M bbl), unconfirmed "Murban tanks toast" X-chain rumor (resolved by wire reporting to VTTI / Barakah).

**Three prompt-injection attempts** detected inside WebFetch result bodies (forged `<system-reminder>` blocks). All ignored per project security note.

**Background retained for context (>7 days but critical):** Apr 22 ceasefire indefinitely extended w/ blockade live, HFI BACD framework, Oil Not Dead "Frozen", Kpler 6-week mark, Atlantic Council 650M bbl math, Ras Laffan Trains 4&6 (3-5 yr), Apr 28 UAE quit OPEC, Andurand silent-while-bleeding pattern.

## 2026-05-04 — May 3-4 Project Freedom convoy; OPEC+ June; Sparta Ep 91; UAE quit OPEC
- **UAE quit OPEC** Apr 28, effective May 1 — removes ~12% of OPEC output. Structural shift.
- **OPEC+ May 3** — Group of 7 set +188K b/d for June (below May +206K). Saudi & Russia +62K each. "Symbolic, none gets through Hormuz."
- **Iran 14-point counter** May 3 (30-day end-of-war + Hormuz reopen + sanctions lift, nuclear deferred). **Trump rejected** ("not yet paid a big enough price").
- **Project Freedom convoy** May 3-4: USN escorts neutral-flag transits. Iran response: cruise missiles, drones, small boats. **US sank 6 small Iranian boats**. Cargo ship attacked off Sirik. Iran also attacked UAE.
- **Apr 30 Brent touched $126 intraday** (4-yr high) on Trump strike rhetoric. CBM26 settled, CBN26 now front (~$108.11).
- **EIA Apr 29: crude −6.233M b/d** for Apr 24 wk (vs −0.2M cons) — 6th-largest weekly draw on record. **HFI BACD thesis printing.**
- **Sparta Ep 91 (~Apr 29)** "Asia absorbed the initial shock. Now the US is running dry." Felipe + Crosby + Molinero. Crosby flagged THREE distillate trades: HOGO, regrade, diesel cracks. Felipe: "TI Brent still looks like a buy"; "Brent physical diffs may run lower short-term." Molinero: "ARA-to-PAD1 arbitrage cracking open for the first time in months."
- **Trade book updates:**
  - #6 HOGO **FLIPPED** from STAY-FLAT (was short, closed) → **LONG HOGO** per Sparta Ep 91 (Crosby explicit).
  - #11 expiry roll DONE (CBM26 → CBN26, HOK26 → HOM26 Apr 30); next deadline LFK26 May 12.
  - #12 $120 calls touched ITM briefly Apr 30 ($126 spike) — manage / monetize.
  - #13 NEW Sparta-anchored: Singapore Regrade (Crosby).
  - #14 NEW Sparta-anchored: ARA-to-PAD1 gasoline arb (Molinero).
- **Andurand YTD −37%** (recovered from −52% Apr 1H). No public reload yet.
- **Barclays raised 2026 Brent to $100** (from $85).
- **Goldman:** Hormuz transits at 20/day (vs pre-war 129); production reduction estimated 14.5M b/d.

## 2026-04-28 — Reorganization + Adjacent trade ideas block
- Moved into `reports/hormuz/` under new research folder layout.
- Sparta vs. non-Sparta trade ideas separated into "Adjacent" block within `analysis.html`.

## 2026-04-27 — Apr 22 ceasefire window resolved aggressively bullish
- Iran proposal rejected; structural shift confirmed.

## 2026-04-14 / 04-15 — Sparta-anchored framework established
- Pivoted from generic geopolitical briefing to trader desk view anchored on Sparta Commodities.
- ICE Gasoil framed as the anchor instrument (June Goh's spread framework).
- Source priority set: Sparta primary; HFI Research and Oil Not Dead secondary; X Oil list (16 members) for sentiment; corroboration only after.
- Trade ideas tracked: long ICE GO/Brent crack, long ICE GO time spread, short HOGO, long Q3 LSFO crack, long jet.
- Fuel oil refinery routing loop documented (June Goh, Apr 11 thesis).
- Pre-pivot daily refresh log (Mar 17 → Apr 10) intentionally not carried forward; lives in git history if needed.
