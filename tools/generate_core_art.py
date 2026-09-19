#!/usr/bin/env python3
"""Source of truth for the 32x32 item and block textures of Ninjacat Skies Core: ninjacatskies, voidloom, clowderhall.

    python tools/generate_core_art.py            # write every texture
    python tools/generate_core_art.py --check    # exit 1 if a shipped PNG differs from what this script draws

Replaces the retired 16px generate_item_textures.py / generate_textures_loom.py. Tribal Power's overhaul_art.py
must not write into this repo; if it ever does, re-run this script to restore Core's art.
  * Kept sprites that were already on style are frozen pixel-for-pixel in art/core-kept-sprites.json.
  * Everything else is drawn here natively at 32px with tools/core_pixel.py (style: 1 px tinted outline,
    top-left light, 4-5 tone hue-shifted ramps, no AA/noise, alpha 0/255).
  * Strand tokens and Tension Post notches carry the canonical tribe glyphs from tools/art_tribe_glyphs.py.
Guardians items live in tools/generate_guardians_items.py; boss textures in tools/pixel_quantise_boss.py.
Models, blockstates and registry ids are not touched.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core_pixel import *  # noqa: E402,F403
from art_tribe_glyphs import TRIBES, TRIBE_COLORS, glyph_pixels  # noqa: E402

OUT: dict[str, Image.Image] = {}
EXTRA: dict[str, str] = {}   # non-PNG files (mcmeta)


def tex(mod, ns, rel):
    return f"mods/{mod}/src/main/resources/assets/{ns}/textures/{rel}.png"


def put(mod, rel, im, ns=None):
    OUT[tex(mod, ns or mod, rel)] = im


# ------------------------------------------------------------------ kept sprites (frozen)
def kept():
    data = json.loads((ROOT / "art/core-kept-sprites.json").read_text())
    for path, s in data["sprites"].items():
        pal = [tuple(bytes.fromhex(h)) for h in s["palette"]]
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        OUT[path] = from_rows(s["rows"], {chars[i]: c for i, c in enumerate(pal)})
    for mod in ("ninjacatskies", "voidloom"):
        EXTRA[tex(mod, mod, "block/loom_light") + ".mcmeta"] = '{\n  "animation": {\n    "frametime": 12,\n    "interpolate": true\n  }\n}'


# ------------------------------------------------------------------ strand tokens + notches
TOKEN_FRAME = [  # the copper-rimmed octagon coin (style reference); K ink, c copper dark, C copper light
    "................................", "................................",
    "........KKKKKKKKKKKKKKKK........", ".......KKKKKKKKKKKKKKKKKK.......",
    "......KKKCCCCCCCCCCCCCCKKK......", ".....KKKCccccccccccccccCKKK.....",
    "....KKKCccccccccccccccccCKKK....", "...KKKCKKKKKKKKKKKKKKKKKKCKKK...",
    "..KKKCcKKKKKKKKKKKKKKKKKKcCKKK..", "..KKCccKKKKKKKKKKKKKKKKKKccCKK..",
] + ["..KKCccKKKKKKKKKKKKKKKKKKccCKK.."] * 13 + [
    "..KKKCcKKKKKKKKKKKKKKKKKKcCKKK..", "...KKKCKKKKKKKKKKKKKKKKKKCKKK...",
    "....KKKCccccccccccccccccCKKK....", ".....KKKCccccccccccccccCKKK.....",
    "......KKKCCCCCCCCCCCCCCKKK......", ".......KKKKKKKKKKKKKKKKKK.......",
    "........KKKKKKKKKKKKKKKK........", "................................",
    "................................",
]
FRAME_PAL = {"K": INK, "c": (131, 75, 33), "C": (214, 179, 111)}


def glyph_bevel(im, pts, x0, y0, base, field=None):
    """Paint a scale-2 glyph: fill base, top/left stroke edges lit, bottom/right shaded, 1 px deep drop shadow."""
    r = ramp(base)
    s = set(pts)
    for dx, dy in pts:  # shadow first, only onto the field colour
        p = (x0 + dx + 1, y0 + dy + 1)
        if (dx + 1, dy + 1) not in s and (field is None or im.getpixel(p) == rgba(field)):
            im.putpixel(p, r[0])
    for dx, dy in pts:
        c = r[2]
        if (dx - 1, dy) not in s or (dx, dy - 1) not in s:
            c = r[3]
        if (dx + 1, dy) not in s and (dx, dy + 1) not in s:
            c = r[1]
        im.putpixel((x0 + dx, y0 + dy), c)


def tribe_glyph_colour(t):
    c = rgba(TRIBE_COLORS[t])
    return mix(c, WARM, 0.18)  # lift dark accents (soil, clock) a touch so they read on ink


def strand_tokens():
    for t in TRIBES:
        im = from_rows(TOKEN_FRAME, FRAME_PAL)
        glyph_bevel(im, glyph_pixels(t, 2), 7, 7, tribe_glyph_colour(t), field=INK)
        put("ninjacatskies", f"item/strand_token_{t}", im)


def notch(t):
    """Tension Post notch: a small opaque stud (the model maps the full texture on a 2x2x3 px cube)."""
    if t == "rewoven":
        base = BONE
    else:
        base = TRIBE_COLORS[t]
    r = ramp(base)
    im = blank(); d = draw(im)
    d.rectangle((0, 0, 31, 31), fill=outline_colour(base))
    d.rectangle((1, 1, 30, 30), fill=r[2])
    d.rectangle((1, 1, 30, 2), fill=r[3]); d.rectangle((1, 1, 2, 30), fill=r[3])
    d.rectangle((1, 29, 30, 30), fill=r[1]); d.rectangle((29, 1, 30, 30), fill=r[1])
    d.point((1, 1), fill=r[4]); d.point((2, 2), fill=r[4])
    if t == "rewoven":  # all strands re-knotted: a three-colour over-under weave instead of one glyph
        cols = [TRIBE_COLORS[x] for x in ("claw", "spindle", "sigil")]
        for i, c in enumerate(cols):
            rr = ramp(c)
            for k in range(3):
                y = 6 + k * 8 + i * 2
                for x in range(4, 28):
                    over = ((x // 4) + k + i) % 3 != 0
                    if over:
                        im.putpixel((x, y), rr[3]); im.putpixel((x, y + 1), rr[1])
        d.rectangle((13, 13, 18, 18), outline=INK, fill=BONE_LIGHT)
        d.rectangle((15, 15, 16, 16), fill=BRASS)
    else:
        pts = glyph_pixels(t, 2); s = set(pts)
        for dx, dy in pts:  # engraved glyph: dark cut, catch-light on the lower-right lip
            im.putpixel((7 + dx, 7 + dy), mix(r[0], INK, 0.3))
        for dx, dy in pts:
            if (dx + 1, dy + 1) not in s:
                im.putpixel((8 + dx, 8 + dy), r[4])
    put("ninjacatskies", f"block/notch_{t}", im)


def notches():
    for t in TRIBES + ["rewoven"]:
        notch(t)


# ------------------------------------------------------------------ small drawing helpers
def dot(im, x, y, c, w=2):
    for a in range(w):
        for b in range(w):
            xx, yy = int(round(x)) + a, int(round(y)) + b
            if 0 <= xx < 32 and 0 <= yy < 32:
                im.putpixel((xx, yy), rgba(c))


def curve(fn, n=240):
    return [fn(i / (n - 1)) for i in range(n)]


def cord(im, pts, r, w=2, glint_every=0):
    """A round cord along pts: base fill w px, top-left half lit, occasional warm glint."""
    for i, (x, y) in enumerate(pts):
        dot(im, x, y, r[2], w)
    for i, (x, y) in enumerate(pts):
        im.putpixel((int(round(x)), int(round(y))), r[3])
        if glint_every and i % glint_every == 0:
            im.putpixel((int(round(x)), int(round(y))), r[4])


def finish(im, base, diagonal=False):
    return outline(im, outline_colour(base), diagonal)


# ------------------------------------------------------------------ ninjacatskies items
def braid_cord():
    """Three strands (copper, loom teal, bone) plaited on a diagonal, brass-bound at both ends."""
    im = blank()
    a, b = (7.0, 24.0), (23.0, 8.0)
    L = math.dist(a, b); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = -uy, ux
    strands = [ramp(COPPER), ramp(LOOM), ramp(BONE)]
    edge = outline_colour(WOOD_DARK)
    for py in range(32):   # sample a chevron plait in (along u, across v) coordinates
        for px in range(32):
            rx, ry = px + 0.5 - a[0], py + 0.5 - a[1]
            u = rx * ux + ry * uy; v = rx * nx + ry * ny
            if not (1.5 <= u <= L - 1.5) or abs(v) > 3.3:
                continue
            q = (u - abs(v) * 0.9) / 3.6      # chevron bands, one strand per band on each side
            k = math.floor(q); f = q - k
            r = strands[(k + (v > 0)) % 3]
            c = edge if f < 0.18 else (r[3] if f < 0.45 else (r[2] if f < 0.8 else r[1]))
            if abs(v) > 2.6 and c != edge:
                c = r[1]
            im.putpixel((px, py), c)
    for (x, y) in (a, b):  # brass wraps
        d = draw(im); rb = ramp(BRASS)
        d.rectangle((x - 3, y - 3, x + 2, y + 2), fill=rb[2])
        d.line((x - 3, y - 3, x + 2, y - 3), fill=rb[4]); d.line((x - 3, y + 2, x + 2, y + 2), fill=rb[1])
        d.point((x - 1, y), fill=rb[1])
    rt = ramp(BONE)  # frayed tuft below the lower wrap
    for dx, dy in ((-4, 4), (-5, 6), (-3, 6), (-6, 7), (-2, 7)):
        im.putpixel((int(a[0] + dx), int(a[1] + dy)), rt[3 if dy < 6 else 2])
    return finish(im, WOOD_DARK)


def frayed_thread():
    """A single loose bone thread in an S-curve, both ends splitting into fibres."""
    im = blank(); r = ramp(BONE)
    pts = curve(lambda t: (6 + 20 * t + 4.5 * math.sin(t * 2 * math.pi * 1.5), 26 - 20 * t + 2.5 * math.cos(t * 2 * math.pi)))
    cord(im, pts[12:-12], r, 2)
    for (x, y), dirs in ((pts[12], ((-1, 1), (-1, 0), (0, 1))), (pts[-12], ((1, -1), (1, 0), (0, -1)))):
        for k, (dx, dy) in enumerate(dirs):
            for s in range(1, 5 - (k == 0)):
                im.putpixel((int(x + dx * s + (k == 2) * 0), int(y + dy * s)), r[3 if s < 3 else 1])
    for (x, y) in pts[40:200:40]:  # small snagged fibres along the thread
        im.putpixel((int(x) + 2, int(y) - 1), r[1])
    return finish(im, BONE_SHADE)


def codex_page():
    """A loose Codex page: torn left edge, dog-eared corner, teal and ink text lines, copper seal."""
    im = blank(); d = draw(im); r = ramp(BONE)
    d.rectangle((7, 4, 25, 28), fill=r[2])
    for y in range(4, 29):  # torn left edge
        if (y * 7) % 5 < 2:
            im.putpixel((7, y), CLEAR)
            if y % 3 == 0:
                im.putpixel((8, y), CLEAR)
    for (x, y) in ((25, 4), (24, 4), (23, 4), (25, 5), (24, 5), (25, 6)):
        im.putpixel((x, y), CLEAR)
    d.polygon(((22, 4), (22, 7), (25, 7)), fill=r[1])  # the folded-over corner
    d.line((22, 4, 25, 7), fill=r[0])
    d.line((9, 5, 21, 5), fill=r[3]); d.line((9, 5, 9, 27), fill=r[3])
    d.line((9, 28, 25, 28), fill=r[1]); d.line((25, 8, 25, 28), fill=r[1])
    t = ramp(LOOM)
    d.line((11, 9, 19, 9), fill=t[1])
    for i, y in enumerate(range(12, 23, 2)):
        d.line((11, y, 23 - (i * 3) % 7, y), fill=mix(INK, BONE, 0.35))
    c = ramp(COPPER)
    d.ellipse((17, 22, 22, 27), fill=c[2]); d.point((18, 23), fill=c[4]); d.point((21, 26), fill=c[0])
    d.point((19, 24), fill=c[1]); d.point((20, 25), fill=c[1])
    return finish(im, BONE_SHADE)


def spindle_loom_fragment():
    """A snapped length of loom spindle: wooden shaft, copper whorl, teal thread still wound, splintered end."""
    im = blank(); d = draw(im)
    w = ramp(WOOD_LIGHT)
    shaft = curve(lambda t: (5 + 20 * t, 27 - 20 * t), 60)
    cord(im, shaft, w, 3)
    for i, (x, y) in enumerate(shaft):  # grain
        if i % 9 == 4:
            im.putpixel((int(x) + 2, int(y)), w[1])
    x, y = 25, 7  # splintered break
    for dx, dy, c in ((1, -2, w[3]), (2, -1, w[2]), (0, -3, w[3]), (3, 0, w[1]), (2, -3, w[2])):
        im.putpixel((x + dx, y + dy), c)
    c = ramp(COPPER)  # whorl disc, seen edge-on at an angle
    d.polygon(((6, 18), (12, 16), (16, 20), (10, 22)), fill=c[2])
    d.line((6, 18, 12, 16), fill=c[4]); d.line((10, 22, 16, 20), fill=c[0]); d.point((11, 18), fill=c[3])
    t = ramp(LOOM)
    for k in range(4):  # thread wound above the whorl
        cx, cy = 14 + k * 2, 17 - k * 2
        d.line((cx - 2, cy - 1, cx + 1, cy + 2), fill=t[3 if k % 2 else 2])
    pts = curve(lambda s: (22 + 6 * s, 14 + 5 * math.sin(s * 3.1)), 30)  # loose end
    for (px, py) in pts:
        im.putpixel((int(px), int(py)), t[2])
    return finish(im, WOOD_DARK)


# ------------------------------------------------------------------ voidloom items
VOID = (0x4a, 0x3f, 0x7a, 255)   # void-yarn violet


def void_yarn():
    """A ball of void-spun yarn: violet wraps with teal glints and a loose tail."""
    im = blank(); d = draw(im); r = ramp(VOID); t = ramp(LOOM)
    d.ellipse((4, 5, 25, 26), fill=r[2])
    for k, (off, c) in enumerate(((-6, r[3]), (-1, r[3]), (4, r[1]), (9, r[1]))):  # wrap bands
        d.arc((4 + off, 5 - 2, 25 + off, 26 + 2), 110, 250, fill=c)
    d.arc((3, 9, 26, 22), 190, 350, fill=r[3]); d.arc((3, 11, 26, 24), 10, 170, fill=r[0])
    for (x, y) in ((9, 9), (12, 8), (16, 12), (10, 15), (19, 18)):
        d.point((x, y), fill=t[3])
    d.point((8, 8), fill=r[4]); d.point((9, 8), fill=r[4])
    d.arc((4, 5, 25, 26), 20, 110, fill=r[0])
    ball = blank(); draw(ball).ellipse((4, 5, 25, 26), fill=INK)
    for y in range(32):  # wrap arcs stay on the ball
        for x in range(32):
            if ball.getpixel((x, y))[3] == 0:
                im.putpixel((x, y), CLEAR)
    tail = curve(lambda s: (22 + 7 * s, 22 + 5 * s + 2 * math.sin(s * 6)), 40)
    for (x, y) in tail:
        im.putpixel((min(30, int(x)), min(30, int(y))), t[2])
    return finish(im, VOID)


def binding_knot():
    """A tied copper-cord binding knot: two interlocked loops with trailing ends."""
    im = blank(); d = draw(im); r = ramp(COPPER)
    for box in ((4, 7, 18, 21), (13, 7, 27, 21)):
        d.ellipse(box, outline=r[2], width=3)
    d.arc((4, 7, 18, 21), 180, 270, fill=r[3], width=1); d.arc((13, 7, 27, 21), 180, 270, fill=r[3], width=1)
    d.arc((4, 7, 18, 21), 0, 90, fill=r[1], width=1); d.arc((13, 7, 27, 21), 0, 90, fill=r[1], width=1)
    # over-crossing in the middle drawn on top so the knot reads as tied
    d.rectangle((14, 8, 17, 11), fill=r[2]); d.line((14, 8, 17, 8), fill=r[4])
    d.rectangle((14, 17, 17, 20), fill=r[1])
    d.line((13, 21, 9, 29), fill=r[2], width=3); d.line((18, 21, 22, 29), fill=r[2], width=3)
    d.line((12, 22, 9, 28), fill=r[3]); d.line((19, 22, 22, 28), fill=r[1])
    b = ramp(BRASS)
    for x in (9, 22):
        d.rectangle((x - 1, 27, x + 1, 29), fill=b[2]); d.point((x - 1, 27), fill=b[4])
    return finish(im, COPPER_DARK)


def loom_lint():
    """A fluffy tuft of loom lint: pale clumped fibre with stray hairs and a few teal flecks."""
    im = blank(); d = draw(im); r = ramp(BONE); t = ramp(LOOM)
    for (x, y, rr) in ((12, 17, 7), (19, 14, 6), (20, 21, 5), (9, 22, 4), (15, 11, 4)):
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=r[2])
    lit(im, r[2], r)
    for (x, y) in ((10, 13), (16, 9), (21, 11), (8, 18)):
        d.point((x, y), fill=r[4])
    for (x, y) in ((14, 18), (19, 17), (11, 22), (22, 22)):
        d.point((x, y), fill=r[1])
    for (x, y) in ((16, 16), (12, 20), (20, 13)):
        d.point((x, y), fill=t[2])
    for (x0, y0, x1, y1) in ((4, 14, 7, 16), (25, 9, 23, 12), (26, 24, 24, 22), (7, 27, 9, 25), (15, 4, 15, 7)):
        d.line((x0, y0, x1, y1), fill=r[3])
    return finish(im, BONE_SHADE)


def strand_filament():
    """A single loose Strand filament: a thin bright teal line in a loose loop, beaded with light."""
    im = blank(); t = ramp(LOOM)
    pts = curve(lambda s: (5 + 22 * s + 6 * math.sin(s * 2 * math.pi), 27 - 22 * s - 6 * math.sin(s * 2 * math.pi) * 0.6
                           + 4 * math.sin(s * math.pi * 3)), 400)
    for (x, y) in pts:
        dot(im, x, y, t[1], 2)
    for (x, y) in pts:
        im.putpixel((int(round(x)), int(round(y))), t[3])
    for i in (60, 150, 240, 330):  # beads of light
        x, y = int(round(pts[i][0])), int(round(pts[i][1]))
        dot(im, x - 1, y - 1, t[3], 3); im.putpixel((x, y), t[4]); im.putpixel((x - 1, y - 1), BONE_LIGHT)
    return finish(im, LOOM_DEEP)


MESH = {  # frame shape, frame ramp base, cord ramp base, grid step, cord width
    "string": ("hoop", WOOD_LIGHT, BONE, 4, 2),
    "flint": ("lashed", STONE_LIGHT, (0x5b, 0x5e, 0x63, 255), 5, 2),
    "iron": ("riveted", (0x8a, 0x93, 0x9b, 255), (0xb4, 0xbc, 0xc2, 255), 3, 1),
}


def mesh_grid(im, box, cord_base, step, w):
    """Over-under weave inside box (x0, y0, x1, y1)."""
    r = ramp(cord_base); x0, y0, x1, y1 = box
    for gx in range(x0 + 1, x1, step):
        for y in range(y0, y1 + 1):
            for k in range(w):
                im.putpixel((gx + k, y), r[3] if k == 0 else r[2])
    for gy in range(y0 + 1, y1, step):
        for x in range(x0, x1 + 1):
            over = ((x - x0) // step) % 2 == ((gy - y0) // step) % 2
            onv = any(x == gx + k for gx in range(x0 + 1, x1, step) for k in range(w))
            if onv and not over:
                continue
            for k in range(w):
                im.putpixel((x, gy + k), r[2] if k == 0 else r[1])
    return r


def thread_mesh(kind):
    shape, fb, cb, step, w = MESH[kind]
    im = blank(); d = draw(im); f = ramp(fb)
    if shape == "hoop":   # embroidery hoop: round wooden ring with a brass screw
        mesh_grid(im, (6, 6, 25, 25), cb, step, w)
        mask = blank(); draw(mask).ellipse((6, 6, 25, 25), fill=INK)
        for y in range(32):
            for x in range(32):
                if mask.getpixel((x, y))[3] == 0:
                    im.putpixel((x, y), CLEAR)
        d.ellipse((3, 3, 28, 28), outline=f[2], width=3)
        d.arc((3, 3, 28, 28), 150, 300, fill=f[3]); d.arc((5, 5, 26, 26), 330, 120, fill=f[1])
        b = ramp(BRASS); d.rectangle((14, 0, 17, 3), fill=b[2]); d.point((14, 0), fill=b[4]); d.point((17, 3), fill=b[0])
    elif shape == "lashed":   # square stone-grey frame, cords lashed at each corner, flint chips on the weave
        d.rectangle((3, 3, 28, 28), fill=f[2]); d.rectangle((6, 6, 25, 25), fill=CLEAR)
        d.line((3, 3, 28, 3), fill=f[3]); d.line((3, 3, 3, 28), fill=f[3]); d.line((4, 28, 28, 28), fill=f[1]); d.line((28, 4, 28, 28), fill=f[1])
        mesh_grid(im, (6, 6, 25, 25), cb, step, w)
        l = ramp(WOOD_LIGHT)
        for (x, y) in ((3, 3), (25, 3), (3, 25), (25, 25)):
            d.line((x, y + 1, x + 3, y + 3), fill=l[2]); d.line((x, y + 3, x + 3, y), fill=l[3])
        fl = ramp((0x3a, 0x3d, 0x44, 255))
        for (x, y) in ((11, 12), (17, 17), (12, 21), (21, 10)):
            d.polygon(((x, y - 2), (x + 2, y + 1), (x - 1, y + 1)), fill=fl[1]); d.point((x, y - 1), fill=fl[4])
    else:   # riveted iron frame, fine wire grid
        d.rectangle((3, 3, 28, 28), fill=f[2]); d.rectangle((6, 6, 25, 25), fill=CLEAR)
        d.line((3, 3, 28, 3), fill=f[4]); d.line((3, 3, 3, 28), fill=f[3]); d.line((4, 28, 28, 28), fill=f[0]); d.line((28, 4, 28, 28), fill=f[1])
        d.line((6, 6, 25, 6), fill=f[0]); d.line((6, 6, 6, 25), fill=f[0])
        mesh_grid(im, (7, 7, 25, 25), cb, step, w)
        for (x, y) in ((4, 4), (26, 4), (4, 26), (26, 26), (15, 4), (15, 26), (4, 15), (26, 15)):
            d.rectangle((x, y, x + 1, y + 1), fill=f[0]); d.point((x, y), fill=f[4])
    return finish(im, fb)


def sieve_mesh(kind):
    """item/mesh/<id>: the square Ex Deorum draws across a sieve (whole face is the weave, holes clear)."""
    shape, fb, cb, step, w = MESH[kind]
    im = blank(); d = draw(im)
    mesh_grid(im, (0, 0, 31, 31), cb, step, w)
    f = ramp(fb); d.rectangle((0, 0, 31, 31), outline=f[1])
    return im


# ------------------------------------------------------------------ blocks
def planks_v(im, box, base, width=4):
    """Vertical staves/planks with seams and a little grain, lit from the top-left."""
    r = ramp(base); x0, y0, x1, y1 = box; d = draw(im)
    for i, x in enumerate(range(x0, x1 + 1, width)):
        c = r[2] if i % 2 == 0 else mix(r[2], r[1], 0.5)
        d.rectangle((x, y0, min(x + width - 1, x1), y1), fill=c)
        d.line((x, y0, x, y1), fill=r[3])
        if x + width - 1 <= x1:
            d.line((x + width - 1, y0, x + width - 1, y1), fill=r[0])
        for gy in range(y0 + 3 + (i * 5) % 7, y1, 9):
            d.line((x + 1 + i % 2, gy, x + 1 + i % 2, gy + 2), fill=r[1])


def tension_post_side():
    """Post column (u 10..21) of dark wood wound with a teal tension cord; rows 0..3 are the copper cap band."""
    im = blank(); d = draw(im)
    planks_v(im, (0, 0, 31, 31), WOOD, 4)
    w = ramp(WOOD)
    d.rectangle((10, 4, 21, 31), fill=w[1])
    d.line((10, 4, 10, 31), fill=w[3]); d.line((21, 4, 21, 31), fill=w[0])
    for gy in (7, 16, 25):
        d.line((13, gy, 13, gy + 4), fill=w[0]); d.line((17, gy + 3, 17, gy + 6), fill=w[2])
    t = ramp(LOOM)
    for y0 in range(8, 30, 7):  # cord wraps round the post, diagonal on the face
        for k in range(12):
            y = y0 + k // 3
            if y < 31:
                im.putpixel((10 + k, y), t[3] if k < 4 else t[2]); im.putpixel((10 + k, y + 1), t[0])
    c = ramp(COPPER)
    d.rectangle((0, 0, 31, 3), fill=c[2]); d.line((0, 0, 31, 0), fill=c[4]); d.line((0, 3, 31, 3), fill=INK)
    for x in range(3, 31, 6):
        d.point((x, 1), fill=c[0]); d.point((x, 2), fill=c[1])
    return im


def tension_post_top():
    """Cap plan view (texels 6..26): copper-rimmed wooden cap with a brass tension ring and a cord cross."""
    im = blank(); d = draw(im)
    planks_v(im, (0, 0, 31, 31), WOOD, 4)
    c = ramp(COPPER); w = ramp(WOOD_LIGHT); b = ramp(BRASS); t = ramp(LOOM)
    d.rectangle((6, 6, 25, 25), fill=c[2]); d.line((6, 6, 25, 6), fill=c[4]); d.line((6, 6, 6, 25), fill=c[3])
    d.line((6, 25, 25, 25), fill=c[0]); d.line((25, 6, 25, 25), fill=c[0])
    d.rectangle((8, 8, 23, 23), fill=w[2])
    for y in range(9, 23, 3):
        d.line((9, y, 22, y), fill=w[1])
    d.line((8, 8, 23, 8), fill=w[0]); d.line((8, 8, 8, 23), fill=w[0])
    d.line((15, 8, 15, 23), fill=t[2]); d.line((16, 8, 16, 23), fill=t[1])
    d.line((8, 15, 23, 15), fill=t[3]); d.line((8, 16, 23, 16), fill=t[1])
    d.ellipse((12, 12, 19, 19), outline=b[2], width=2); d.arc((12, 12, 19, 19), 180, 270, fill=b[4])
    d.rectangle((15, 15, 16, 16), fill=t[4])
    for (x, y) in ((7, 7), (24, 7), (7, 24), (24, 24)):
        d.point((x, y), fill=INK)
    return im


def tension_barrel_side():
    """Barrel staves (visible rows 6..28, hooped by the model's copper trim) with a coil of loom thread wound round."""
    im = blank(); d = draw(im)
    planks_v(im, (0, 0, 31, 31), WOOD_LIGHT, 4)
    t = ramp(LOOM)
    for y in range(12, 21, 2):   # wound coil band
        d.line((0, y, 31, y), fill=t[2]); d.line((0, y + 1, 31, y + 1), fill=t[1])
        for x in range((y // 2) % 4, 32, 4):
            d.point((x, y), fill=t[3])
    d.line((0, 11, 31, 11), fill=INK); d.line((0, 22, 31, 22), fill=mix(INK, WOOD, 0.4))
    for x in (7, 21):
        d.point((x, 12), fill=t[4])
    return im


def tension_barrel_top():
    """Lid plan view (texels 4..28): planked lid, copper rim, a glowing loom-light bung in the middle."""
    im = blank(); d = draw(im); w = ramp(WOOD_LIGHT); c = ramp(COPPER); t = ramp(LOOM)
    d.rectangle((0, 0, 31, 31), fill=w[2])
    for y in range(4, 29, 4):
        d.line((4, y, 27, y), fill=w[0]); d.line((4, y + 1, 27, y + 1), fill=w[3])
    d.rectangle((2, 2, 29, 4), fill=c[2]); d.line((2, 2, 29, 2), fill=c[4])
    d.rectangle((2, 27, 29, 29), fill=c[1]); d.rectangle((2, 2, 4, 29), fill=c[2]); d.rectangle((27, 2, 29, 29), fill=c[1])
    d.line((2, 2, 2, 29), fill=c[3])
    d.ellipse((11, 11, 20, 20), fill=INK)
    d.ellipse((12, 12, 19, 19), fill=t[1]); d.ellipse((13, 13, 18, 18), fill=t[2])
    d.rectangle((14, 14, 15, 15), fill=t[4]); d.point((17, 17), fill=t[0])
    return im


def loomframe_top():
    """Plan view of the stretched mesh (texels 4..28) in its copper-trimmed frame; rows 4..6 show on the sides."""
    im = blank(); d = draw(im); c = ramp(COPPER); s = ramp(STONE_DARK)
    d.rectangle((0, 0, 31, 31), fill=s[2])
    d.rectangle((4, 4, 27, 27), fill=c[2]); d.line((4, 4, 27, 4), fill=c[4]); d.line((4, 4, 4, 27), fill=c[3])
    d.line((4, 27, 27, 27), fill=c[0]); d.line((27, 4, 27, 27), fill=c[0])
    d.rectangle((7, 7, 24, 24), fill=INK)
    mesh_grid(im, (7, 7, 24, 24), BONE, 3, 1)
    for (x, y) in ((5, 5), (26, 5), (5, 26), (26, 26)):
        d.point((x, y), fill=INK)
    return im


# ------------------------------------------------------------------ build
def build():
    kept()
    strand_tokens()
    notches()
    put("ninjacatskies", "item/braid_cord", braid_cord())
    put("ninjacatskies", "item/frayed_thread", frayed_thread())
    put("ninjacatskies", "item/codex_page", codex_page())
    put("ninjacatskies", "item/spindle_loom_fragment", spindle_loom_fragment())
    put("ninjacatskies", "block/tension_post", tension_post_side())
    put("ninjacatskies", "block/tension_post_top", tension_post_top())
    put("voidloom", "item/void_yarn", void_yarn())
    put("voidloom", "item/binding_knot", binding_knot())
    put("voidloom", "item/loom_lint", loom_lint())
    put("voidloom", "item/strand_filament", strand_filament())
    for k in MESH:
        put("voidloom", f"item/thread_mesh_{k}", thread_mesh(k))
        put("voidloom", f"item/mesh/thread_mesh_{k}", sieve_mesh(k))
    put("voidloom", "block/tension_barrel", tension_barrel_side())
    put("voidloom", "block/tension_barrel_top", tension_barrel_top())
    put("voidloom", "block/loomframe_top", loomframe_top())


def main():
    check = "--check" in sys.argv
    build()
    drift = []
    for rel, im in sorted(OUT.items()):
        p = ROOT / rel
        if check:
            if not p.exists() or Image.open(p).convert("RGBA").tobytes() != im.tobytes() or Image.open(p).size != im.size:
                drift.append(rel)
        else:
            save(im, p)
    for rel, text in EXTRA.items():
        p = ROOT / rel
        if check:
            if not p.exists() or p.read_text().strip() != text.strip():
                drift.append(rel)
        else:
            p.write_text(text + "\n")
    if drift:
        sys.exit("Core art drift (re-run tools/generate_core_art.py):\n" + "\n".join(drift))
    print(f"{'verified' if check else 'wrote'} {len(OUT)} textures")


if __name__ == "__main__":
    main()
