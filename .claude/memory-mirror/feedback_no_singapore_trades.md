---
name: No Singapore-product trades
description: Skip any trade idea where the primary instrument is a Singapore product (Sing Regrade, E/W Gasoil, Sing 0.5%, Sing Kero, Visco, etc.) — user has no execution path
type: feedback
originSessionId: ffab3716-767f-4057-9da9-1ec01fe922ca
---
Do not put any Singapore-product trade in the active trade book. User has no way to execute Singapore-product spreads on retail IB or any other available platform.

**Why:** Confirmed 2026-05-11. User does not have ICE-Singapore market data, SGX FOB Singapore Gasoil swap access (`SHO`), or any Asia-cleared platform that would let Sing Regrade / E/W Gasoil / Sing 0.5%/Brent / Sing Kero/Dubai / Visco (HSFO 180-380) execute. Sparta's framework leans heavily on Singapore products because Goh sits in Singapore — but those calls are watch-only at best for this user.

**How to apply:**

- **Skip entirely from active trade book:** Sing Regrade (Jet vs Sing Gasoil), Long/Short E/W Gasoil (Sing GO vs ICE GO), Q3 Sing 0.5%/Brent, Q3 Sing HSFO/Brent, 0.5% East-West (Sing 0.5% − Eur 0.5%), Visco (HSFO 180-380), Sing Kero outright, Sing Naphtha, Sing diesel cracks, SGX clean tankers (TC7, TC11, TC12).
- **DO keep Singapore as market color / context.** Sing market levels are useful framing for the broader thesis (e.g., "Sing 0.5% crack printed $11 → $15 = Goh's Ep 90 call working" is fine as proof-point for the framework, just NOT as a trade idea).
- **When Sparta explicit calls are Singapore-only** (e.g., Crosby Ep 92 "buy regrade again"), note that the call exists and is directionally bullish for the framework, but do NOT add it as a trade. Pivot to the Atlantic / US-domestic expression of the same physical view if one exists (e.g., NWE Jet/Brent crack instead of Sing Regrade; Long HOGO instead of E/W Gasoil; Long ICE GO/Brent crack as the cross-region distillate expression).
- **Tradable Sparta categories that DO work:** ICE Gasoil (front and back, time spreads, GO/Brent crack), ICE Brent (outright, calendar spreads, calls/puts), NYMEX Heating Oil (outright, HOGO), NYMEX WTI (outright, calendar, BZ-CL diff), NYMEX RBOB, NYMEX gasoil, USD-denominated FFAs if user has FFA access.
