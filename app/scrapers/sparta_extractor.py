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
- "instrument": the underlying or spread (e.g. "HOGO", "Long ICE Gasoil time spread Jun-Jul", "Short TC14 freight", "Long Brent Murban physical diff", "Long Singapore Regrade")
- "conviction": one of "high", "medium-high", "medium", "low". Use this scale:
    - "high"        = explicit "highest conviction" / "this is THE call" / "strong long"
    - "medium-high" = clear directional call with rationale + a few caveats
    - "medium"      = tilt or "cautiously bullish" / "I lean long"
    - "low"         = passing comment, vague, or hedged with "but I don't have high conviction"
- "rationale": one concise sentence on why
- "quote": short verbatim quote from the transcript (under 25 words)
- "executable_on_ibkr": true if tradable via standard IB futures/options (NYMEX, ICE, CME). false if it's a Singapore-only product (Sing Gasoil swap, Sing LSFO, Sing Jet, Sing Regrade), a physical OTC differential, or freight (TC2/TC14/TD).
- "ibkr_expression": A SHORT phrase naming the specific IBKR-tradable contract pair or spread that expresses this idea, IF executable. Examples:
    - LONG HOGO → "Long HOQ6/HOU6 vs short GOILQ6/GOILU6 — see 'HOGO Q3' spread"
    - LONG ICE Gasoil M1-M2 → "Long GOILM6 vs short GOILN6 — see 'ICE Gasoil M1-M2' spread"
    - LONG WTI-Brent → "Long CLN6 vs short BZN6 — see 'Brent-WTI front' spread"
    - LONG RBOB cracks → "Long RBN6 vs short BZN6 — see 'RBOB/Brent crack' spread"
    - LONG Brent flat price → "Long BZN6 outright (or COILN6 for ICE basis)"
   If NOT executable on IBKR, instead give a one-phrase REASON (e.g. "physical OTC diff", "Singapore-only product", "freight FFA", "OTC swap").

Rules:
- Only extract actual trade calls, not macro observations
- Skip "I don't want to call that" or "I'd avoid this"-style non-calls UNLESS the host explicitly says "avoid" as a recommendation
- If the same trade is mentioned multiple times by the same person, output once
- If the call is from a guest or external source they cite, attribute to the host who endorses it
- Output ONLY a JSON array (starting with `[` and ending with `]`). No commentary, no markdown code fences, no preamble. If no trade ideas exist, output `[]`.

TRANSCRIPT:
{transcript}
"""


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
