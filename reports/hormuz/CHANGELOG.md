# Hormuz — Changelog

Living log of refresh deltas. Newest first.

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

**Background retained for context (>7 days but critical):** Apr 22 ceasefire indefinitely extended w/ blockade live, HFI BACD framework, Oil Not Dead "Frozen", Kpler 6-week mark, Atlantic Council math, Ras Laffan Trains 4&6 (3-5 yr), Apr 28 UAE quit OPEC, Andurand silent-while-bleeding pattern.

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
