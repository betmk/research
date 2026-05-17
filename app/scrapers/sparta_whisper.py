"""Sparta podcast transcription via local faster-whisper.

Replaces the YouTube-auto-caption flow with direct MP3 → text using
faster-whisper. Episodes get transcribed within ~2-3 minutes of being
released (vs. waiting hours for the YouTube upload + auto-caption).

Model: base.en — best speed/quality balance for English business podcasts
on Apple Silicon CPU (int8). ~16x realtime, ~75MB model.

Runs serially via shared lock so we don't load the model twice in parallel.
"""
from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import time
from typing import Any

import httpx

from ..db import episodes_without_transcripts, set_episode_transcript
from .base import BaseScraper

logger = logging.getLogger(__name__)

WHISPER_MODEL = "base.en"        # tiny.en / base.en / small.en / medium.en
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE = "int8"
MAX_TRANSCRIPT_CHARS = 80_000     # raised from 30K (full ~48min ep is ~50K)

# Serialize loading + transcription across scraper instances
_whisper_lock = asyncio.Lock()
_model = None


def _load_model():
    """Lazy-load the Whisper model. Cached for process lifetime."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        logger.info("loading faster-whisper %s (%s/%s)",
                     WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE)
        _model = WhisperModel(
            WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE,
        )
    return _model


async def _download_mp3(url: str, dest: str) -> int:
    """Stream MP3 to dest. Returns bytes written."""
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            total = 0
            with open(dest, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=65536):
                    f.write(chunk)
                    total += len(chunk)
            return total


def _transcribe(mp3_path: str) -> str:
    """Synchronous transcription. Called via asyncio.to_thread."""
    model = _load_model()
    segments, _info = model.transcribe(mp3_path, beam_size=5, vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments)
    return text[:MAX_TRANSCRIPT_CHARS]


class SpartaWhisper(BaseScraper):
    """Transcribes Sparta podcast episodes via local Whisper. Pulls up to
    `episodes_per_run` from episodes without a transcript yet."""

    name = "sparta_whisper"
    episodes_per_run = 3

    async def fetch(self) -> dict[str, Any]:
        async with _whisper_lock:
            # Primary: episodes with no transcript at all
            episodes = episodes_without_transcripts(limit=self.episodes_per_run)
            episodes = [e for e in episodes if e.get("audio_url")]

            # Secondary: also upgrade non-Whisper transcripts on recent eps
            # (YouTube auto-captions are noisier and truncated at 30K chars;
            # Whisper produces ~50K cleaner chars for a 48-min episode).
            if len(episodes) < self.episodes_per_run:
                from ..db import get_conn
                slots = self.episodes_per_run - len(episodes)
                seen_ids = {e["id"] for e in episodes}
                with get_conn() as conn:
                    rows = conn.execute(
                        """
                        SELECT id, series, number, title, url, audio_url, duration_seconds
                        FROM episodes
                        WHERE audio_url IS NOT NULL
                          AND (transcript_source IS NULL
                               OR transcript_source NOT LIKE 'whisper%')
                        ORDER BY COALESCE(published_at, fetched_at) DESC
                        LIMIT ?
                        """,
                        [slots * 3],
                    ).fetchall()
                    for r in rows:
                        if r[0] in seen_ids or len(episodes) >= self.episodes_per_run:
                            continue
                        episodes.append({"id": r[0], "series": r[1], "number": r[2],
                                          "title": r[3], "url": r[4],
                                          "audio_url": r[5], "duration_seconds": r[6]})

            if not episodes:
                return {"items_found": 0, "items_new": 0,
                        "skipped": "no episodes with audio_url awaiting transcript"}

            items_new = 0
            errors: list[str] = []

            for ep in episodes:
                try:
                    started = time.time()
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                        mp3_path = tmp.name

                    try:
                        size = await _download_mp3(ep["audio_url"], mp3_path)
                        download_time = time.time() - started

                        # Transcription is CPU-bound — run in a thread so we
                        # don't block the event loop / FastAPI
                        text = await asyncio.to_thread(_transcribe, mp3_path)
                        total_time = time.time() - started

                        if not text or len(text) < 500:
                            errors.append(f"Ep {ep.get('number')}: transcript too short")
                            continue

                        set_episode_transcript(ep["id"], text, source="whisper-base.en")
                        items_new += 1
                        logger.info(
                            "transcribed Ep %s: %d chars in %.1fs "
                            "(download %.1fs, %dMB audio)",
                            ep.get("number"), len(text), total_time,
                            download_time, size // 1024 // 1024,
                        )
                    finally:
                        try:
                            os.unlink(mp3_path)
                        except OSError:
                            pass
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"Ep {ep.get('number')}: {type(exc).__name__}: {exc}")

            result: dict[str, Any] = {
                "items_found": len(episodes),
                "items_new": items_new,
                "model": f"whisper-{WHISPER_MODEL}",
            }
            if errors:
                result["errors"] = errors[:5]
            return result
