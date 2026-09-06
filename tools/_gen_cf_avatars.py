"""Generate CurseForge project avatars (512x512)."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CF = ROOT / "docs" / "public" / "cf-assets"
TP_OUT = ROOT.parent / "tribal-power" / "docs" / "public"


def tribal_icon(size: int = 512) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size // 2
    r = 248
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= r:
                t = dist / r
                R = int(18 + 20 * (1 - t))
                G = int(24 + 70 * t)
                B = int(48 + 90 * t)
                a = 255
                if dist > r - 6:
                    a = int(255 * (r - dist) / 6)
                img.putpixel((x, y), (R, G, B, a))

    for rad, color in [
        (200, (80, 200, 190, 180)),
        (160, (120, 160, 255, 140)),
        (110, (200, 170, 80, 160)),
    ]:
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=color, width=6)

    pts = [(cx, cy - 90), (cx + 70, cy), (cx, cy + 90), (cx - 70, cy)]
    d.polygon(pts, fill=(40, 90, 120, 230), outline=(220, 200, 120, 255))
    d.line([cx, cy - 70, cx, cy + 70], fill=(240, 220, 140, 255), width=8)
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(30, 50, 80, 255), outline=(120, 230, 210, 255), width=4)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(90, 240, 220, 255))

    for ang_off in range(8):
        ang = ang_off * math.pi / 4
        x1 = cx + int(math.cos(ang) * 175)
        y1 = cy + int(math.sin(ang) * 175)
        x2 = cx + int(math.cos(ang) * 205)
        y2 = cy + int(math.sin(ang) * 205)
        d.line([x1, y1, x2, y2], fill=(160, 220, 255, 200), width=5)

    return img.filter(ImageFilter.SMOOTH_MORE)


def main() -> None:
    CF.mkdir(parents=True, exist_ok=True)
    TP_OUT.mkdir(parents=True, exist_ok=True)

    ncs_src = ROOT / "docs" / "public" / "pack-icon.png"
    Image.open(ncs_src).convert("RGBA").save(CF / "ninjacat-skies-avatar-512.png")

    tribal = tribal_icon()
    tribal.save(CF / "tribal-power-avatar-512.png")
    tribal.save(TP_OUT / "project-icon-512.png")
    print("wrote", CF)
    print("wrote", TP_OUT / "project-icon-512.png")


if __name__ == "__main__":
    main()
