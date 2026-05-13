"""Sparta podcast transcript enrichment via YouTube auto-captions.

Per memory: transcripts are accessible on YouTube channel @SpartaCommo
(playlist PLI3dsnod9Rdj7KEMrCvibuZGxwFCw43Jv). Uses yt-dlp to pull
auto-generated captions for each episode and parse them into plain text.

Saves to episodes.transcript so synthesis can use the full content.
"""
from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..db import episodes_without_transcripts, set_episode_transcript
from .base import BaseScraper

YT_CHANNEL_HANDLE = "@SpartaCommo"
YT_PLAYLIST_ID = "PLI3dsnod9Rdj7KEMrCvibuZGxwFCw43Jv"
YT_DLP = shutil.which("yt-dlp") or "/Users/mikemadden/Desktop/Claude Projects/research/.venv/bin/yt-dlp"
EP_NUMBER_RE = re.compile(r"Episode\s+(\d+)", re.IGNORECASE)
MAX_TRANSCRIPT_CHARS = 30_000  # keep token budget bounded


async def _list_playlist_videos() -> list[dict]:
    """Use yt-dlp --flat-playlist to enumerate videos. Returns
    [{title, video_id, url}]."""
    proc = await asyncio.create_subprocess_exec(
        YT_DLP, "--flat-playlist", "-J",
        f"https://www.youtube.com/playlist?list={YT_PLAYLIST_ID}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
    data = json.loads(stdout.decode())
    out = []
    for entry in data.get("entries", []):
        out.append({
            "title": entry.get("title", ""),
            "video_id": entry.get("id"),
            "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
        })
    return out


def _parse_episode_number(title: str) -> int | None:
    m = EP_NUMBER_RE.search(title)
    return int(m.group(1)) if m else None


async def _fetch_captions(video_id: str) -> str | None:
    """Download English auto-captions for a video and return cleaned text."""
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "captions"
        proc = await asyncio.create_subprocess_exec(
            YT_DLP, "--skip-download",
            "--write-auto-subs", "--sub-lang", "en", "--sub-format", "vtt",
            "-o", str(out_path),
            f"https://www.youtube.com/watch?v={video_id}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            await asyncio.wait_for(proc.communicate(), timeout=120)
        except asyncio.TimeoutError:
            proc.kill()
            return None

        # Find the .vtt file
        vtt_files = list(Path(tmp).glob("*.vtt"))
        if not vtt_files:
            return None

        raw = vtt_files[0].read_text(errors="ignore")
        # Strip VTT headers, timestamps, blank lines
        text_lines: list[str] = []
        seen: set[str] = set()
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            if line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
                continue
            if "-->" in line:
                continue
            # Remove inline VTT tags <c.colorXXX>...</c>
            clean = re.sub(r"<[^>]+>", "", line)
            clean = re.sub(r"\s+", " ", clean).strip()
            if clean and clean not in seen:
                seen.add(clean)
                text_lines.append(clean)

        text = " ".join(text_lines)
        return text[:MAX_TRANSCRIPT_CHARS] if text else None


class SpartaTranscripts(BaseScraper):
    name = "sparta_transcripts"

    async def fetch(self) -> dict[str, Any]:
        if not shutil.which(YT_DLP):
            return {"items_found": 0, "items_new": 0,
                    "skipped": "yt-dlp not on PATH"}

        try:
            videos = await _list_playlist_videos()
        except Exception as exc:  # noqa: BLE001
            return {"items_found": 0, "items_new": 0,
                    "skipped": f"playlist enum failed: {exc}"}

        # Build map of episode_number -> video_id
        ep_to_video: dict[int, str] = {}
        for v in videos:
            num = _parse_episode_number(v["title"])
            if num:
                ep_to_video[num] = v["video_id"]

        # Find episodes in DB that don't have transcripts yet
        episodes = episodes_without_transcripts(limit=5)
        new_count = 0
        for ep in episodes:
            num = ep.get("number")
            if not num or num not in ep_to_video:
                continue
            text = await _fetch_captions(ep_to_video[num])
            if text:
                set_episode_transcript(ep["id"], text)
                new_count += 1

        return {
            "items_found": len(episodes),
            "items_new": new_count,
            "videos_indexed": len(ep_to_video),
        }
