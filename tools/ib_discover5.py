"""IB symbology discovery — round 5. Permutation matrix for the gaps."""
import asyncio, json
from pathlib import Path
from ib_async import IB, Future, ContFuture, util
util.patchAsyncio()

OUT = Path("/Users/mikemadden/Desktop/Claude Projects/research/.claude/worktrees/elegant-pasteur-58d995/tools/ib_results5.json")

# Murban — every plausible permutation
MURBAN = [
    ("ADM","IFEU"), ("ADM","IFAD"), ("ADM","ICEEU"), ("ADM","ICEEUSOFT"),
    ("ABO","IFAD"), ("ABO","IFEU"), ("ABO","ICEEU"),
    ("ADO","IFEU"), ("ADO","IFAD"),
    ("ABM","IFEU"), ("ABM","IFAD"),
    ("MUR","IFEU"), ("MUR","IFAD"), ("MUR","ICEEU"), ("MUR","ICEEUSOFT"),
    ("MURBAN","IFEU"), ("MURBAN","IFAD"),
    ("MURB","IFEU"), ("MURB","IFAD"),
]

# Sing Marine Fuel 0.5% — broad permutation
MARINE_FUEL = [
    (s, e) for s in ["MFB","MOL","S05","MFP","MF0","MFQ","M05","SMF"]
    for e in ["NYMEX","CME","GLOBEX","CMEN","SGX","ICEEU"]
]

# Sing Jet Kerosene (Platts) — JKB / AKB family
SING_JET = [
    (s, e) for s in ["AKB","JKB","SJK","SJB","SJP","JKM","JKE","SKO"]
    for e in ["NYMEX","CME","GLOBEX","CMEN","SGX"]
]

# Sing Jet Regrade — RKA family
SING_REGRADE = [
    (s, e) for s in ["RKA","JKR","JRG","SRG","RKB","JKR"]
    for e in ["NYMEX","CME","GLOBEX","CMEN"]
]

# Sing Gasoil 0.05% (Platts) — SGB family
SING_GASOIL = [
    (s, e) for s in ["SGB","S5G","SG5","SGP","GBP","SGD"]
    for e in ["NYMEX","CME","GLOBEX","CMEN","SGX"]
]

# Naphtha NWE / Asia — DKE / DKF / NDE / MAJ / MOJ family
NAPHTHA = [
    (s, e) for s in ["DKE","DKF","NDE","NPN","NPP","MAJ","MOJ","NSP",
                      "NWE","NPF","NPC","MN","NMW","JN","NJF"]
    for e in ["NYMEX","CME","GLOBEX","IPE","ICEEU","IFEU"]
]

# Fuel oil — HSFO 380 / 180, LSFO 1.0%, etc.
FUEL_OIL = [
    (s, e) for s in ["HZ","FUS","HSF","LSF","HFO","FOM","UV","UA",
                      "WFO","RIK","S0F","SO5","HFG","HFA","RKA"]
    for e in ["NYMEX","CME","GLOBEX","SGX","CMEN"]
]

# Diesel / ULSD US Gulf
DIESEL_US = [
    (s, e) for s in ["LT","HOG","ULSD","DIESEL","ULGC"]
    for e in ["NYMEX","CME"]
]

ALL_TESTS = MURBAN + MARINE_FUEL + SING_JET + SING_REGRADE + SING_GASOIL + NAPHTHA + FUEL_OIL + DIESEL_US

async def test_one(ib, sym, exch, exp="202607"):
    c = Future(symbol=sym, lastTradeDateOrContractMonth=exp, exchange=exch, currency="USD")
    try:
        qd = await asyncio.wait_for(ib.reqContractDetailsAsync(c), timeout=3)
        if qd:
            r = qd[0]
            return {"tried": f"{sym}/{exch}", "MATCH": True,
                    "longName": r.longName, "ltd": r.contract.lastTradeDateOrContractMonth,
                    "mult": r.contract.multiplier, "tradingClass": r.contract.tradingClass,
                    "primaryExch": r.contract.primaryExchange,
                    "currency": r.contract.currency}
    except Exception:
        pass
    # Also try ContFuture as fallback (no expiry needed)
    cf = ContFuture(symbol=sym, exchange=exch, currency="USD")
    try:
        qd = await asyncio.wait_for(ib.reqContractDetailsAsync(cf), timeout=3)
        if qd:
            r = qd[0]
            return {"tried": f"{sym}/{exch} [ContFuture]", "MATCH": True,
                    "longName": r.longName, "tradingClass": r.contract.tradingClass,
                    "primaryExch": r.contract.primaryExchange,
                    "currency": r.contract.currency}
    except Exception:
        pass
    return None


async def main():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 4001, clientId=13, timeout=8)
    # Run in batches of 30 to avoid swamping the API
    matches = []
    BATCH = 30
    for i in range(0, len(ALL_TESTS), BATCH):
        batch = ALL_TESTS[i:i+BATCH]
        tasks = [test_one(ib, s, e) for s, e in batch]
        results = await asyncio.gather(*tasks)
        matches.extend([r for r in results if r])
        OUT.write_text(json.dumps(matches, indent=2, default=str))
        print(f"Batch {i//BATCH + 1}/{(len(ALL_TESTS)+BATCH-1)//BATCH}: {len(matches)} matches so far", flush=True)

    ib.disconnect()
    print(f"\nFINAL: {len(matches)} contracts found", flush=True)
    print(json.dumps(matches, indent=2, default=str), flush=True)

asyncio.run(main())
