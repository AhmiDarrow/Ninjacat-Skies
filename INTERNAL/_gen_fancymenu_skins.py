#!/usr/bin/env python3
"""Procedural FancyMenu button nine-slices, title sky, and window icons.

Palette from STYLEGUIDE / existing logo generator. Regenerates assets under
pack/overrides/config/fancymenu/assets/.
"""
from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "pack/overrides/config/fancymenu/assets"
UI_LOGO = (
    ROOT
    / "pack/overrides/resourcepacks/ninjacat-skies-ui/assets/ninjacat_skies_ui/textures/gui/ninjacat_logo.png"
)

# STYLEGUIDE-aligned
INDIGO = (42, 47, 79, 255)
INDIGO_MID = (58, 64, 110, 255)
INDIGO_DEEP = (22, 26, 48, 255)
TEAL = (61, 122, 122, 255)
TEAL_BRIGHT = (90, 150, 148, 255)
TEAL_DIM = (48, 88, 90, 255)
GOLD = (212, 168, 75, 255)
CREAM = (232, 224, 213, 255)
MUTE = (70, 72, 86, 255)
MUTE_BORDER = (90, 92, 104, 255)


def _lerp(a: tuple[int, ...], b: tuple[int, ...], t: float) -> tuple[int, ...]:
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def nine_slice_button(
    path: Path,
    fill: tuple[int, int, int, int],
    border: tuple[int, int, int, int],
    highlight: tuple[int, int, int, int] | None = None,
    w: int = 64,
    h: int = 20,
    border_px: int = 5,
) -> None:
    """Flat nine-slice-friendly button: solid fill, crisp border, optional top sheen."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=3, fill=fill, outline=border, width=2)
    # Inner edge so nine-slice borders stay opaque
    inset = border_px - 1
    d.rectangle((inset, inset, w - 1 - inset, h - 1 - inset), outline=border)
    if highlight:
        d.line([(4, 3), (w - 5, 3)], fill=highlight, width=1)
        d.line([(4, 4), (w - 5, 4)], fill=(*highlight[:3], 90), width=1)
    # Corner anchors (helps nine-slice look intentional)
    for x, y in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
        d.point((x, y), fill=border)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print("wrote", path, img.size)


def title_sky(path: Path, w: int = 1920, h: int = 1080) -> None:
    """Void-indigo sky with teal wisps, sparse stars, faint loom arcs."""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        # Vertical gradient: deep void → mid indigo → slightly teal-tinted bottom
        if t < 0.55:
            c = _lerp(INDIGO_DEEP, INDIGO, t / 0.55)
        else:
            c = _lerp(INDIGO, (36, 55, 72, 255), (t - 0.55) / 0.45)
        for x in range(w):
            px[x, y] = c

    # Soft teal nebula blobs (pre-blur layer)
    nebula = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    blobs = [
        (0.22, 0.35, 0.42, 55),
        (0.68, 0.28, 0.38, 48),
        (0.48, 0.62, 0.50, 40),
        (0.82, 0.70, 0.30, 36),
        (0.12, 0.78, 0.28, 32),
    ]
    for cx_n, cy_n, r_n, alpha in blobs:
        cx, cy, r = int(cx_n * w), int(cy_n * h), int(r_n * min(w, h))
        col = (*TEAL[:3], alpha)
        nd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    nebula = nebula.filter(ImageFilter.GaussianBlur(radius=90))
    img = Image.alpha_composite(img, nebula)

    # Faint loom-strand arcs
    strands = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strands)
    for i, (y0, amp, phase, alpha) in enumerate(
        [
            (0.28, 90, 0.0, 38),
            (0.45, 70, 1.2, 28),
            (0.62, 110, 2.4, 22),
        ]
    ):
        pts = []
        base_y = int(y0 * h)
        for x in range(0, w, 8):
            yy = base_y + int(amp * math.sin(x / 180.0 + phase + i * 0.4))
            pts.append((x, yy))
        if len(pts) > 1:
            sd.line(pts, fill=(*TEAL_BRIGHT[:3], alpha), width=2)
            sd.line([(x, y + 1) for x, y in pts], fill=(*GOLD[:3], max(8, alpha // 3)), width=1)
    strands = strands.filter(ImageFilter.GaussianBlur(radius=1.2))
    img = Image.alpha_composite(img, strands)

    # Sparse stars (deterministic hash grid)
    star = ImageDraw.Draw(img)
    for i in range(220):
        # simple LCG-ish positions
        x = (i * 1103515245 + 12345) % w
        y = (i * 214013 + 2531011) % int(h * 0.85)
        bright = 140 + (i * 37) % 100
        size = 1 if i % 5 else 2
        col = (*CREAM[:3], min(255, bright)) if i % 7 else (*GOLD[:3], min(255, bright))
        star.ellipse((x, y, x + size, y + size), fill=col)
        if i % 11 == 0:
            # tiny cross sparkle
            star.point((x - 1, y), fill=(*col[:3], col[3] // 2))
            star.point((x + size + 1, y), fill=(*col[:3], col[3] // 2))

    # Soft vignette
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(8):
        a = 18 + i * 10
        m = i * 40
        vd.rectangle((m, m, w - 1 - m, h - 1 - m), outline=(10, 12, 22, a))
    vig = vig.filter(ImageFilter.GaussianBlur(radius=50))
    img = Image.alpha_composite(img, vig)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True)
    print("wrote", path, img.size)


def window_icons(logo_path: Path) -> None:
    if not logo_path.is_file():
        print("skip icons; logo missing:", logo_path)
        return
    logo = Image.open(logo_path).convert("RGBA")
    for size, name in ((16, "window_icon_16.png"), (32, "window_icon_32.png")):
        out = ASSETS / name
        icon = logo.resize((size, size), Image.NEAREST)
        icon.save(out)
        print("wrote", out, icon.size)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)

    nine_slice_button(
        ASSETS / "button_normal.png",
        fill=INDIGO,
        border=TEAL,
        highlight=TEAL_BRIGHT,
    )
    nine_slice_button(
        ASSETS / "button_hover.png",
        fill=INDIGO_MID,
        border=TEAL_BRIGHT,
        highlight=GOLD,
    )
    nine_slice_button(
        ASSETS / "button_inactive.png",
        fill=MUTE,
        border=MUTE_BORDER,
        highlight=None,
    )

    title_sky(ASSETS / "title_sky.png")

    logo = ASSETS / "ninjacat_logo.png"
    if not logo.is_file() and UI_LOGO.is_file():
        logo = UI_LOGO
    window_icons(logo)

    # CRC sanity: files non-empty
    for name in (
        "button_normal.png",
        "button_hover.png",
        "button_inactive.png",
        "title_sky.png",
        "window_icon_16.png",
        "window_icon_32.png",
    ):
        p = ASSETS / name
        assert p.is_file() and p.stat().st_size > 64, p


if __name__ == "__main__":
    main()
