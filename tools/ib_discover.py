"""Discover IB symbology for the contracts we need by searching.

Brent, ICE Gasoil, Sing MF0.5%, Sing Jet Regrade, Murban — these all
need the right IB symbol/exchange combo. Use reqMatchingSymbols + 
reqContractDetailsAsync to find them.
"""
import asyncio, json
from ib_async import IB, util, Future, Contract
util.patchAsyncio()

async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=8, timeout=8)
    out = {}

    # Try various search strings — IB matching symbols
    searches = ["BRENT", "BRN", "BZ", "COIL", "GASOIL", "LSGO", "GAS",
                "MARINE FUEL", "SINGAPORE", "REGRADE", "MURBAN"]
    for s in searches:
        try:
            res = await ib.reqMatchingSymbolsAsync(s)
            out[s] = [{"sym": r.contract.symbol, "exch": r.contract.exchange,
                       "secType": r.contract.secType, "primary": r.contract.primaryExchange,
                       "cur": r.contract.currency, "desc": r.contract.description if hasattr(r.contract,'description') else None}
                      for r in res[:8]]
        except Exception as e:
            out[s] = {"error": str(e)[:120]}

    # Also try direct contract details on the most likely BRN combos
    direct_tests = [
        Future(symbol="BZ",  lastTradeDateOrContractMonth="202607", exchange="NYMEX", currency="USD"),
        Future(symbol="QM",  lastTradeDateOrContractMonth="202607", exchange="NYMEX", currency="USD"),
        Future(symbol="BRN", lastTradeDateOrContractMonth="202607", exchange="NYBOT", currency="USD"),
        Future(symbol="BRN", lastTradeDateOrContractMonth="202607", exchange="ICEEU", currency="USD"),
        Future(symbol="BRN", lastTradeDateOrContractMonth="202607", exchange="ICEEUSOFT", currency="USD"),
        Future(symbol="GAS", lastTradeDateOrContractMonth="202606", exchange="ICEEU", currency="USD"),
        Future(symbol="GAS", lastTradeDateOrContractMonth="202606", exchange="NYBOT", currency="USD"),
        Future(symbol="GAS", lastTradeDateOrContractMonth="202606", exchange="IPE", currency="USD"),
        Future(symbol="MUR", lastTradeDateOrContractMonth="202607", exchange="ICEEU", currency="USD"),
        Future(symbol="MUR", lastTradeDateOrContractMonth="202607", exchange="NYBOT", currency="USD"),
    ]
    out["direct_tests"] = []
    for c in direct_tests:
        try:
            d = await ib.reqContractDetailsAsync(c)
            out["direct_tests"].append({
                "tried": f"{c.symbol}/{c.exchange}/{c.lastTradeDateOrContractMonth}",
                "found": [{"sym": x.contract.symbol, "exch": x.contract.exchange,
                           "ltd": x.contract.lastTradeDateOrContractMonth,
                           "longName": x.longName} for x in d[:3]]
            })
        except Exception as e:
            out["direct_tests"].append({"tried": f"{c.symbol}/{c.exchange}", "error": str(e)[:80]})

    ib.disconnect()
    print(json.dumps(out, indent=2, default=str))

asyncio.run(main())
