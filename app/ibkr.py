"""IBKR Gateway integration — singleton connection + contract registry.

Connection is established lazily on first use, reused across scraper runs.
Pulls live quotes when subscribed, falls back to delayed (free) otherwise.

Gateway must be running on 127.0.0.1:4001 (live) or 4002 (paper) with
"Enable ActiveX and Socket Clients" checked in Global Configuration → API.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from ib_async import IB, Contract, Future, Option, Stock

logger = logging.getLogger(__name__)

# Connection params — pinned to live Gateway. Switch to 4002 for paper.
IBKR_HOST = "127.0.0.1"
IBKR_PORT = 4001
IBKR_CLIENT_ID = 17        # avoids conflict with investing-dash (1, 2)
IBKR_TIMEOUT = 10

# Market data type:
#   1 = live (requires subscription)
#   2 = frozen (last known)
#   3 = delayed (free, ~15-20 min lag)
#   4 = delayed frozen
# We set to 1 and IB auto-falls-back to 3 if not subscribed.
MARKET_DATA_TYPE = 1

# === Contract registry — internal label -> IB Contract spec ===
# All resolved against live Gateway. Update lastTradeDateOrContractMonth
# for monthly rolls (Brent rolls into JUL26 after JUN26 expiry, etc.).
WATCHLIST: dict[str, Contract] = {
    "BRENT_JUL26": Future(symbol="BZ", lastTradeDateOrContractMonth="202607",
                          exchange="NYMEX", currency="USD"),
    "BRENT_AUG26": Future(symbol="BZ", lastTradeDateOrContractMonth="202608",
                          exchange="NYMEX", currency="USD"),
    "BRENT_SEP26": Future(symbol="BZ", lastTradeDateOrContractMonth="202609",
                          exchange="NYMEX", currency="USD"),
    "BRENT_OCT26": Future(symbol="BZ", lastTradeDateOrContractMonth="202610",
                          exchange="NYMEX", currency="USD"),
    "BRENT_DEC26": Future(symbol="BZ", lastTradeDateOrContractMonth="202612",
                          exchange="NYMEX", currency="USD"),
    "WTI_JUL26": Future(symbol="CL", lastTradeDateOrContractMonth="202607",
                        exchange="NYMEX", currency="USD"),
    "WTI_AUG26": Future(symbol="CL", lastTradeDateOrContractMonth="202608",
                        exchange="NYMEX", currency="USD"),
    "WTI_DEC26": Future(symbol="CL", lastTradeDateOrContractMonth="202612",
                        exchange="NYMEX", currency="USD"),
    # ICE Brent (COIL on IPE) — the user holds COIL Q6/U6/V6 outright
    "ICE_BRENT_JUL26": Future(symbol="COIL", lastTradeDateOrContractMonth="202607",
                              exchange="IPE", currency="USD"),
    "ICE_BRENT_AUG26": Future(symbol="COIL", lastTradeDateOrContractMonth="202608",
                              exchange="IPE", currency="USD"),
    "ICE_BRENT_SEP26": Future(symbol="COIL", lastTradeDateOrContractMonth="202609",
                              exchange="IPE", currency="USD"),
    "ICE_BRENT_OCT26": Future(symbol="COIL", lastTradeDateOrContractMonth="202610",
                              exchange="IPE", currency="USD"),
    "ICE_BRENT_DEC26": Future(symbol="COIL", lastTradeDateOrContractMonth="202612",
                              exchange="IPE", currency="USD"),
    "ICE_GASOIL_JUN26": Future(symbol="GOIL", lastTradeDateOrContractMonth="202606",
                               exchange="IPE", currency="USD"),
    "ICE_GASOIL_JUL26": Future(symbol="GOIL", lastTradeDateOrContractMonth="202607",
                               exchange="IPE", currency="USD"),
    "ICE_GASOIL_AUG26": Future(symbol="GOIL", lastTradeDateOrContractMonth="202608",
                               exchange="IPE", currency="USD"),
    "NYMEX_HO_JUN26": Future(symbol="HO", lastTradeDateOrContractMonth="202606",
                             exchange="NYMEX", currency="USD"),
    "NYMEX_HO_JUL26": Future(symbol="HO", lastTradeDateOrContractMonth="202607",
                             exchange="NYMEX", currency="USD"),
    "NYMEX_HO_AUG26": Future(symbol="HO", lastTradeDateOrContractMonth="202608",
                             exchange="NYMEX", currency="USD"),
    "NYMEX_HO_SEP26": Future(symbol="HO", lastTradeDateOrContractMonth="202609",
                             exchange="NYMEX", currency="USD"),
    "NYMEX_HO_OCT26": Future(symbol="HO", lastTradeDateOrContractMonth="202610",
                             exchange="NYMEX", currency="USD"),
    "NYMEX_HO_DEC26": Future(symbol="HO", lastTradeDateOrContractMonth="202612",
                             exchange="NYMEX", currency="USD"),
    "RBOB_JUL26": Future(symbol="RB", lastTradeDateOrContractMonth="202607",
                         exchange="NYMEX", currency="USD"),
    "NATGAS_JUL26": Future(symbol="NG", lastTradeDateOrContractMonth="202607",
                           exchange="NYMEX", currency="USD"),
}


# === Connection management ===

_ib: Optional[IB] = None
_connect_lock = asyncio.Lock()


async def get_ib() -> IB:
    """Return a live IB connection. Reconnects if dropped."""
    global _ib
    async with _connect_lock:
        if _ib is not None and _ib.isConnected():
            return _ib
        ib = IB()
        await ib.connectAsync(IBKR_HOST, IBKR_PORT,
                               clientId=IBKR_CLIENT_ID, timeout=IBKR_TIMEOUT)
        ib.reqMarketDataType(MARKET_DATA_TYPE)
        _ib = ib
        accts = ib.managedAccounts()
        logger.info("IBKR connected: account=%s clientId=%s", accts, IBKR_CLIENT_ID)
        return ib


def disconnect() -> None:
    global _ib
    if _ib is not None:
        try:
            _ib.disconnect()
        except Exception:  # noqa: BLE001
            pass
        _ib = None


async def qualify_contracts(contracts: list[Contract]) -> list[Contract]:
    """Resolve abstract contract specs into concrete contracts with conIds."""
    ib = await get_ib()
    qualified = await ib.qualifyContractsAsync(*contracts)
    return list(qualified)


async def snapshot_quotes(labels: list[str] | None = None,
                          wait_seconds: float = 4.0) -> dict[str, dict]:
    """Pull a snapshot quote for each requested watchlist instrument.

    Returns dict keyed by label with {bid, ask, last, close, change_pct,
    fetched_at, source}. Missing/nan fields are None.
    """
    from datetime import datetime

    ib = await get_ib()
    if labels is None:
        labels = list(WATCHLIST.keys())

    # Resolve contracts
    raw_contracts = [WATCHLIST[label] for label in labels]
    qualified = await ib.qualifyContractsAsync(*raw_contracts)
    pairs: list[tuple[str, Contract]] = []
    qualified_idx = 0
    for label, raw in zip(labels, raw_contracts):
        # qualifyContractsAsync returns same order as input; some may be None
        # if unresolvable. ib_async raises on full failure, so guard anyway.
        if qualified_idx < len(qualified) and qualified[qualified_idx] is not None:
            pairs.append((label, qualified[qualified_idx]))
        qualified_idx += 1

    # Subscribe (streaming, not snapshot — snapshot mode is unreliable for
    # some IB instruments; streaming for ~4 sec gets last+close+bid+ask).
    tickers = [(label, c, ib.reqMktData(c, "", False, False)) for label, c in pairs]
    await asyncio.sleep(wait_seconds)

    out: dict[str, dict] = {}
    for label, contract, t in tickers:
        def _nan_to_none(v):
            return v if (v is not None and v == v) else None  # nan check
        last = _nan_to_none(t.last)
        close = _nan_to_none(t.close)
        bid = _nan_to_none(t.bid)
        ask = _nan_to_none(t.ask)
        change_pct = None
        if last and close:
            change_pct = round((last - close) / close * 100, 3)
        out[label] = {
            "instrument": label,
            "contract": contract.localSymbol,
            "con_id": contract.conId,
            "price": last or close,        # prefer last; fall back to close
            "change": (last - close) if (last and close) else None,
            "change_pct": change_pct,
            "prev_close": close,
            "bid": bid,
            "ask": ask,
            "source": "ibkr",
            "fetched_at": datetime.utcnow(),
        }
        ib.cancelMktData(contract)
    return out


async def get_positions(sec_types: tuple[str, ...] = ("FUT", "OPT", "STK")) -> list[dict]:
    """Return all positions, optionally filtered by sec type.

    Each entry: {symbol, local_symbol, sec_type, exchange, position, avg_cost,
                 unrealized_pnl, market_price, market_value, account}.
    """
    ib = await get_ib()
    positions = ib.positions()
    portfolio = {p.contract.conId: p for p in ib.portfolio()}

    out: list[dict] = []
    for p in positions:
        if p.contract.secType not in sec_types:
            continue
        port = portfolio.get(p.contract.conId)
        out.append({
            "symbol": p.contract.symbol,
            "local_symbol": p.contract.localSymbol,
            "sec_type": p.contract.secType,
            "exchange": p.contract.exchange or p.contract.primaryExchange or "",
            "currency": p.contract.currency,
            "position": float(p.position),
            "avg_cost": float(p.avgCost),
            "market_price": float(port.marketPrice) if port and port.marketPrice == port.marketPrice else None,
            "market_value": float(port.marketValue) if port and port.marketValue == port.marketValue else None,
            "unrealized_pnl": float(port.unrealizedPNL) if port and port.unrealizedPNL == port.unrealizedPNL else None,
            "account": p.account,
        })
    return out


async def get_account_summary() -> dict:
    """Net liquidation, buying power, P&L summary."""
    ib = await get_ib()
    summary = ib.accountSummary()
    out = {}
    for row in summary:
        if row.tag in ("NetLiquidation", "TotalCashValue", "BuyingPower",
                        "GrossPositionValue", "UnrealizedPnL", "RealizedPnL",
                        "AvailableFunds", "ExcessLiquidity"):
            out[row.tag] = {"value": row.value, "currency": row.currency}
    return out
