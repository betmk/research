"""Extract explicit trade ideas from Sparta podcast transcripts via Claude CLI.

For each Sparta episode with a transcript we don't yet have ideas for,
runs `claude -p` against the transcript with a structured-output prompt,
parses JSON, stores in trade_ideas table.

Runs serially (one Claude call at a time) — scheduler ticks fetch ~3
episodes per pass.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import shutil
from typing import Any

from ..db import episodes_needing_extraction, insert_trade_ideas, prior_episode_trade_ideas
from .base import BaseScraper

logger = logging.getLogger(__name__)

CLAUDE_CLI = shutil.which("claude") or "/opt/homebrew/bin/claude"
CLAUDE_TIMEOUT_SECONDS = 300

# Transcript chars per call — long enough to cover a 48-min episode (~50K)
MAX_TRANSCRIPT_CHARS = 60_000


_extract_lock = asyncio.Lock()


_PROMPT_TEMPLATE = """You are extracting explicit trade ideas from this Sparta Commodities podcast transcript.

For each trade call (a long/short call on a specific instrument or spread that listeners could act on), output a JSON object with these fields:

- "person": who said it (e.g. "Neil Crosby", "James Noel-Beswick", "June Goh", "Felipe Schuurman", "Jorge Molinero")
- "direction": one of "long", "short", "spread", "avoid", "exit", "watch"
- "instrument": the underlying or spread (e.g. "HOGO", "Long ICE Gasoil time spread Jun-Jul", "Short TC14 freight")
- "conviction": one of "high", "medium-high", "medium", "low". Scale:
    - "high"        = explicit "highest conviction" / "this is THE call"
    - "medium-high" = clear directional call with rationale + a few caveats
    - "medium"      = tilt or "cautiously bullish" / "I lean long"
    - "low"         = passing comment, vague, hedged
- "rationale": one concise sentence on why
- "quote": short verbatim quote from the transcript (under 25 words)
- "executable_on_ibkr": true if tradable via standard IB futures/options. false if Singapore-only product, physical OTC, or freight FFA.
- "ibkr_expression": SHORT phrase naming the IBKR contract/spread expression IF executable; otherwise one-phrase reason. Examples:
    - LONG HOGO → "Long HOQ6/HOU6 vs short GOILQ6/GOILU6 — see 'HOGO Q3' spread"
    - LONG ICE Gasoil M1-M2 → "Long GOILM6 vs short GOILN6 — see 'ICE Gasoil M1-M2' spread"
    - LONG WTI-Brent → "Long CLN6 vs short BZN6 — see 'Brent-WTI front' spread"
    - LONG RBOB cracks → "Long RBN6 vs short BZN6 — see 'RBOB/Brent crack' spread"
    - non-IBKR examples: "physical OTC diff" / "Singapore-only product" / "Freight FFA" / "OTC swap"
- "relation_to_prior": one of "new" | "reiterates" | "elevates" | "offsets" | "reverses" | "parks". Using the PRIOR EPISODES context below:
    - "new"         = trade not previously called
    - "reiterates"  = same instrument + same direction + similar conviction
    - "elevates"    = same direction + HIGHER conviction than prior
    - "offsets"     = same instrument, conviction REDUCED OR speaker walking back / adding caveats
    - "reverses"    = same instrument, opposite direction
    - "parks"       = was a live call, now AVOID/WATCH/exited
- "relation_to_prior_note": one-line description citing the prior episode number + speaker + what changed. Examples:
    - "Reiterates Ep 92 Crosby LONG HOGO with same conviction"
    - "Reverses Ep 91 Crosby LONG WTI-Brent — now parked"
    - "Offsets Ep 92 Crosby MED-HIGH LONG ICE Gasoil M1-M2 — Noel-Beswick now LOW, 'headline-driven'"
   If "new", set to null or empty string.

