"""IB symbology discovery — round 2, comprehensive.

Lessons from round 1: reqMatchingSymbols returns IND/STK rows even when
the symbol IS tradeable as FUT. Always test Future() directly with the
returned symbol. Don't assume secType from search.
"""
import asyncio, json
from ib_async import IB, Future, Contract, util
util.patchAsyncio()

# Direct Future-construction tests on every plausible symbol+exchange combo
DIRECT_TESTS = [
    # ICE Gasoil — user confirmed ticker is GOIL
    ("GOIL", "IPE",   "USD", "202606"), ("GOIL", "IPE",   "USD", "202607"),
    ("GOIL", "ICEEU", "USD", "202606"), ("GOIL", "ICEEUSOFT", "USD", "202606"),
    ("GOIL", "NYBOT", "USD", "202606"),
    # ICE Brent — actual ICE (not cash-settled NYMEX BZ)
    ("BRN", "IPE",   "USD", "202607"), ("BRN", "ICEEU",  "USD", "202607"),
    ("BRN", "NYBOT", "USD", "202607"), ("BRN", "ICEEUSOFT", "USD", "202607"),
    ("CO",  "IPE",   "USD", "202607"), ("COIL","IPE",   "USD", "202607"),
    # Murban — ICE Futures Abu Dhabi
    ("MUR", "IFAD",  "USD", "202607"), ("MUR", "IFEU",  "USD", "202607"),
    ("MUR", "ICEEU", "USD", "202607"), ("MUR", "IPE",   "USD", "202607"),
    ("MURB","IFAD",  "USD", "202607"), ("MUR", "NYMEX", "USD", "202607"),
    # CME Sing Marine Fuel 0.5% — try common product codes
    ("MFB", "NYMEX", "USD", "202607"), ("MF0", "NYMEX", "USD", "202607"),
    ("S05", "NYMEX", "USD", "202607"), ("MFP", "NYMEX", "USD", "202607"),
    ("PMI", "NYMEX", "USD", "202607"),
    # CME Sing Jet Regrade — try product codes
    ("RKA", "NYMEX", "USD", "202606"), ("JKB", "NYMEX", "USD", "202606"),
    ("AKB", "NYMEX", "USD", "202606"), ("SJK", "NYMEX", "USD", "202606"),
    ("FFB", "NYMEX", "USD", "202606"),
    # Singapore Gasoil 0.05% (Platts) — for jet regrade computation
    ("SGB", "NYMEX", "USD", "202606"), ("SG", "NYMEX", "USD", "202606"),
    ("0G", "NYMEX", "USD", "202606"),
    # Singapore Jet Kerosene (Platts)
    ("AKB", "SGX",   "USD", "202606"),
    # Naphtha — Asia (MOPJ) and NWE
    ("NAP", "NYMEX", "USD", "202606"), ("DKE", "NYMEX", "USD", "202606"),
    ("DKF", "NYMEX", "USD", "202606"), ("NPP", "NYMEX", "USD", "202606"),
    ("NWE", "NYMEX", "USD", "202606"), ("MOJ", "NYMEX", "USD", "202606"),
    # Fuel Oil 380 / 180
    ("UA",  "NYMEX", "USD", "202607"), ("UV",  "NYMEX", "USD", "202607"),
    ("FOM", "NYMEX", "USD", "202607"), ("HSF", "NYMEX", "USD", "202607"),
]

# Broader searches than round 1
SEARCHES = ["ICE BRENT", "BRENT", "GASOIL", "GOIL", "MURBAN", "ABU DHABI",
            "JET", "JET KEROSENE", "MARINE FUEL", "MARINE 0.5", "FUEL OIL",
            "VLSFO", "HSFO", "NAPHTHA", "REGRADE", "EFS", "PLATTS",
            "SINGAPORE GASOIL", "SINGAPORE JET", "ASIA NAPHTHA", "NWE NAPHTHA"]


async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=10, timeout=8)

    out = {"direct_futures": [], "searches": {}}

    # Round A: direct Future construction — qualifyContracts will succeed
    # IFF the contract exists in IB's universe (regardless of mkt-data sub)
    for sym, exch, cur, expiry in DIRECT_TESTS:
        c = Future(symbol=sym, lastTradeDateOrContractMonth=expiry,
                   exchange=exch, currency=cur)
        try:
            qd = await ib.reqContractDetailsAsync(c)
            if qd:
                out["direct_futures"].append({
                    "tried": f"{sym}/{exch}/{expiry}",
                    "found": [{"sym": x.contract.symbol, "exch": x.contract.exchange,
                               "ltd": x.contract.lastTradeDateOrContractMonth,
                               "longName": x.longName, "mult": x.contract.multiplier,
                               "secType": x.contract.secType} for x in qd[:3]]
                })
        except Exception as e:
            pass  # Ignore failures, we expect many

    # Round B: broader search strings
    for s in SEARCHES:
        try:
            res = await ib.reqMatchingSymbolsAsync(s)
            # Filter to FUT and IND (which often hint at FUT availability)
            interesting = [r for r in res if r.contract.secType in ("FUT", "IND", "CMDTY")]
            out["searches"][s] = [{"sym": r.contract.symbol, "exch": r.contract.exchange,
                                    "primary": r.contract.primaryExchange,
                                    "secType": r.contract.secType, "cur": r.contract.currency,
                                    "desc": getattr(r.contract, "description", None)}
                                   for r in interesting[:10]]
        except Exception as e:
            out["searches"][s] = {"error": str(e)[:120]}

    ib.disconnect()
    print(json.dumps(out, indent=2, default=str))

asyncio.run(main())
