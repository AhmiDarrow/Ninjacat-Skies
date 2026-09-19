#!/usr/bin/env python3
"""32x32 Guardians items: the thirteen Relics and the thirteen Frayed Totems.

    python tools/generate_guardians_items.py           # write mods/guardians/.../textures/item/*.png
    python tools/generate_guardians_items.py --check   # exit 1 on drift

Replaces the 16px hand PNGs (their documented relics/pixel.py never existed). Style: tools/core_pixel.py.
Relics are precious and each has its own silhouette (gold settings, a gem or glow, one specular glint).
Frayed Totems share one silhouette (a carved post with a frayed cord skirt) and carry the boss's canonical
strand glyph from tools/art_tribe_glyphs.py, or a boss mark for the four strandless Guardians.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core_pixel import *  # noqa: E402,F403
from art_tribe_glyphs import TRIBE_COLORS, glyph_pixels  # noqa: E402

DEST = ROOT / "mods/guardians/src/main/resources/assets/guardians/textures/item"
GOLD = BRASS
# boss -> (strand or None, accent colour) — colours from GuardianKind
BOSSES = {
    "beddown": ("soil", (0x6B, 0x8E, 0x3A)), "grindmaw": ("stone", (0x8A, 0x85, 0x80)),
    "thornmother": ("sprout", (0x5A, 0xAF, 0x5A)), "edgewalker": ("claw", (0x8C, 0x8C, 0x96)),
    "drumheart": ("spark", (0xD4, 0xA8, 0x4B)), "cogwright": ("clock", (0xC8, 0x7A, 0x3A)),
    "hivemind": ("swarm", (0xE6, 0xC4, 0x78)), "sealbreaker": ("sigil", (0x8A, 0x5F, 0xB8)),
    "unwoven": ("spindle", (0x3D, 0x7A, 0x7A)), "lintgolem": (None, (0xB8, 0xB4, 0xBC)),
    "tangle": (None, (0xC9, 0xA4, 0x5C)), "firstcut": (None, (0x5a, 0x3a, 0x78)),
    "overweaver": (None, (0x6C, 0x4F, 0xB0)),
}


def shape(im, fn, base, light=True):
    """Draw a flat shape with fn(draw, colour) on a scratch layer, relight it, and composite it on im."""
    layer = blank(); fn(draw(layer), rgba(base))
    if light:
        lit(layer, rgba(base), ramp(base))
    im.alpha_composite(layer)
    return layer


def glint(im, x, y, big=False):
    im.putpixel((x, y), BONE_LIGHT)
    if big:
        im.putpixel((x + 1, y), mix(BONE_LIGHT, BRASS_LIGHT, 0.5)); im.putpixel((x, y + 1), mix(BONE_LIGHT, BRASS_LIGHT, 0.5))


def done(im, base):
    return outline(im, outline_colour(base))


# ------------------------------------------------------------------ relics
def rootheart():
    im = blank(); g = (0x8f, 0xc0, 0x5a)
    shape(im, lambda d, c: (d.ellipse((6, 7, 16, 17), fill=c), d.ellipse((15, 7, 25, 17), fill=c),
                            d.polygon(((6, 13), (25, 13), (16, 25)), fill=c)), g)
    gr = ramp(g)
    for (x, y) in ((14, 7), (15, 7), (16, 7), (17, 7), (15, 8), (16, 8), (15, 9), (16, 9)):  # the heart's cleft
        im.putpixel((x, y), CLEAR)
    for (x, y) in ((14, 8), (17, 8), (14, 10), (17, 10), (15, 10), (16, 10)):
        im.putpixel((x, y), gr[1])
    d = draw(im); r = ramp(WOOD_LIGHT)
    for pts in (((4, 6), (8, 10), (7, 15), (10, 20), (15, 26)), ((27, 6), (23, 10), (24, 15), (21, 20), (16, 26)),
                ((15, 26), (14, 29)), ((16, 26), (18, 29))):
        d.line(pts, fill=r[2], width=2)
        d.line(pts, fill=r[3], width=1)
    d.line((10, 5, 12, 9), fill=r[2]); d.line((21, 5, 19, 9), fill=r[2])
    glint(im, 10, 10, True); im.putpixel((18, 20), ramp(g)[0])
    return done(im, WOOD_DARK)


def grindcore():
    im = blank(); d = draw(im)
    shape(im, lambda d, c: d.ellipse((3, 3, 28, 28), fill=c), STONE_PALE)
    d = draw(im); s = ramp(STONE_PALE)
    for a in range(0, 360, 45):  # millstone furrows
        x0, y0 = 15.5 + 7 * math.cos(math.radians(a)), 15.5 + 7 * math.sin(math.radians(a))
        x1, y1 = 15.5 + 11 * math.cos(math.radians(a + 20)), 15.5 + 11 * math.sin(math.radians(a + 20))
        d.line((x0, y0, x1, y1), fill=s[1])
    d.ellipse((9, 9, 22, 22), outline=GOLD, width=2); d.arc((9, 9, 22, 22), 180, 270, fill=BRASS_LIGHT)
    shape(im, lambda d, c: d.ellipse((12, 12, 19, 19), fill=c), LOOM)
    glint(im, 13, 13, True); glint(im, 7, 8)
    return done(im, STONE_DARK)


def thornseed():
    im = blank(); d = draw(im); v = ramp(WOOD)
    d.line(((3, 28), (8, 24), (7, 19), (12, 14), (10, 8)), fill=v[1], width=2)
    for (x, y, dx, dy) in ((8, 24, -2, -1), (7, 19, -2, 1), (11, 14, 2, 0), (10, 9, -2, -1)):
        d.line((x, y, x + dx, y + dy), fill=v[3])
    shape(im, lambda d, c: d.ellipse((12, 7, 26, 25), fill=c), (0x5a, 0xaf, 0x5a))
    shape(im, lambda d, c: d.polygon(((13, 10), (19, 4), (25, 10), (19, 12)), fill=c), GOLD)
    d = draw(im); gr = ramp((0x5a, 0xaf, 0x5a))
    d.line((19, 13, 19, 23), fill=gr[1]); d.point((19, 12), fill=gr[0])
    glint(im, 15, 14, True)
    return done(im, WOOD_DARK)


def edgestep():
    im = blank(); st = (0x9a, 0xa4, 0xb4)
    shape(im, lambda d, c: d.polygon(((5, 27), (9, 16), (16, 8), (27, 3), (20, 12), (13, 20), (9, 27)), fill=c), st)
    d = draw(im); s = ramp(st)
    d.line(((8, 23), (11, 16), (17, 10), (25, 5)), fill=s[4])
    shape(im, lambda d, c: d.polygon(((3, 24), (11, 28), (10, 30), (2, 26)), fill=c), GOLD)
    d = draw(im); d.rectangle((5, 27, 7, 29), fill=ramp(LOOM)[2]); d.point((5, 27), fill=LOOM_PALE)
    glint(im, 20, 8)
    return done(im, STONE_DARK)


def drumpulse():
    im = blank(); body = (0xb0, 0x4a, 0x2c)
    shape(im, lambda d, c: d.rectangle((6, 9, 25, 25), fill=c), body)
    d = draw(im); b = ramp(body)
    for x in range(8, 25, 4):
        d.line((x, 12, x + 2, 22), fill=BONE_SHADE); d.line((x + 2, 12, x, 22), fill=BONE_SHADE)
    shape(im, lambda d, c: d.rectangle((5, 23, 26, 26), fill=c), GOLD)
    shape(im, lambda d, c: d.ellipse((5, 5, 26, 12), fill=c), BONE)
    shape(im, lambda d, c: d.rectangle((5, 8, 26, 10), fill=c), GOLD, light=True)
    d = draw(im); d.ellipse((6, 5, 25, 9), fill=BONE); d.ellipse((12, 6, 19, 8), fill=BONE_LIGHT)
    y = ramp(BRASS_LIGHT)  # the pulse: a spark bolt struck into the skin
    d.line(((17, 1), (14, 5), (18, 5), (15, 9)), fill=y[3], width=1); d.point((17, 1), fill=BONE_LIGHT)
    glint(im, 8, 13)
    return done(im, b[0])


def cogloop():
    im = blank(); c = COPPER
    def cog(d, col):
        for a in range(0, 360, 40):
            x, y = 15.5 + 12 * math.cos(math.radians(a)), 15.5 + 12 * math.sin(math.radians(a))
            d.rectangle((x - 2, y - 2, x + 2, y + 2), fill=col)
        d.ellipse((5, 5, 26, 26), fill=col)
    shape(im, cog, c)
    d = draw(im); d.ellipse((10, 10, 21, 21), fill=CLEAR)
    layer = blank(); draw(layer).ellipse((10, 10, 21, 21), outline=GOLD, width=2)
    im.alpha_composite(layer)
    shape(im, lambda d, col: d.ellipse((13, 13, 18, 18), fill=col), TRIBE_COLORS["clock"])
    d = draw(im); d.arc((10, 10, 21, 21), 200, 260, fill=BRASS_LIGHT)
    glint(im, 14, 14); glint(im, 8, 7)
    return done(im, COPPER_DARK)


def hivecall():
    im = blank(); h = (0xe0, 0xae, 0x48)
    shape(im, lambda d, c: d.polygon(((4, 10), (10, 7), (20, 9), (27, 4), (29, 8), (24, 17), (14, 21), (6, 18)), fill=c), h)
    d = draw(im); r = ramp(h)
    for (x, y) in ((9, 11), (14, 12), (19, 12), (11, 16), (16, 16), (21, 14)):
        d.polygon(((x, y - 2), (x + 2, y - 1), (x + 2, y + 1), (x, y + 2), (x - 2, y + 1), (x - 2, y - 1)), outline=r[0], fill=r[3])
    shape(im, lambda d, c: d.ellipse((2, 8, 7, 19), fill=c), BRASS_DARK)
    d = draw(im); d.ellipse((3, 10, 6, 17), fill=INK)
    d.line(((24, 17), (22, 24), (26, 28)), fill=ramp(WOOD_LIGHT)[2], width=2)  # carry cord
    d.point((12, 24), fill=BRASS_LIGHT); d.point((9, 26), fill=BRASS); d.point((14, 27), fill=BRASS)  # bees
    glint(im, 24, 7)
    return done(im, r[0])


def sealmark():
    im = blank(); v = TRIBE_COLORS["sigil"]
    rib = ramp(v)
    shape(im, lambda d, c: (d.polygon(((10, 18), (14, 20), (10, 30), (8, 27)), fill=c),
                            d.polygon(((22, 18), (18, 20), (22, 30), (24, 27)), fill=c)), rib[1], light=False)
    def wax(d, c):
        for a in range(0, 360, 30):
            x, y = 16 + 11 * math.cos(math.radians(a)), 14 + 11 * math.sin(math.radians(a))
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=c)
        d.ellipse((5, 3, 27, 25), fill=c)
    shape(im, wax, v)
    layer = blank(); draw(layer).ellipse((8, 6, 24, 22), outline=GOLD, width=1); im.alpha_composite(layer)
    for dx, dy in glyph_pixels("sigil", 1):
        im.putpixel((12 + dx, 10 + dy), rib[0])
        if (12 + dx + 1, 10 + dy + 1) and im.getpixel((13 + dx, 11 + dy)) == rgba(v):
            im.putpixel((13 + dx, 11 + dy), rib[3])
    glint(im, 9, 7, True)
    return done(im, rib[0])


def loomthread():
    im = blank(); t = LOOM
    shape(im, lambda d, c: d.rectangle((9, 8, 22, 23), fill=c), t)
    d = draw(im); r = ramp(t)
    for y in range(9, 23, 2):
        d.line((9, y, 22, y), fill=r[1])
    for y in range(9, 23, 4):
        d.point((10, y), fill=LOOM_PALE)
    shape(im, lambda d, c: d.rectangle((6, 4, 25, 8), fill=c), GOLD)
    shape(im, lambda d, c: d.rectangle((6, 23, 25, 27), fill=c), GOLD)
    d = draw(im)
    d.line(((22, 16), (26, 19), (24, 24), (28, 29)), fill=r[3])  # loose glowing end
    d.point((28, 29), fill=LOOM_PALE); d.point((15, 6), fill=ramp(LOOM)[2]); d.point((16, 6), fill=ramp(LOOM)[2])
    glint(im, 8, 5, True)
    return done(im, LOOM_DEEP)


def lintwisp():
    im = blank(); gl = (0xa8, 0xd8, 0xe0)
    shape(im, lambda d, c: d.ellipse((7, 9, 24, 28), fill=c), (0x88, 0xa8, 0xb4))   # glass vial body
    d = draw(im); d.ellipse((9, 11, 22, 26), fill=(0x4b, 0x55, 0x6e, 255))
    shape(im, lambda d, c: (d.ellipse((11, 15, 18, 22), fill=c), d.ellipse((15, 13, 21, 19), fill=c)), (0xd8, 0xd4, 0xdc))
    d = draw(im); d.point((13, 17), fill=LOOM); d.point((18, 15), fill=LOOM_PALE)
    for (x, y) in ((12, 23), (19, 22), (16, 12)):
        d.point((x, y), fill=(0xd8, 0xd4, 0xdc, 255))
    shape(im, lambda d, c: d.rectangle((12, 5, 19, 10), fill=c), (0x88, 0xa8, 0xb4))
    shape(im, lambda d, c: d.rectangle((11, 2, 20, 5), fill=c), GOLD)
    d = draw(im); d.line((10, 13, 10, 20), fill=mix(gl, WARM, 0.5)); d.point((11, 12), fill=BONE_LIGHT)
    return done(im, STONE_DARK)


def knotcharm():
    im = blank()
    layer = blank(); d = draw(layer)
    for box in ((5, 9, 18, 22), (13, 9, 26, 22), (9, 4, 22, 17)):
        d.ellipse(box, outline=rgba(GOLD), width=3)
    lit(layer, rgba(GOLD), ramp(GOLD)); im.alpha_composite(layer)
    d = draw(im); r = ramp(GOLD)
    d.arc((5, 9, 18, 22), 190, 250, fill=r[4]); d.arc((9, 4, 22, 17), 200, 260, fill=r[4])
    shape(im, lambda d, c: d.ellipse((13, 22, 18, 28), fill=c), TRIBE_COLORS["spindle"])
    d = draw(im); d.line((15, 19, 15, 22), fill=r[1]); glint(im, 14, 23)
    return done(im, BRASS_DARK)


def firstcut_shard():
    im = blank(); ob = (0x3a, 0x26, 0x52)
    shape(im, lambda d, c: d.polygon(((16, 2), (24, 12), (21, 28), (12, 30), (8, 16)), fill=c), ob)
    d = draw(im); r = ramp(ob)
    d.polygon(((16, 2), (12, 16), (8, 16)), fill=r[3]); d.polygon(((16, 2), (24, 12), (17, 16)), fill=r[2])
    d.line(((16, 2), (15, 14), (16, 29)), fill=r[0])
    cut = ramp((0xd0, 0x5a, 0xa0))  # the glowing cut through the stone
    d.line(((10, 24), (15, 17), (22, 10)), fill=cut[3]); d.line(((11, 24), (16, 17)), fill=cut[4])
    glint(im, 13, 8, True)
    return done(im, r[0])


def overweaver_shuttle():
    im = blank(); v = (0x6C, 0x4F, 0xB0)
    shape(im, lambda d, c: d.polygon(((2, 26), (9, 17), (20, 9), (29, 4), (23, 13), (13, 22)), fill=c), v)
    d = draw(im); r = ramp(v)
    d.polygon(((11, 18), (18, 12), (19, 14), (13, 20)), fill=INK)   # bobbin slot
    d.line((12, 18, 18, 13), fill=ramp(LOOM)[3])
    shape(im, lambda d, c: d.polygon(((2, 26), (5, 22), (7, 24)), fill=c), GOLD)
    shape(im, lambda d, c: d.polygon(((29, 4), (24, 7), (26, 9)), fill=c), GOLD)
    t = ramp(LOOM)
    d = draw(im); d.line(((13, 20), (12, 25), (16, 28), (22, 27)), fill=t[2])
    d.line(((6, 21), (16, 12), (24, 7)), fill=r[4])
    glint(im, 25, 7)
    return done(im, r[0])


RELICS = {
    "rootheart": rootheart, "grindcore": grindcore, "thornseed": thornseed, "edgestep": edgestep,
    "drumpulse": drumpulse, "cogloop": cogloop, "hivecall": hivecall, "sealmark": sealmark,
    "loomthread": loomthread, "lintwisp": lintwisp, "knotcharm": knotcharm, "firstcut_shard": firstcut_shard,
    "overweaver_shuttle": overweaver_shuttle,
}


# ------------------------------------------------------------------ frayed totems
MARKS = {  # 9x9 marks for the Guardians that have no strand
    "lintgolem": [".#.#.#...", "#.#.#.#..", ".#####.#.", "#######..", ".#######.", "#######.#", ".#####...", "#.#.#.#..", "...#.#..."],
    "tangle": ["..###....", ".#...#...", "#..#..#..", "#.#.#.#..", ".#.#.#...", "..#.#.#..", ".#.#..#.#", "#...###..", ".#.....#."],
    "firstcut": ["........#", ".......#.", "......#..", ".....#...", "....#....", "...#.....", "..#......", ".#.......", "#........"],
    "overweaver": ["........#", "......##.", ".....###.", "...####..", "..####...", ".####....", ".##......", "#........", "........."],
}


def mark_pixels(boss):
    strand, _ = BOSSES[boss]
    if strand:
        return glyph_pixels(strand, 1)
    return [(x, y) for y, row in enumerate(MARKS[boss]) for x, ch in enumerate(row) if ch == "#"]


def frayed_totem(boss):
    strand, accent = BOSSES[boss]
    im = blank(); a = ramp(accent)
    # carved post: head cap, plaque body, frayed cord skirt
    shape(im, lambda d, c: d.rectangle((10, 6, 21, 25), fill=c), WOOD)
    shape(im, lambda d, c: d.polygon(((8, 6), (16, 1), (23, 6), (23, 8), (8, 8)), fill=c), WOOD_LIGHT)
    d = draw(im); w = ramp(WOOD)
    d.point((16, 3), fill=a[3]); d.point((15, 4), fill=a[2]); d.point((17, 4), fill=a[2])   # eye on the cap
    d.rectangle((11, 10, 20, 20), fill=a[1]); d.rectangle((11, 10, 20, 10), fill=a[3]); d.rectangle((11, 10, 11, 20), fill=a[3])
    d.rectangle((12, 11, 20, 20), fill=mix(a[0], INK, 0.35))
    for dx, dy in mark_pixels(boss):
        im.putpixel((12 + dx, 11 + dy), a[4] if dy < 3 else a[3])
    for y in (22, 24):   # carved rings
        d.line((10, y, 21, y), fill=w[0])
    b = ramp(BONE)       # frayed cord skirt below the post, tied with a gold band
    d.rectangle((9, 25, 22, 26), fill=GOLD); d.line((9, 25, 22, 25), fill=BRASS_LIGHT)
    for i, x in enumerate(range(9, 23, 2)):
        ln = 3 + (i * 5) % 3
        d.line((x, 27, x + (i % 3 - 1), 27 + ln), fill=b[2] if i % 2 else a[2])
        d.point((x + (i % 3 - 1), 27 + ln), fill=b[1])
    return done(im, WOOD_DARK)


def build():
    out = {}
    for name, fn in RELICS.items():
        out[f"relic_{name}"] = fn()
    for boss in BOSSES:
        out[f"frayed_totem_{boss}"] = frayed_totem(boss)
    return out


def main():
    check = "--check" in sys.argv
    drift = []
    for name, im in sorted(build().items()):
        p = DEST / f"{name}.png"
        if check:
            if not p.exists() or Image.open(p).size != im.size or Image.open(p).convert("RGBA").tobytes() != im.tobytes():
                drift.append(name)
        else:
            save(im, p, quiet=True)
    if drift:
        sys.exit("Guardians item art drift: " + ", ".join(drift))
    print(("verified" if check else "wrote"), "26 Guardians item textures")


if __name__ == "__main__":
    main()
