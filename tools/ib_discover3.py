"""IB symbology discovery — round 3, exhaustive on gaps.

Confirmed working: GOIL/IPE (ICE Gasoil), COIL/IPE (ICE Brent), BZ/NYMEX,
HO/NYMEX, RB/NYMEX, CL/NYMEX.

Still chasing: Murban, Sing Marine Fuel 0.5%, Sing Jet Regrade, Sing Gasoil
0.05%, Sing Jet Kerosene, Naphtha (Asia/NWE), HSFO/LSFO swaps, NWE Gasoil,
Gulf Coast ULSD spread.
"""
import asyncio, json
from ib_async import IB, Future, ContFuture, util
util.patchAsyncio()

# Try permutations of (symbol, exchange) for each product family.
# Goal: find which (sym, exch) qualifies as FUT on IB.
TESTS = [
    # NYMEX-traded indices that hint at FUT availability
    ("HZ",  "NYMEX"),  # Sing 380 fuel oil
    ("GR",  "NYMEX"),  # NWE Gasoil
    ("LT",  "NYMEX"),  # Gulf Coast ULSD Platts up-down
    ("SC",  "NYMEX"),  # NYMEX Brent index
    ("QB",  "NYMEX"),  # Europe Miny Brent
    ("BB",  "NYMEX"),  # Brent Financial Futures
    # Sing Marine Fuel 0.5% — try every exchange code I can think of
    ("MFB", "NYMEX"), ("MFB", "CME"), ("MFB", "GLOBEX"), ("MFB", "SGX"),
    ("MFB", "ICEUS"), ("MFB", "IFEU"),
    # Marine Fuel 0.5% vs Brent crack
    ("MFV", "NYMEX"), ("MFV", "CME"), ("MFV", "GLOBEX"),
    # Sing Jet Kerosene (Platts) — CME code AKB, also try
    ("AKB", "CME"), ("AKB", "GLOBEX"), ("JKB", "CME"), ("JKB", "GLOBEX"),
    # Sing Jet Regrade — CME code RKA
    ("RKA", "CME"), ("RKA", "GLOBEX"), ("RKA", "ICEUS"), ("RKA", "ICEEU"),
    # Sing Gasoil (Platts) — CME code SGB
    ("SGB", "CME"), ("SGB", "GLOBEX"),
    # Murban — IB code is ADM on IFEU per ICE docs
    ("ADM", "IFEU"), ("ADM", "IFAD"), ("ADM", "ICEEU"),
    ("MUR", "IFEU"), ("MURBAN", "IFEU"),
    # Naphtha NWE Argus / Platts — ICE codes DKE, NDE; CME codes
    ("DKE", "IPE"), ("DKE", "ICEEU"), ("DKE", "IFEU"),
    ("DKF", "IPE"), ("NDE", "NYMEX"), ("NDE", "CME"),
    ("NPN", "NYMEX"), ("NPC", "NYMEX"), ("NPP", "NYMEX"),
    # Naphtha Japan (MOPJ) — CME code
    ("MAJ", "CME"), ("MAJ", "GLOBEX"), ("MAJ", "NYMEX"),
    ("MOJ", "CME"), ("MOJ", "GLOBEX"),
    # Sing Naphtha — CME code SAJ?
    ("SAJ", "CME"), ("SAJ", "GLOBEX"),
    # HSFO 380 / 180
    ("UV", "NYMEX"), ("UA", "NYMEX"),  # different products
    ("FOM", "NYMEX"), ("FO",  "NYMEX"),
    ("HSF", "CME"), ("HSF", "GLOBEX"),
    # E/W spread products
    ("EW",  "NYMEX"), ("EWS", "NYMEX"), ("EWE", "NYMEX"),
    # Common CME refined product spread codes
    ("NCG", "CME"), ("NCF", "CME"),
]

EXPIRIES = ["202606", "202607"]


async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=11, timeout=8)
    out = []

    for sym, exch in TESTS:
        for exp in EXPIRIES:
            c = Future(symbol=sym, lastTradeDateOrContractMonth=exp,
                       exchange=exch, currency="USD")
            try:
                qd = await ib.reqContractDetailsAsync(c)
                if qd:
                    rec = qd[0]
                    out.append({
                        "tried": f"{sym}/{exch}/{exp}",
                        "MATCH": True,
                        "longName": rec.longName,
                        "ltd": rec.contract.lastTradeDateOrContractMonth,
                        "mult": rec.contract.multiplier,
                        "primaryExch": rec.contract.primaryExchange,
                        "currency": rec.contract.currency,
                        "tradingClass": rec.contract.tradingClass,
                    })
                    break  # Don't test second expiry if first works
            except Exception:
                pass

    # Also do contFuture lookups (continuous front month) — sometimes
    # ContFuture qualifies even when specific expiry doesn't
    contfutures = [
        ("GOIL", "IPE"), ("COIL", "IPE"), ("BZ", "NYMEX"),
        ("ADM", "IFEU"), ("MFB", "NYMEX"), ("AKB", "NYMEX"),
        ("RKA", "NYMEX"), ("SGB", "NYMEX"), ("DKE", "NYMEX"),
    ]
    out.append({"--- contfutures ---": ""})
    for sym, exch in contfutures:
        cf = ContFuture(symbol=sym, exchange=exch, currency="USD")
        try:
            qd = await ib.reqContractDetailsAsync(cf)
            if qd:
                rec = qd[0]
                out.append({"contfuture": f"{sym}/{exch}", "MATCH": True,
                            "longName": rec.longName,
                            "tradingClass": rec.contract.tradingClass})
        except Exception as e:
            pass

    # Broader searches focused on what I missed
    extra_searches = ["DIESEL", "ULSD", "ASIA", "MOPJ", "MOPS", "LSFO",
                      "MARINE", "BUNKER", "DIRTY", "CLEAN", "GROWTH",
                      "HEATING OIL", "GASOLINE", "RBOB", "ETHANOL", "PROPANE",
                      "BUTANE", "LPG", "EAST WEST", "CRACK"]
    out.append({"--- extra_searches ---": ""})
    for s in extra_searches:
        try:
            res = await ib.reqMatchingSymbolsAsync(s)
            interesting = [r for r in res if r.contract.secType in ("FUT","IND","CMDTY")
                          and "OIL" in (getattr(r.contract,"description","") or "").upper()
                          or "FUEL" in (getattr(r.contract,"description","") or "").upper()
                          or "GAS" in (getattr(r.contract,"description","") or "").upper()
                          or "DIESEL" in (getattr(r.contract,"description","") or "").upper()
                          or "JET" in (getattr(r.contract,"description","") or "").upper()
                          or "CRUDE" in (getattr(r.contract,"description","") or "").upper()]
            if interesting:
                out.append({"search": s, "hits": [
                    {"sym": r.contract.symbol, "primary": r.contract.primaryExchange,
                     "cur": r.contract.currency,
                     "desc": getattr(r.contract,"description",None)}
                    for r in interesting[:8]]})
        except Exception as e:
            pass

    ib.disconnect()
    print(json.dumps(out, indent=2, default=str))

asyncio.run(main())
