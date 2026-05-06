"""Pull live futures quotes from IB Gateway (port 4001).

Symbology confirmed via discovery:
- Brent: BZ on NYMEX (cash-settled, equiv to ICE Brent)
- HO/RB/CL: NYMEX (work)
- ICE Gasoil, Sing Marine Fuel, Sing Regrade, Murban: NOT in user subs.
"""
import asyncio, json
from ib_async import IB, Future, util
util.patchAsyncio()

WANTS = [
    # Brent curve — cash-settled NYMEX Brent (equiv to ICE Brent)
    ("BZ",  "NYMEX", "USD", "202607", "Brent JUL26 (BZ)"),
    ("BZ",  "NYMEX", "USD", "202608", "Brent AUG26"),
    ("BZ",  "NYMEX", "USD", "202609", "Brent SEP26"),
    ("BZ",  "NYMEX", "USD", "202610", "Brent OCT26"),
    ("BZ",  "NYMEX", "USD", "202611", "Brent NOV26"),
    ("BZ",  "NYMEX", "USD", "202612", "Brent DEC26"),
    ("BZ",  "NYMEX", "USD", "202703", "Brent MAR27"),
    ("BZ",  "NYMEX", "USD", "202706", "Brent JUN27"),
    ("BZ",  "NYMEX", "USD", "202712", "Brent DEC27"),
    # NYMEX Heating Oil — for #6 HOGO US leg
    ("HO",  "NYMEX", "USD", "202606", "NYMEX HO JUN26"),
    ("HO",  "NYMEX", "USD", "202607", "NYMEX HO JUL26"),
    ("HO",  "NYMEX", "USD", "202608", "NYMEX HO AUG26"),
    ("HO",  "NYMEX", "USD", "202609", "NYMEX HO SEP26"),
    # RBOB — for #14 + summer driving check
    ("RB",  "NYMEX", "USD", "202606", "RBOB JUN26"),
    ("RB",  "NYMEX", "USD", "202607", "RBOB JUL26"),
    ("RB",  "NYMEX", "USD", "202608", "RBOB AUG26"),
    # WTI for cross-check + spread vs Brent
    ("CL",  "NYMEX", "USD", "202606", "WTI JUN26"),
    ("CL",  "NYMEX", "USD", "202607", "WTI JUL26"),
    ("CL",  "NYMEX", "USD", "202612", "WTI DEC26"),
]


async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=9, timeout=8)
    out = []
    for sym, exch, cur, expiry, label in WANTS:
        c = Future(symbol=sym, lastTradeDateOrContractMonth=expiry,
                   exchange=exch, currency=cur)
        try:
            qd = await ib.qualifyContractsAsync(c)
            if not qd:
                out.append({"label": label, "sym": sym, "expiry": expiry, "status": "not qualified"})
                continue
            qc = qd[0]
            ib.reqMktData(qc, "", False, False)
            await asyncio.sleep(2.5)
            t = ib.ticker(qc)
            row = {
                "label": label, "sym": sym, "expiry": expiry,
                "ltd": qc.lastTradeDateOrContractMonth,
                "last": t.last if t.last == t.last else None,
                "close": t.close if t.close == t.close else None,
                "bid": t.bid if t.bid == t.bid else None,
                "ask": t.ask if t.ask == t.ask else None,
                "mark": t.marketPrice() if t.marketPrice() == t.marketPrice() else None,
            }
            out.append(row)
            ib.cancelMktData(qc)
        except Exception as e:
            out.append({"label": label, "error": str(e)[:120]})

    ib.disconnect()
    print(json.dumps(out, indent=2, default=str))

asyncio.run(main())
