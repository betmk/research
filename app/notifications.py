"""macOS notification helpers."""
from __future__ import annotations

import asyncio
import shutil


async def notify(title: str, message: str, sound: str = "Sosumi") -> None:
    """Fire a macOS notification. Silently no-op on non-mac."""
    if not shutil.which("osascript"):
        return
    safe_title = title.replace('"', "'")
    safe_message = message.replace('"', "'")
    cmd = [
        "osascript",
        "-e",
        f'display notification "{safe_message}" with title "{safe_title}" sound name "{sound}"',
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()


def notify_sync(title: str, message: str, sound: str = "Sosumi") -> None:
    """Synchronous variant for non-async callers (cron, scripts)."""
    import subprocess
    if not shutil.which("osascript"):
        return
    safe_title = title.replace('"', "'")
    safe_message = message.replace('"', "'")
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{safe_message}" with title "{safe_title}" sound name "{sound}"',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
