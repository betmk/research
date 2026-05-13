"""Position-to-trade-thesis mapping.

Tags account positions with their probable trade-book thesis so the dashboard
shows "GOIL Sep ×2 — Trade #3 GO/Brent crack" instead of just "GOIL Sep ×2".

Tags are heuristic, anchored on the v1 trade-book from methodology.md:
- #3 ICE GO/Brent crack (long GOIL, short BZ/COIL Jul basis)
- #6 HOGO (long HO, short Gasoil; Dec back-end is the live expression)
- #10 Back-end Brent compression (long OCT26/DEC26, short JUL26)
- #14 ARA→PAD1 gasoline arb (long Eurobob, short RBOB)
"""
from __future__ import annotations


# Symbol → high-level thesis label. The dashboard shows this alongside
# the contract. Updated when the trade book changes structurally.
SYMBOL_THESIS: dict[str, str] = {
    "GOIL": "#3 GO/Brent crack — long leg (Crosby distillate)",
    "COIL": "#3 short leg (front) + #10 back-end Brent (Oct/Dec)",
    "BZ":   "NYMEX Brent — #3 short leg / #10 back-end",
    "CL":   "WTI outright — Ep 92 Goh TMX bid",
    "HO":   "#6 HOGO long leg — Dec back-end is live expression",
    "RB":   "#14 ARA→PAD1 gasoline arb — RBOB short leg",
    "NG":   "Nat gas — not in active trade book",
}


def tag_for_symbol(symbol: str, local_symbol: str | None = None) -> str:
    """Best-effort thesis tag for a position symbol. Empty string if unmapped."""
    if symbol in SYMBOL_THESIS:
        base = SYMBOL_THESIS[symbol]
        # Refine for back-end exposure: V (Oct), X (Nov), Z (Dec) month codes
        if local_symbol and symbol in ("COIL", "BZ"):
            month_code = local_symbol[-2] if len(local_symbol) >= 3 else ""
            if month_code in ("V", "X", "Z"):
                return f"{base} → back-end (Oct/Nov/Dec)"
            if month_code in ("N", "Q", "U"):
                return f"{base} → front (Jul/Aug/Sep)"
        return base
    return ""


def annotate_positions(positions: list[dict]) -> list[dict]:
    """Return positions with a `thesis` field added."""
    out = []
    for p in positions:
        p = dict(p)
        p["thesis"] = tag_for_symbol(p.get("symbol", ""), p.get("local_symbol"))
        out.append(p)
    return out
