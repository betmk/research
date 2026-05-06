"""IB historical data — works without live mkt-data subscription on
many contracts. Pulls last N days of daily bars for COIL (ICE Brent)
and GOIL (ICE Gasoil), where live mkt-data was null.
"""
import asyncio, json
from ib_async import IB, Future, util
util.patchAsyncio()

CONTRACTS = [
    ("COIL","IPE","USD","202607","ICE Brent JUL26"),
    ("COIL","IPE","USD","202608","ICE Brent AUG26"),
    ("COIL","IPE","USD","202610","ICE Brent OCT26"),
    ("COIL","IPE","USD","202612","ICE Brent DEC26"),
    ("COIL","IPE","USD","202706","ICE Brent JUN27"),
    ("COIL","IPE","USD","202712","ICE Brent DEC27"),
    ("GOIL","IPE","USD","202605","ICE Gasoil MAY26"),
    ("GOIL","IPE","USD","202606","ICE Gasoil JUN26"),
    ("GOIL","IPE","USD","202607","ICE Gasoil JUL26"),
    ("GOIL","IPE","USD","202608","ICE Gasoil AUG26"),
    ("GOIL","IPE","USD","202609","ICE Gasoil SEP26"),
]

async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=16, timeout=8)
    out = []
    for sym,exch,cur,exp,label in CONTRACTS:
        c = Future(symbol=sym, lastTradeDateOrContractMonth=exp,
                   exchange=exch, currency=cur)
        try:
            qd = await ib.qualifyContractsAsync(c)
            if not qd:
                out.append({"label": label, "status": "not qualified"}); continue
            qc = qd[0]
            bars = await ib.reqHistoricalDataAsync(
                qc,
                endDateTime="",
                durationStr="5 D",
                barSizeSetting="1 day",
                whatToShow="TRADES",
                useRTH=False,
                formatDate=1,
                keepUpToDate=False,
            )
            if bars:
                last_bar = bars[-1]
                out.append({"label": label, "sym": sym, "expiry": exp,
                            "last_date": str(last_bar.date),
                            "close": last_bar.close, "open": last_bar.open,
                            "high": last_bar.high, "low": last_bar.low,
                            "n_bars": len(bars)})
            else:
                out.append({"label": label, "status": "no bars"})
        except Exception as e:
            out.append({"label": label, "error": str(e)[:100]})
    ib.disconnect()
    print(json.dumps(out, indent=2, default=str))

asyncio.run(main())
