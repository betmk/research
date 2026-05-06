"""IB symbology discovery — round 6. Last targeted permutation.
Murban single-letter, Naphtha alt, fuel oil alt, also browse what IBKR
shows on its public symbol-search via web is the next fallback."""
import asyncio, json
from pathlib import Path
from ib_async import IB, Future, ContFuture, util
util.patchAsyncio()

OUT = Path("/Users/mikemadden/Desktop/Claude Projects/research/.claude/worktrees/elegant-pasteur-58d995/tools/ib_results6.json")

# Murban — try really obscure variants
MURBAN = [
    (s, e) for s in ["AB","M","ABM","ABO","ABU","ADM","MBN","MUR","MURB","MURBAN"]
    for e in ["IFEU","IFAD","IFLX","IFAB","NYMEX","CME","ICEEUSOFT"]
]

# Naphtha alt names — Argus/Platts variants
NAPHTHA_2 = [
    (s, e) for s in ["NPH","NEX","NAJ","NHJ","NAR","NAP","NDP","NPL","NJF","JNA","JNP","NAPH","NWN"]
    for e in ["NYMEX","CME","IPE","IFEU","ICEEU","SGX"]
]

# CME Sing Fuel 0.5% — maybe under a different code
SING_FO = [
    (s, e) for s in ["SFB","BFO","BFB","S05","SO5","S5O","MO5","S5","FOC","FOG","FOJ","FOA","FOM"]
    for e in ["NYMEX","CME","SGX"]
]

ALL = MURBAN + NAPHTHA_2 + SING_FO

async def test(ib, sym, exch):
    for exp in ["202607","202606"]:
        c = Future(symbol=sym, lastTradeDateOrContractMonth=exp, exchange=exch, currency="USD")
        try:
            qd = await asyncio.wait_for(ib.reqContractDetailsAsync(c), timeout=2.5)
            if qd:
                r = qd[0]
                return {"tried": f"{sym}/{exch}/{exp}", "MATCH": True,
                        "longName": r.longName, "ltd": r.contract.lastTradeDateOrContractMonth,
                        "mult": r.contract.multiplier, "tradingClass": r.contract.tradingClass}
        except Exception:
            pass
    return None

async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=14, timeout=8)
    matches = []
    BATCH = 25
    for i in range(0, len(ALL), BATCH):
        batch = ALL[i:i+BATCH]
        results = await asyncio.gather(*[test(ib, s, e) for s, e in batch])
        matches.extend([r for r in results if r])
        OUT.write_text(json.dumps(matches, indent=2, default=str))
        print(f"Batch {i//BATCH + 1}: {len(matches)}", flush=True)
    ib.disconnect()
    print(json.dumps(matches, indent=2, default=str), flush=True)

asyncio.run(main())
