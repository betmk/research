"""IB live quote pull v2 — using all confirmed-working symbols.

Confirmed FUT contracts (all on user's IB):
- COIL/IPE = ICE Brent Crude (real ICE, mult=1000 bbl)
- GOIL/IPE = ICE Gasoil (mult=100 mt)
- BZ/NYMEX = Cash-settled Brent
- BB/NYMEX = NYMEX Brent Financial Futures Index
- HO/NYMEX = Heating Oil (42000 gal)
- RB/NYMEX = RBOB (42000 gal)
- CL/NYMEX = WTI (1000 bbl)
- LT/NYMEX = Gulf Coast ULSD Platts Up-Down (42000 gal)
- QM/NYMEX = Mini WTI
"""
import asyncio, json
from ib_async import IB, Future, util
util.patchAsyncio()

WANTS = [
    # Brent curve — REAL ICE Brent (not BZ)
    ("COIL","IPE",  "USD","202607","ICE Brent JUL26"),
    ("COIL","IPE",  "USD","202608","ICE Brent AUG26"),
    ("COIL","IPE",  "USD","202609","ICE Brent SEP26"),
    ("COIL","IPE",  "USD","202610","ICE Brent OCT26"),
    ("COIL","IPE",  "USD","202612","ICE Brent DEC26"),
    ("COIL","IPE",  "USD","202703","ICE Brent MAR27"),
    ("COIL","IPE",  "USD","202706","ICE Brent JUN27"),
    ("COIL","IPE",  "USD","202712","ICE Brent DEC27"),
    # ICE Gasoil curve — for #2 calendar, #3 crack, #6 HOGO
    ("GOIL","IPE",  "USD","202605","ICE Gasoil MAY26"),
    ("GOIL","IPE",  "USD","202606","ICE Gasoil JUN26"),
    ("GOIL","IPE",  "USD","202607","ICE Gasoil JUL26"),
    ("GOIL","IPE",  "USD","202608","ICE Gasoil AUG26"),
    ("GOIL","IPE",  "USD","202609","ICE Gasoil SEP26"),
    # NYMEX HO + RB + CL + LT (Gulf Coast ULSD)
    ("HO",  "NYMEX","USD","202606","NYMEX HO JUN26"),
    ("HO",  "NYMEX","USD","202607","NYMEX HO JUL26"),
    ("RB",  "NYMEX","USD","202606","RBOB JUN26"),
    ("RB",  "NYMEX","USD","202607","RBOB JUL26"),
    ("CL",  "NYMEX","USD","202607","WTI JUL26"),
    ("LT",  "NYMEX","USD","202607","Gulf Coast ULSD Up-Down JUL26"),
]

async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=15, timeout=8)
    out = []
    for sym,exch,cur,exp,label in WANTS:
        c = Future(symbol=sym, lastTradeDateOrContractMonth=exp,
                   exchange=exch, currency=cur)
        try:
            qd = await ib.qualifyContractsAsync(c)
            if not qd:
                out.append({"label": label, "status": "not qualified"})
                continue
            qc = qd[0]
            ib.reqMktData(qc, "", False, False)
            await asyncio.sleep(2.0)
            t = ib.ticker(qc)
            row = {"label": label, "sym": sym, "exch": exch, "expiry": exp,
                   "ltd": qc.lastTradeDateOrContractMonth, "mult": qc.multiplier,
                   "last": t.last if t.last==t.last else None,
                   "close": t.close if t.close==t.close else None,
                   "bid": t.bid if t.bid==t.bid else None,
                   "ask": t.ask if t.ask==t.ask else None,
                   "mark": t.marketPrice() if t.marketPrice()==t.marketPrice() else None}
            out.append(row)
            ib.cancelMktData(qc)
        except Exception as e:
            out.append({"label": label, "error": str(e)[:100]})
    ib.disconnect()
    print(json.dumps(out, indent=2, default=str))

asyncio.run(main())
