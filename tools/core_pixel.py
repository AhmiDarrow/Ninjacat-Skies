"""Shared 32px pixel-art primitives for the Core art generators (generate_core_art.py, generate_guardians_items.py).

Style (docs: visual STYLE_TARGET): 32x32 native, no anti-aliasing, alpha 0/255, top-left light, 4-5 tone
hue-shifted ramps (shadows cooler, highlights warmer), 1 px outline tinted toward the item's own hue, ink #111a22.
Palette = the Living Lattice colours (tribal-power tools/art/lattice.py) so Core sits with Tribal Power.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CLEAR = (0, 0, 0, 0)
INK = (17, 26, 34, 255)
WOOD_DARK, WOOD, WOOD_LIGHT = (0x3e, 0x28, 0x1f, 255), (0x5a, 0x3b, 0x2e, 255), (0x7a, 0x51, 0x38, 255)
STONE_DARK, STONE, STONE_LIGHT, STONE_PALE = (0x2a, 0x36, 0x3f, 255), (0x3a, 0x4a, 0x55, 255), (0x55, 0x66, 0x72, 255), (0x74, 0x86, 0x92, 255)
COPPER_DARK, COPPER, COPPER_LIGHT = (0x8a, 0x5e, 0x30, 255), (0xc0, 0x8a, 0x4e, 255), (0xe3, 0xb1, 0x71, 255)
BRASS_DARK, BRASS, BRASS_LIGHT = (0x9a, 0x74, 0x2e, 255), (0xd2, 0xa5, 0x4a, 255), (0xf1, 0xd0, 0x82, 255)
LOOM_DEEP, LOOM, LOOM_PALE = (0x2f, 0x8a, 0x86, 255), (0x62, 0xd1, 0xc9, 255), (0xc9, 0xf6, 0xf1, 255)
BONE_SHADE, BONE, BONE_LIGHT = (176, 165, 136, 255), (225, 217, 189, 255), (246, 241, 222, 255)
INDIGO_DEEP, INDIGO, INDIGO_LIGHT = (0x1e, 0x22, 0x3c, 255), (0x2e, 0x34, 0x58, 255), (0x45, 0x4d, 0x7c, 255)
COOL = (24, 34, 72)      # shadow hue pull (blue-violet)
WARM = (255, 238, 196)   # highlight hue pull (warm cream)


def rgba(c):
    c = tuple(int(v) for v in c)
    return c if len(c) == 4 else c + (255,)


def mix(a, b, t):
    return rgba(tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))


def ramp(base):
    """5 tones, dark -> light: [deep, shade, base, light, highlight]; shadows cooler, highlights warmer."""
    b = rgba(base)
    return [mix(b, COOL, 0.55), mix(b, COOL, 0.28), b, mix(b, WARM, 0.28), mix(b, WARM, 0.58)]


def outline_colour(base):
    return mix(INK, base, 0.22)


def blank(w=32, h=32):
    return Image.new("RGBA", (w, h), CLEAR)


def draw(im):
    return ImageDraw.Draw(im)


def opaque(im, x, y):
    w, h = im.size
    return 0 <= x < w and 0 <= y < h and im.getpixel((x, y))[3] > 0


def outline(im, colour=INK, diagonal=False):
    """1 px outline around every opaque region (drawn into transparent pixels)."""
    w, h = im.size; src = im.copy(); px = im.load()
    nb = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (-1, -1), (1, -1), (-1, 1)] if diagonal else [])
    for y in range(h):
        for x in range(w):
            if src.getpixel((x, y))[3] == 0 and any(opaque(src, x + dx, y + dy) for dx, dy in nb):
                px[x, y] = rgba(colour)
    return im


def lit(im, mask_colour, r, rim=True):
    """Relight a flat-filled region (every pixel == mask_colour): top/left edge -> light, bottom/right -> shade,
    a second band of deep on the bottom-right edge. r = ramp(base)."""
    w, h = im.size; src = im.copy(); px = im.load(); m = rgba(mask_colour)
    inside = lambda x, y: 0 <= x < w and 0 <= y < h and src.getpixel((x, y)) == m
    for y in range(h):
        for x in range(w):
            if not inside(x, y):
                continue
            c = r[2]
            if not inside(x + 1, y) or not inside(x, y + 1):
                c = r[1]
                if rim and (not inside(x + 1, y + 1)) and (not inside(x + 1, y) and not inside(x, y + 1)):
                    c = r[0]
            elif not inside(x - 1, y) or not inside(x, y - 1):
                c = r[3]
            px[x, y] = c
    return im


def sparkle(im, x, y, c):
    im.putpixel((x, y), rgba(c))


def from_rows(rows, palette, size=None):
    """Pixel map -> image. palette: char -> colour; '.' is clear."""
    h = len(rows); w = max(len(r) for r in rows)
    im = blank(*(size or (w, h)))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                im.putpixel((x, y), rgba(palette[ch]))
    return im


def paste_rows(im, x0, y0, rows, palette):
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                im.putpixel((x0 + x, y0 + y), rgba(palette[ch]))


def assert_clean(im, name):
    """No semi-transparent pixels on items/blocks."""
    bad = [a for *_, a in im.getdata() if a not in (0, 255)]
    assert not bad, f"{name}: {len(bad)} semi-transparent pixels"


def save(im, path: Path, quiet=False):
    assert_clean(im, path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    if not quiet:
        print("wrote", path.relative_to(ROOT).as_posix())
