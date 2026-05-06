"""IB symbology discovery — round 4. Lean, parallel, file-output.

Tests futures by direct construction in parallel via asyncio.gather.
Writes to results.json so we can check progress while running.
"""
import asyncio, json, sys
from pathlib import Path
from ib_async import IB, Future, util
util.patchAsyncio()

OUT = Path("/Users/mikemadden/Desktop/Claude Projects/research/.claude/worktrees/elegant-pasteur-58d995/tools/ib_results.json")

# (symbol, exchange) — every plausible combo for the gaps
TESTS = [
    # NYMEX-traded futures whose IND form was found in search
    ("HZ", "NYMEX"), ("GR", "NYMEX"), ("LT", "NYMEX"),
    ("SC", "NYMEX"), ("QB", "NYMEX"), ("BB", "NYMEX"),
    # Murban — ICE Futures Abu Dhabi (IFAD per docs, IFEU sometimes)
    ("ADM", "IFEU"), ("ADM", "IFAD"), ("ADM", "ICEEU"),
    ("MUR", "IFEU"), ("MURBAN", "IFEU"),
    # CME Globex Singapore products — try alt exchange codes
    ("MFB", "NYMEX"), ("MFB", "CMEN"), ("MFB", "GLOBEX"),
    ("AKB", "NYMEX"), ("AKB", "CMEN"), ("AKB", "GLOBEX"),
    ("RKA", "NYMEX"), ("RKA", "CMEN"), ("RKA", "GLOBEX"),
    ("SGB", "NYMEX"), ("SGB", "CMEN"), ("SGB", "GLOBEX"),
    # Naphtha
    ("DKE", "NYMEX"), ("DKE", "IPE"), ("DKE", "IFEU"),
    ("DKF", "NYMEX"), ("DKF", "IPE"),
    ("MAJ", "NYMEX"), ("MAJ", "IPE"),
    # Fuel oil
    ("FOM", "NYMEX"), ("UA", "NYMEX"), ("UV", "NYMEX"),
    ("HZ", "NYMEX"),
]

EXP = "202607"


async def test_one(ib, sym, exch, exp):
    c = Future(symbol=sym, lastTradeDateOrContractMonth=exp,
               exchange=exch, currency="USD")
    try:
        qd = await asyncio.wait_for(ib.reqContractDetailsAsync(c), timeout=4)
        if qd:
            r = qd[0]
            return {
                "tried": f"{sym}/{exch}",
                "MATCH": True,
                "longName": r.longName,
                "ltd": r.contract.lastTradeDateOrContractMonth,
                "mult": r.contract.multiplier,
                "tradingClass": r.contract.tradingClass,
                "primaryExch": r.contract.primaryExchange,
                "currency": r.contract.currency,
            }
    except (asyncio.TimeoutError, Exception):
        pass
    return None


async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=12, timeout=8)

    # Run all tests in parallel — ib_async multiplexes on the socket
    tasks = [test_one(ib, s, e, EXP) for s, e in TESTS]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    matches = [r for r in results if r and r.get("MATCH")]

    OUT.write_text(json.dumps(matches, indent=2, default=str))
    ib.disconnect()
    print(f"Wrote {len(matches)} matches to {OUT}", flush=True)
    print(json.dumps(matches, indent=2, default=str), flush=True)

asyncio.run(main())