Rules:
- Only extract actual trade calls, not macro observations
- If the same trade is mentioned multiple times by the same person, output once
- Output ONLY a JSON array (starting with `[` and ending with `]`). No commentary, no markdown code fences. If none, output `[]`.

## PRIOR EPISODES — extracted ideas for context (for relation_to_prior tagging)

{prior_context}

## TRANSCRIPT (extract NEW ideas from THIS)
{transcript}
"""


def _format_prior_context(prior_ideas: list[dict]) -> str:
    if not prior_ideas:
        return "(No prior episodes extracted yet — every new idea = 'new'.)"
    lines: list[str] = []
    current_ep: int | None = None
    for p in prior_ideas:
        ep = p.get("episode_number")
        if ep != current_ep:
            lines.append(f"\nEp {ep}:")
            current_ep = ep
        conv = (p.get("conviction") or "?").upper()
        direction = (p.get("direction") or "?").upper()
        lines.append(
            f"- [{conv}] {direction} {p.get('instrument','?')} "
            f"({p.get('person','?')})"
        )
    return "\n".join(lines)


def _strip_code_fences(s: str) -> str:
    """Some Claude outputs wrap JSON in ```json ... ``` fences. Strip them."""
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```\w*\s*\n", "", s)
        s = re.sub(r"\n```\s*$", "", s)
    return s.strip()


async def _extract_via_claude(transcript: str, prior_ideas: list[dict]) -> list[dict]:
    """Run Claude CLI, parse JSON, return list of trade dicts."""
    prompt = _PROMPT_TEMPLATE.format(
        transcript=transcript[:MAX_TRANSCRIPT_CHARS],
        prior_context=_format_prior_context(prior_ideas),
    )
    proc = await asyncio.create_subprocess_exec(
        CLAUDE_CLI, "-p", prompt, "--output-format", "text",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=CLAUDE_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:  # noqa: BLE001
            pass
        logger.warning("claude CLI timeout extracting trades")
        return []

    if proc.returncode != 0:
        logger.warning("claude CLI returncode %s extracting trades; stderr=%s",
                        proc.returncode, stderr.decode()[:200])
        return []

    output = _strip_code_fences(stdout.decode())
    if not output:
        return []
    try:
        data = json.loads(output)
        if isinstance(data, list):
            return data
        logger.warning("expected JSON array, got %s", type(data).__name__)
        return []
    except json.JSONDecodeError as exc:
        # Try to salvage by finding the first [ and last ]
        a = output.find("[")
        b = output.rfind("]")
        if 0 <= a < b:
            try:
                return json.loads(output[a:b+1])
            except json.JSONDecodeError:
                pass
        logger.warning("JSON parse failed: %s; head=%s", exc, output[:200])
        return []


class SpartaTradeExtractor(BaseScraper):
    name = "sparta_extract"
    episodes_per_run = 3

    async def fetch(self) -> dict[str, Any]:
        async with _extract_lock:
            episodes = episodes_needing_extraction(limit=self.episodes_per_run)
            if not episodes:
                return {"items_found": 0, "items_new": 0,
                        "skipped": "no episodes pending extraction"}

            total_ideas = 0
            for ep in episodes:
                try:
                    # Pull prior 2 episodes' ideas as context for reversal detection
                    prior = prior_episode_trade_ideas(
                        before_episode=ep["number"], lookback=2,
                    )
                    ideas = await _extract_via_claude(ep["transcript"], prior)
                    n = insert_trade_ideas(
                        episode_id=ep["id"],
                        episode_number=ep["number"],
                        episode_title=ep["title"],
                        episode_published_at=ep["published_at"],
                        trades=ideas,
                        model="claude-cli",
                    )
                    total_ideas += n
                    logger.info("Ep %s: extracted %d trade ideas",
                                 ep["number"], n)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("extract failed for Ep %s: %s",
                                    ep["number"], exc)

            return {
                "items_found": len(episodes),
                "items_new": total_ideas,
            }
