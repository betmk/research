# Hormuz — Changelog

Living log of refresh deltas. Newest first.

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
