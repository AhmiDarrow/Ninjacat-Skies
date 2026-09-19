#!/usr/bin/env python3
"""Driftwrecks pixel art: item and block textures, the Drift Needle's 32 frames, the Steward echo, 54 Keepsakes.

    python tools/generate_driftwrecks_art.py [--sheets DIR]

Hand-built 16x16 pixel maps drawn with a small shape library, in the pack's palette (STYLEGUIDE: teal thread, gold
seam, each Strand's own colour). Keepsakes are one object per Strand x core, drawn from a shape and the Strand's
palette; --sheets writes a render sheet per Strand for approval.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from driftwrecks_content import C, CORES, HEART, STRANDS, TRIBES  # noqa: E402

TEX = ROOT / "mods/driftwrecks/src/main/resources/assets/driftwrecks/textures"
TEAL, TEAL_LT, GOLD, GOLD_LT, INK, PAPER = (0x3D, 0x7A, 0x7A), (0x5C, 0xD8, 0xC8), (0xD4, 0xA8, 0x4B), (0xF2, 0xD2, 0x7A), (0x2A, 0x2F, 0x4F), (0xED, 0xE3, 0xCC)
STRAND_RGB = {"soil": 0x6B8E3A, "stone": 0x8A8580, "sprout": 0x5AAF5A, "claw": 0x8C8C96, "spark": 0xD4A84B, "clock": 0xC87A3A,
              "swarm": 0xE6C478, "sigil": 0x8A5FB8, "spindle": 0x3D7A7A}


def rgb(h):
    return ((h >> 16) & 255, (h >> 8) & 255, h & 255)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def pal(strand):
    base = rgb(STRAND_RGB[strand])
    return {"base": base, "dark": shade(base, 0.55), "deep": shade(base, 0.35), "light": mix(base, (255, 255, 255), 0.35), "hi": mix(base, (255, 255, 255), 0.65)}


class Px:
    def __init__(self, size=16):
        self.im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.n = size

    def p(self, x, y, c, a=255):
        if 0 <= x < self.n and 0 <= y < self.n:
            self.im.putpixel((int(x), int(y)), (*c[:3], a))

    def rect(self, x0, y0, x1, y1, c, a=255):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.p(x, y, c, a)

    def line(self, x0, y0, x1, y1, c, a=255):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.p(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c, a)

    def disc(self, cx, cy, r, c, a=255):
        for x in range(self.n):
            for y in range(self.n):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.p(x, y, c, a)

    def ring(self, cx, cy, r, c, w=1.0):
        for x in range(self.n):
            for y in range(self.n):
                d = math.hypot(x - cx, y - cy)
                if r - w <= d <= r:
                    self.p(x, y, c)

    def outline(self, c=INK):
        """Dark outline round every opaque shape (the pack's item style)."""
        src = self.im.copy()
        for x in range(self.n):
            for y in range(self.n):
                if src.getpixel((x, y))[3]:
                    continue
                if any(0 <= x + dx < self.n and 0 <= y + dy < self.n and src.getpixel((x + dx, y + dy))[3] > 128 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.p(x, y, shade(c, 1.0), 230)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.im.save(path)


# ================================================================== keepsake shapes

def s_bell(g, P):
    for y in range(4, 11):
        r = 2 + (y - 4) * 0.55
        g.rect(round(8 - r), y, round(7 + r), y, P["base"])
    g.rect(3, 11, 12, 11, P["dark"]); g.rect(7, 12, 8, 13, GOLD); g.rect(7, 2, 8, 3, P["dark"])
    g.line(9, 5, 11, 10, P["hi"]); g.line(5, 7, 7, 9, INK)   # the crack


def s_rod(g, P):
    g.line(3, 13, 12, 3, P["dark"]); g.line(4, 13, 13, 3, P["base"]); g.rect(11, 2, 13, 4, GOLD); g.p(12, 3, GOLD_LT)
    for i in range(3):
        g.p(5 + i * 3, 11 - i * 3, TEAL_LT)


def s_book(g, P):
    g.rect(3, 3, 12, 13, P["base"]); g.rect(3, 3, 4, 13, P["dark"]); g.rect(5, 4, 12, 12, PAPER)
    for y in (6, 8, 10):
        g.line(6, y, 11, y, shade(P["dark"], 1.2))
    g.rect(12, 3, 12, 13, P["dark"]); g.rect(8, 12, 9, 13, GOLD)


def s_scroll(g, P):
    g.rect(4, 3, 11, 12, PAPER); g.rect(3, 2, 12, 3, P["dark"]); g.rect(3, 12, 12, 13, P["dark"])
    g.line(5, 5, 10, 5, P["base"]); g.line(5, 7, 9, 7, P["base"]); g.disc(8, 9.5, 1.3, GOLD)


def s_tablet(g, P):
    g.rect(3, 2, 12, 13, P["dark"]); g.rect(4, 3, 11, 12, P["base"])
    for y in range(4, 12, 2):
        g.line(5, y, 5 + (y * 3) % 6, y, P["hi"])
    g.p(10, 11, TEAL_LT)


def s_pendant(g, P):
    g.line(4, 1, 8, 5, GOLD); g.line(12, 1, 8, 5, GOLD)
    for y in range(5, 14):
        w = max(0, 3 - abs(y - 9) * 0.6)
        g.rect(round(8 - w), y, round(7 + w), y, P["base"])
    g.line(8, 6, 8, 12, P["hi"]); g.p(9, 9, TEAL_LT)


def s_fork(g, P):
    g.rect(5, 2, 6, 9, P["base"]); g.rect(9, 2, 10, 9, P["base"]); g.rect(5, 9, 10, 10, P["base"]); g.rect(7, 11, 8, 14, P["dark"]); g.p(6, 3, P["hi"])


def s_cord(g, P):
    for y in range(1, 15):
        g.p(8 + round(math.sin(y * 0.8)), y, P["base"])
    for y in (3, 6, 9, 12):
        g.rect(7 + round(math.sin(y * 0.8)), y, 9 + round(math.sin(y * 0.8)), y + 1, P["dark"])
    g.p(8, 14, GOLD)


def s_tool(g, P):
    g.line(3, 14, 10, 7, (0x6B, 0x4A, 0x2E)); g.line(4, 14, 11, 7, (0x85, 0x5D, 0x3A))
    g.rect(8, 2, 13, 6, P["dark"]); g.rect(9, 3, 13, 5, P["base"]); g.line(13, 2, 13, 6, P["hi"])


def s_chisel(g, P):
    g.line(4, 13, 9, 8, (0x85, 0x5D, 0x3A)); g.line(5, 13, 10, 8, (0x6B, 0x4A, 0x2E))
    g.line(9, 7, 12, 4, P["base"]); g.line(10, 7, 13, 4, P["hi"]); g.p(13, 3, TEAL_LT)


def s_knife(g, P):
    g.line(3, 13, 7, 9, (0x6B, 0x4A, 0x2E)); g.rect(6, 8, 7, 9, GOLD)
    for i in range(6):
        g.line(8 + i, 7 - i, 8 + i, 8 - i, P["base"])
    g.line(8, 6, 13, 2, P["hi"])


def s_jar(g, P):
    g.rect(5, 4, 10, 13, P["base"]); g.rect(4, 6, 11, 12, P["base"]); g.rect(5, 2, 10, 3, P["dark"]); g.rect(6, 7, 7, 10, P["hi"])
    g.p(9, 3, GOLD); g.rect(4, 13, 11, 13, P["dark"])


def s_tin(g, P):
    g.rect(3, 5, 12, 13, P["base"]); g.rect(3, 4, 12, 5, P["dark"]); g.rect(3, 8, 12, 8, GOLD); g.rect(4, 6, 5, 12, P["hi"])


def s_box(g, P):
    g.rect(2, 5, 13, 13, P["dark"]); g.rect(3, 6, 12, 12, P["base"]); g.rect(2, 4, 13, 5, P["deep"]); g.rect(7, 7, 8, 10, GOLD); g.p(7, 8, INK)


def s_key(g, P):
    g.ring(5, 5, 3.2, P["base"], 1.3); g.line(7, 7, 13, 13, P["base"]); g.rect(11, 12, 12, 14, P["base"]); g.rect(9, 10, 10, 12, P["base"])
    g.p(5, 5, TEAL_LT)


def s_lantern(g, P):
    g.rect(6, 1, 9, 2, P["dark"]); g.rect(4, 3, 11, 13, P["dark"]); g.rect(5, 4, 10, 12, GOLD_LT); g.rect(7, 5, 8, 11, GOLD)
    g.rect(4, 13, 11, 14, P["deep"])


def s_horn(g, P):
    for i in range(10):
        r = 1 + i * 0.35
        cx, cy = 3 + i, 12 - i * 0.7
        g.disc(cx, cy, r, P["base"] if i % 3 else P["dark"])
    g.disc(12, 5, 2.4, P["deep"]); g.p(12, 5, INK)


def s_drumstick(g, P):
    g.line(3, 13, 11, 5, (0x85, 0x5D, 0x3A)); g.line(4, 13, 12, 5, (0x6B, 0x4A, 0x2E)); g.disc(12, 4, 2.2, P["base"]); g.p(12, 3, GOLD_LT)


def s_nozzle(g, P):
    for x in range(3, 14):
        h = 1 + (13 - x) * 0.35
        g.rect(x, round(8 - h), x, round(8 + h), P["base"] if x % 3 else P["dark"])
    g.rect(13, 7, 14, 9, GOLD)


def s_pod(g, P):
    g.disc(8, 9, 4.2, P["base"]); g.disc(7, 8, 2, P["light"]); g.rect(7, 2, 8, 5, (0x4A, 0x7A, 0x30)); g.p(9, 3, (0x6A, 0xA0, 0x40))


def s_acorn(g, P):
    g.disc(8, 10, 3.6, P["base"]); g.rect(4, 5, 11, 7, (0x6B, 0x4A, 0x2E)); g.rect(7, 3, 8, 4, (0x6B, 0x4A, 0x2E)); g.rect(8, 12, 9, 14, (0x5A, 0xAF, 0x5A))


def s_coil(g, P):
    for i in range(5):
        y = 3 + i * 2
        g.line(4, y, 11, y + 1, P["base"]); g.line(4, y + 1, 11, y + 2, P["dark"])
    g.rect(3, 2, 12, 2, P["deep"]); g.rect(3, 14, 12, 14, P["deep"]); g.p(8, 8, TEAL_LT)


def s_cog(g, P, teeth=9, missing=True):
    g.disc(8, 8, 4.3, P["base"]); g.disc(8, 8, 1.6, INK)
    for i in range(teeth):
        if missing and i == 2:
            continue
        a = i / teeth * math.tau
        g.rect(round(8 + math.cos(a) * 5.6) - 1, round(8 + math.sin(a) * 5.6) - 1, round(8 + math.cos(a) * 5.6), round(8 + math.sin(a) * 5.6), P["dark"])


def s_sundial(g, P):
    g.disc(8, 9, 5.5, P["base"]); g.ring(8, 9, 5.5, P["dark"], 1.0); g.line(8, 9, 8, 3, GOLD); g.line(8, 3, 11, 9, GOLD)
    for i in range(8):
        a = i / 8 * math.tau
        g.p(round(8 + math.cos(a) * 4), round(9 + math.sin(a) * 4), P["deep"])


def s_spyglass(g, P):
    g.line(3, 12, 12, 3, P["base"]); g.line(4, 13, 13, 4, P["base"]); g.line(3, 13, 13, 3, P["dark"])
    g.rect(11, 2, 13, 4, GOLD); g.line(2, 11, 5, 14, (0x5A, 0xAF, 0x5A)); g.p(7, 9, (0x5A, 0xAF, 0x5A))


def s_stone(g, P):
    g.disc(8, 9, 5, P["base"]); g.ring(8, 9, 4, P["light"], 0.7); g.ring(8, 9, 2.5, P["light"], 0.7); g.p(8, 9, (0x9C, 0xC0, 0x60)); g.p(11, 6, (0x9C, 0xC0, 0x60))


def s_charm(g, P):
    g.ring(8, 8, 4.5, P["base"], 1.4); g.line(4, 4, 12, 12, P["dark"]); g.line(12, 4, 4, 12, P["dark"]); g.p(8, 8, GOLD)
    g.rect(7, 12, 8, 14, (0x5A, 0xAF, 0x5A))


def s_frame(g, P):
    g.rect(2, 2, 13, 13, P["dark"]); g.rect(3, 3, 12, 12, PAPER)
    for i, c in enumerate([(0xE0, 0x60, 0x70), (0xE6, 0xC4, 0x78), (0x8A, 0x5F, 0xB8)]):
        g.disc(5 + i * 3, 6 + (i % 2) * 3, 1.2, c); g.line(5 + i * 3, 7 + (i % 2) * 3, 5 + i * 3, 11, (0x5A, 0xAF, 0x5A))


def s_claw(g, P):
    g.disc(8, 9, 5, P["base"])
    for i in range(4):
        g.line(5 + i * 2, 5, 4 + i * 2, 13, INK)
    g.p(12, 5, P["hi"])


def s_clasp(g, P):
    g.ring(8, 8, 5, GOLD, 1.6)
    for i in range(3):
        g.line(6 + i * 2, 3, 5 + i * 2 + 2, 9, GOLD_LT)
    g.p(8, 8, TEAL_LT)


def s_idol(g, P):
    g.disc(8, 4, 2.2, P["base"]); g.rect(6, 6, 9, 12, P["base"]); g.rect(4, 12, 11, 13, P["dark"]); g.p(7, 4, INK); g.p(9, 4, INK)
    g.p(6, 2, P["base"]); g.p(10, 2, P["base"]); g.line(6, 8, 9, 10, TEAL_LT)


def s_can(g, P):
    g.rect(4, 5, 11, 13, P["base"]); g.rect(4, 4, 11, 4, P["dark"]); g.rect(6, 1, 9, 3, P["dark"]); g.rect(12, 7, 13, 11, (0x85, 0x5D, 0x3A))
    g.p(7, 0, (0xC0, 0xC0, 0xC0), 150); g.p(8, 0, (0xC0, 0xC0, 0xC0), 110)


def s_glass(g, P):
    g.ring(7, 7, 4.5, GOLD, 1.3); g.disc(7, 7, 3.2, TEAL_LT, 150); g.line(10, 10, 14, 14, (0x6B, 0x4A, 0x2E)); g.p(6, 6, (255, 255, 255))


def s_crystal(g, P):
    for cx, h in ((6, 8), (9, 11), (11, 6)):
        g.rect(cx - 1, 14 - h, cx, 13, P["base"]); g.p(cx - 1, 14 - h, P["hi"])
    g.rect(3, 13, 13, 14, (0xC8, 0xC0, 0xB0))


def s_seal(g, P):
    g.disc(8, 8, 5.3, P["base"]); g.ring(8, 8, 5.3, P["dark"], 1.0)
    g.line(5, 8, 11, 8, GOLD); g.line(8, 5, 8, 11, GOLD); g.line(6, 6, 10, 10, GOLD_LT)


def s_rubbing(g, P):
    g.rect(3, 2, 12, 13, PAPER); g.ring(8, 8, 3.8, (0x40, 0x40, 0x48), 1.2); g.line(8, 5, 8, 11, (0x40, 0x40, 0x48)); g.line(5, 8, 11, 8, (0x40, 0x40, 0x48))


def s_whorl(g, P):
    g.rect(7, 1, 8, 14, (0x85, 0x5D, 0x3A)); g.disc(8, 11, 3.6, P["base"]); g.ring(8, 11, 3.6, P["dark"], 0.9); g.line(8, 3, 11, 6, TEAL_LT)


def s_beacon(g, P):
    g.rect(4, 9, 11, 13, P["dark"]); g.rect(5, 5, 10, 9, TEAL_LT); g.rect(6, 6, 9, 8, (255, 255, 255)); g.line(8, 1, 8, 4, TEAL_LT)


def s_card(g, P):
    g.rect(2, 3, 13, 12, PAPER)
    for x in range(3, 13, 2):
        for y in range(4, 12, 2):
            if (x * 7 + y * 3) % 5 < 2:
                g.p(x, y, INK)
    g.rect(2, 3, 13, 3, P["base"])


def s_shuttle(g, P):
    for x in range(2, 14):
        h = 2.6 - abs(x - 8) * 0.38
        g.rect(x, round(8 - h), x, round(8 + h), (0xE8, 0xE0, 0xC8) if x % 4 else (0xC8, 0xBC, 0xA0))
    g.line(4, 8, 12, 8, P["base"])


def s_flower(g, P):
    g.line(8, 7, 8, 14, (0x5A, 0xAF, 0x5A)); g.p(7, 11, (0x5A, 0xAF, 0x5A))
    for a in range(5):
        t = a / 5 * math.tau
        g.disc(8 + math.cos(t) * 2.6, 5 + math.sin(t) * 2.6, 1.4, (0x6A, 0x8C, 0xE0))
    g.p(8, 5, GOLD_LT)


def s_tapestry(g, P):
    g.rect(2, 2, 13, 12, P["base"])
    for i, s in enumerate(STRANDS):
        g.rect(2 + i + (i > 4), 3, 2 + i + (i > 4), 11, rgb(STRAND_RGB[s]))
    g.rect(2, 1, 13, 1, (0x6B, 0x4A, 0x2E)); g.line(13, 12, 14, 14, GOLD)


SHAPE = {
    "soil": ["bell", "rod", "book", "tool", "jar", "tin"],
    "stone": ["pendant", "fork", "tablet", "chisel", "stone", "key"],
    "sprout": ["charm", "spyglass", "frame", "knife", "acorn", "box"],
    "claw": ["claw", "lantern", "cord", "chisel", "flower", "clasp"],
    "spark": ["drumstick", "horn", "tablet", "nozzle", "pod", "coil"],
    "clock": ["cog", "sundial", "book", "cog", "acorn", "box"],
    "swarm": ["idol", "glass", "book", "can", "pod", "jar"],
    "sigil": ["key", "lantern", "rubbing", "chisel", "crystal", "seal"],
    "spindle": ["whorl", "beacon", "card", "shuttle", "flower", "tapestry"],
}
SHAPES = {n[2:]: f for n, f in globals().items() if n.startswith("s_")}


def keepsake(strand, core) -> Px:
    g = Px()
    shape = SHAPE[strand][CORES.index(core)]
    fn = SHAPES[shape]
    if shape == "cog" and core == "shrine":
        s_cog(g, pal(strand), teeth=10, missing=False)
    else:
        fn(g, pal(strand))
    g.outline()
    return g


def heart_keepsake() -> Px:
    g = Px()
    for i, s in enumerate(STRANDS):
        a = i / 9 * math.tau - math.pi / 2
        g.line(8, 8, round(8 + math.cos(a) * 6), round(8 + math.sin(a) * 6), rgb(STRAND_RGB[s]))
    g.disc(8, 8, 2.6, GOLD); g.disc(8, 8, 1.2, TEAL_LT)
    g.outline()
    return g


# ================================================================== items

def thread_knot(g, a, b):
    for i in range(14):
        g.p(1 + i, 8 + round(math.sin(i * 0.9) * 3), a)
        g.p(1 + i, 8 + round(math.cos(i * 0.9) * 3), b)


def items():
    I = TEX / "item"
    g = Px(); thread_knot(g, TEAL_LT, GOLD); g.rect(6, 6, 9, 10, TEAL); g.outline(); g.save(I / "salvaged_weft.png")
    g = Px(); g.disc(8, 8, 4.5, (0x30, 0x2A, 0x3A)); g.ring(8, 8, 4.5, TEAL_LT, 1.2); g.line(5, 5, 11, 11, GOLD); g.line(11, 5, 5, 11, GOLD); g.outline(); g.save(I / "frayed_core.png")
    g = Px(); g.disc(8, 8, 5.5, (0xB0, 0x3A, 0x3A)); g.disc(8, 8, 3.5, (0xC8, 0x50, 0x48)); g.line(6, 8, 10, 8, GOLD_LT); g.line(8, 6, 8, 10, GOLD_LT)
    g.line(4, 13, 6, 11, TEAL_LT); g.line(12, 13, 10, 11, TEAL_LT); g.outline(); g.save(I / "driftwreck_seal.png")
    g = Px()
    for y in range(2, 15):
        w = max(0, 3 - abs(y - 8) * 0.45)
        g.rect(round(8 - w), y, round(7 + w), y, (0x6A, 0x3A, 0xA0))
    g.line(8, 3, 8, 13, TEAL_LT); g.outline(); g.save(I / "rift_shard.png")
    g = Px(); g.rect(4, 3, 11, 13, (0x85, 0x5D, 0x3A)); g.rect(5, 5, 10, 11, TEAL_LT)
    for y in range(5, 12, 2):
        g.line(5, y, 10, y, TEAL)
    g.rect(3, 2, 12, 3, (0x6B, 0x4A, 0x2E)); g.rect(3, 13, 12, 14, (0x6B, 0x4A, 0x2E)); g.line(11, 8, 15, 10, GOLD); g.outline(); g.save(I / "tether_spool.png")
    for name, bead in (("driftlure", GOLD), ("strand_lure", (0x8A, 0x5F, 0xB8))):
        g = Px(); g.line(8, 1, 8, 8, TEAL_LT); g.line(7, 1, 9, 1, TEAL); g.disc(8, 10, 2.8, bead); g.p(7, 9, (255, 255, 255))
        g.line(5, 13, 8, 12, TEAL_LT); g.line(11, 13, 8, 12, TEAL_LT); g.outline(); g.save(I / f"{name}.png")
    g = Px(); g.ring(5, 5, 3.4, TEAL_LT, 1.4); g.line(7, 7, 13, 13, GOLD); g.rect(11, 12, 13, 13, GOLD); g.rect(9, 10, 10, 12, GOLD); g.p(5, 5, GOLD_LT); g.outline(); g.save(I / "weft_key.png")
    g = Px(); g.disc(8, 10, 4.8, (0xA0, 0x80, 0x58)); g.rect(6, 3, 9, 6, (0x85, 0x5D, 0x3A)); g.line(4, 5, 11, 5, TEAL_LT); g.p(6, 9, (0xC0, 0xA0, 0x70)); g.outline(); g.save(I / "salvage_bundle.png")
    g = Px(); g.rect(2, 2, 13, 13, TEAL); g.rect(3, 3, 12, 12, PAPER)
    for x in range(4, 12, 3):
        for y in range(4, 12, 3):
            g.rect(x, y, x + 1, y + 1, GOLD if (x + y) % 2 else TEAL_LT)
    g.rect(2, 2, 2, 13, (0x1E, 0x4A, 0x4A)); g.outline(); g.save(I / "wreck_atlas.png")
    g = Px(); g.rect(3, 3, 12, 12, PAPER); g.rect(2, 2, 13, 3, (0x85, 0x5D, 0x3A)); g.rect(2, 12, 13, 13, (0x85, 0x5D, 0x3A))
    g.line(4, 10, 7, 6, TEAL); g.line(7, 6, 10, 8, TEAL); g.p(10, 7, (0xB0, 0x3A, 0x3A)); g.p(11, 7, (0xB0, 0x3A, 0x3A)); g.outline(); g.save(I / "wreck_map_scroll.png")
    g = Px(); g.rect(4, 2, 12, 13, PAPER); g.line(5, 5, 11, 5, INK); g.line(5, 7, 10, 7, INK); g.line(5, 9, 11, 9, INK); g.disc(10, 11, 1.5, GOLD); g.outline(); g.save(I / "hint_page.png")
    # the needle: 32 frames, frame 16 points straight up (target ahead), clockwise
    for i in range(32):
        g = Px(); g.disc(8, 8, 6.6, (0x6B, 0x4A, 0x2E)); g.disc(8, 8, 5.4, PAPER); g.ring(8, 8, 5.4, GOLD, 0.8)
        a = (i - 16) / 32 * math.tau - math.pi / 2
        tip = (8 + math.cos(a) * 4.6, 8 + math.sin(a) * 4.6)
        tail = (8 - math.cos(a) * 3, 8 - math.sin(a) * 3)
        g.line(round(tail[0]), round(tail[1]), 8, 8, INK); g.line(8, 8, round(tip[0]), round(tip[1]), TEAL)
        g.p(round(tip[0]), round(tip[1]), TEAL_LT); g.p(8, 8, GOLD)
        g.outline(); g.save(I / f"drift_needle_{i:02d}.png")
    for s in STRANDS:
        for c in CORES:
            keepsake(s, c).save(I / f"keepsake_{s}_{c}.png")
    heart_keepsake().save(I / "keepsake_heartwreck.png")


# ================================================================== blocks

def wood(g, base=(0x6B, 0x4A, 0x2E)):
    for y in range(16):
        for x in range(16):
            v = 0.85 + 0.15 * math.sin(x * 0.7 + y * 0.15 + (y // 4) * 2.1)
            g.p(x, y, shade(base, v))
    for y in (0, 4, 8, 12):
        g.line(0, y, 15, y, shade(base, 0.6))


def blocks():
    B = TEX / "block"
    g = Px()
    for y in range(16):
        for x in range(16):
            weave = ((x // 2) + (y // 2)) % 2
            g.p(x, y, TEAL_LT if weave else TEAL, 255)
    for i in range(0, 16, 4):
        g.line(i, 0, i, 15, GOLD)
    g.save(B / "tether_thread.png")
    g = Px(); g.rect(0, 0, 15, 15, (0, 0, 0), 0)
    for x in range(16):
        g.p(x, 7, TEAL_LT); g.p(x, 8, TEAL); g.p(x, 15, TEAL); g.p(x, 14, TEAL_LT if x % 2 else GOLD)
    g.save(B / "tether_thread_side.png")
    for face in ("front", "side", "top"):
        g = Px(); wood(g, (0x5A, 0x40, 0x2A))
        g.rect(0, 5, 15, 6, TEAL); g.rect(0, 12, 15, 12, (0x3A, 0x3A, 0x44))
        if face == "front":
            g.rect(6, 4, 9, 8, GOLD); g.p(7, 6, INK); g.p(8, 6, INK)
        if face == "top":
            g.rect(0, 0, 15, 15, (0x5A, 0x40, 0x2A)); wood(g, (0x50, 0x38, 0x24)); g.rect(0, 7, 15, 8, TEAL)
        g.line(2, 14, 5, 11, TEAL_LT)   # a frayed seam scar
        g.save(B / f"wreck_chest_{face}.png")
    g = Px(); g.rect(0, 0, 15, 15, (0x22, 0x20, 0x2A))
    for i in range(0, 16, 3):
        g.line(i, 0, i, 15, (0x3A, 0x38, 0x46)); g.line(0, i, 15, i, (0x3A, 0x38, 0x46))
    g.line(3, 13, 7, 8, TEAL_LT); g.line(7, 8, 6, 5, TEAL_LT); g.line(6, 5, 11, 2, GOLD); g.line(8, 9, 12, 12, TEAL)
    g.save(B / "frayed_spawner.png")
    for lit in ("off", "on"):
        g = Px(); g.rect(0, 0, 15, 15, (0x5A, 0x56, 0x60))
        for y in range(0, 16, 2):
            g.line(0, y, 15, y + 1, TEAL_LT if lit == "on" else (0x40, 0x5A, 0x5A))
        if lit == "on":
            g.rect(6, 0, 9, 15, (0xA0, 0xF0, 0xE8))
        g.save(B / f"thread_pillar_{lit}.png")
    g = Px(); g.rect(0, 0, 15, 15, (0x48, 0x44, 0x50)); g.disc(8, 8, 4, TEAL); g.disc(8, 8, 2, GOLD); g.save(B / "thread_pillar_top.png")
    g = Px(); wood(g, (0x6B, 0x4A, 0x2E))
    for y in range(0, 16, 2):
        g.line(0, y, 15, y + 2, TEAL_LT)
    g.rect(6, 3, 9, 5, GOLD); g.save(B / "thread_idol.png")
    g = Px(); g.rect(0, 0, 15, 15, (0x6B, 0x4A, 0x2E)); g.disc(8, 8, 5, TEAL); g.disc(8, 8, 2, GOLD); g.save(B / "thread_idol_top.png")
    g = Px()
    for y in range(16):
        for x in range(16):
            if (x + y) % 3 == 0 or (x - y) % 4 == 0:
                g.p(x, y, TEAL_LT if (x // 4) % 2 else GOLD, 200)
    g.save(B / "thread_lock.png")
    g = Px()
    for y in range(16):
        w = 1.2 + 2.2 * math.sin(y / 15 * math.pi)
        for x in range(16):
            d = abs(x - 7.5 - math.sin(y * 0.8) * 0.8)
            if d < w:
                g.p(x, y, mix((0x6A, 0x3A, 0xA0), TEAL_LT, 1 - d / w), int(120 + 135 * (1 - d / w)))
    g.save(B / "rift_tear.png")
    g = Px(); wood(g, (0x80, 0x60, 0x40)); g.rect(0, 0, 15, 1, (0x50, 0x38, 0x24)); g.rect(0, 14, 15, 15, (0x50, 0x38, 0x24)); g.rect(0, 7, 15, 8, TEAL); g.save(B / "salvage_crate_side.png")
    g = Px(); wood(g, (0x70, 0x52, 0x36)); g.rect(0, 0, 15, 15, (0x50, 0x38, 0x24)); g.rect(1, 1, 14, 14, (0x80, 0x60, 0x40)); g.line(1, 1, 14, 14, (0x50, 0x38, 0x24)); g.line(14, 1, 1, 14, (0x50, 0x38, 0x24)); g.save(B / "salvage_crate_top.png")
    g = Px(); wood(g, (0x85, 0x5D, 0x3A)); g.save(B / "salvagers_frame_wood.png")
    g = Px()
    for x in range(0, 16, 2):
        g.line(x, 0, x, 15, TEAL_LT if x % 4 else GOLD, 230)
    g.line(0, 9, 15, 9, (0xE8, 0xE0, 0xC8))
    g.save(B / "salvagers_frame_warp.png")
    g = Px(); g.rect(0, 0, 15, 15, (0x9A, 0x96, 0x92)); g.rect(0, 0, 15, 1, (0x7A, 0x76, 0x72)); g.rect(0, 14, 15, 15, (0x7A, 0x76, 0x72)); g.rect(0, 7, 15, 7, TEAL); g.save(B / "trophy_plinth_side.png")
    g = Px(); g.rect(0, 0, 15, 15, (0xA8, 0xA4, 0xA0)); g.ring(8, 8, 6, TEAL, 1.0); g.ring(8, 8, 3, GOLD, 1.0); g.save(B / "trophy_plinth_top.png")
    for s in STRANDS:
        P = pal(s)
        g = Px(); g.rect(0, 0, 15, 15, P["base"]); g.rect(0, 0, 15, 1, P["deep"])
        for x in range(0, 16, 2):
            g.p(x, 15, P["deep"])
        g.rect(1, 2, 1, 14, TEAL_LT); g.rect(14, 2, 14, 14, GOLD)
        shape = SHAPES[SHAPE[s][0]]
        emb = Px(); shape(emb, {"base": P["hi"], "dark": P["light"], "deep": P["dark"], "light": P["hi"], "hi": (255, 255, 255)})
        g.im.alpha_composite(emb.im.resize((10, 10), Image.NEAREST), (3, 3))
        g.save(B / f"tribe_banner_{s}.png")


def entity():
    E = TEX / "entity"
    im = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    for y in range(32):
        for x in range(64):
            t = ((x // 2) + (y // 2)) % 2
            im.putpixel((x, y), (*(TEAL_LT if t else TEAL), 255))
            if (x * 7 + y * 3) % 11 == 0:
                im.putpixel((x, y), (*GOLD, 255))
    E.mkdir(parents=True, exist_ok=True)
    im.save(E / "steward_echo.png")


def sheets(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    from PIL import ImageFont
    for s in STRANDS:
        W, H = 6 * 150, 190
        sheet = Image.new("RGB", (W, H), (0xED, 0xE3, 0xCC))
        d = ImageDraw.Draw(sheet)
        d.text((10, 6), f"{TRIBES[s]} ({s}) keepsakes", fill=INK)
        for i, c in enumerate(CORES):
            im = Image.open(TEX / "item" / f"keepsake_{s}_{c}.png").resize((96, 96), Image.NEAREST)
            sheet.paste(im, (i * 150 + 27, 26), im)
            name = C[s][c][0]
            d.text((i * 150 + 8, 130), c, fill=(0x3D, 0x7A, 0x7A))
            for j, line in enumerate([name[k:k + 22] for k in range(0, len(name), 22)]):
                d.text((i * 150 + 8, 146 + j * 12), line, fill=INK)
        sheet.save(out / f"keepsakes_{s}.png")
    all_ = Image.new("RGB", (6 * 40 + 20, 9 * 40 + 20), (0xED, 0xE3, 0xCC))
    for r, s in enumerate(STRANDS):
        for c, core in enumerate(CORES):
            im = Image.open(TEX / "item" / f"keepsake_{s}_{core}.png").resize((32, 32), Image.NEAREST)
            all_.paste(im, (10 + c * 40, 10 + r * 40), im)
    all_.save(out / "keepsakes_all.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets", default="")
    a = ap.parse_args()
    items()
    blocks()
    entity()
    if a.sheets:
        sheets(Path(a.sheets))
    print("Driftwrecks art written to", TEX.relative_to(ROOT))


if __name__ == "__main__":
    main()
