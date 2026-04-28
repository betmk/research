#!/usr/bin/env python3
"""Generate research-dashboard.icns from an emoji and apply it to launcher files.

Uses PyObjC (bundled with macOS Python) to render the emoji at native quality,
sips to resize, iconutil to package, NSWorkspace to apply.

Re-run any time the launcher is reinstalled (icons live in extended attributes
that don't survive git or cp).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

EMOJI = "📊"
HERE = Path(__file__).parent.resolve()
ICONSET = Path("/tmp/research-dashboard.iconset")
MASTER_PNG = Path("/tmp/research-dashboard-master.png")
ICNS = HERE / "research-dashboard.icns"

TARGET_FILES = [
    HERE / "research-dashboard.command",
    Path.home() / "Desktop" / "📊 Research Dashboard.command",
]


def render_emoji_png(emoji: str, out: Path, size: int = 1024) -> None:
    """Render emoji at full size using AppKit's NSAttributedString."""
    from AppKit import (
        NSImage, NSAttributedString, NSFont, NSColor,
        NSBitmapImageRep, NSPNGFileType, NSMakeRect, NSRectFill,
    )

    img = NSImage.alloc().initWithSize_((float(size), float(size)))
    font_size = size * 0.85
    font = NSFont.fontWithName_size_("AppleColorEmoji", font_size)
    if font is None:
        raise RuntimeError("AppleColorEmoji font not found")
    attrs = {"NSFont": font}
    s = NSAttributedString.alloc().initWithString_attributes_(emoji, attrs)

    img.lockFocus()
    NSColor.clearColor().set()
    NSRectFill(NSMakeRect(0, 0, size, size))
    text_size = s.size()
    x = (size - text_size.width) / 2
    y = (size - text_size.height) / 2
    s.drawAtPoint_((x, y))
    img.unlockFocus()

    tiff = img.TIFFRepresentation()
    rep = NSBitmapImageRep.alloc().initWithData_(tiff)
    png = rep.representationUsingType_properties_(NSPNGFileType, {})
    png.writeToFile_atomically_(str(out), True)


def build_iconset(master: Path, iconset: Path) -> None:
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir(parents=True)
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]
    for px, name in sizes:
        subprocess.run(
            ["sips", "-z", str(px), str(px), str(master), "--out", str(iconset / name)],
            check=True,
            capture_output=True,
        )


def apply_icon(icns: Path, target: Path) -> bool:
    from AppKit import NSImage, NSWorkspace

    if not target.exists():
        print(f"  skipped (not found): {target}")
        return False
    icon = NSImage.alloc().initWithContentsOfFile_(str(icns))
    if icon is None:
        raise RuntimeError(f"could not load icon: {icns}")
    ok = NSWorkspace.sharedWorkspace().setIcon_forFile_options_(icon, str(target), 0)
    print(f"  {'applied' if ok else 'FAILED'}: {target}")
    return bool(ok)


def main() -> int:
    print(f"Rendering '{EMOJI}' to {MASTER_PNG}")
    render_emoji_png(EMOJI, MASTER_PNG)

    print(f"Building iconset at {ICONSET}")
    build_iconset(MASTER_PNG, ICONSET)

    print(f"Packaging to {ICNS}")
    subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET), "-o", str(ICNS)],
        check=True,
    )

    print("Applying icon to targets:")
    results = [apply_icon(ICNS, t) for t in TARGET_FILES]

    # Cleanup tmp artifacts
    shutil.rmtree(ICONSET, ignore_errors=True)
    MASTER_PNG.unlink(missing_ok=True)

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
