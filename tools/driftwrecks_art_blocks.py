"""Driftwrecks blocks at 32x32: tileable faces with top-left light and 4-5 tone ramps, drawn for their model UVs.

UV notes (16-unit model space x2 = texels):
  wreck_chest     element [1,0,1]-[15,14,15]: north face shows cols 2..29 x rows 4..31; top cols/rows 2..29.
  thread_pillar   element [3,0,3]-[13,16,13]: sides show cols 6..25; ends cols/rows 6..25.
  thread_idol     body [5,3,5]-[11,13,11] shows side cols 10..21 x rows 6..25; base/cap faces use the top texture.
  trophy_plinth   body [2,3,2]-[14,10,14] shows side cols 4..27 x rows 12..25.
  salvagers_frame warp plane [3,5]-[13,12] shows cols 6..25 x rows 8..21.
  tribe_banner    cloth plane [1,0]-[15,15] shows cols 2..29 x rows 2..31 (rows 0..1: the item icon's rod).
"""
from __future__ import annotations

import math

from art_tribe_glyphs import TRIBE_COLORS
from driftwrecks_art_lib import (BONE, DRIFT, GOLD, INK, IRON, LOOM, RIFT, SLATE, TEAL, WOOD, Px, ellipse_cells,
                                 poly_cells, ramp, rect_cells, ring_cells)

CHEST_WOOD = ramp((0x5e, 0x44, 0x34))
CRATE_WOOD = ramp((0x9a, 0x74, 0x4c))
STONE = ramp((0x5a, 0x66, 0x74))
MARBLE = ramp((0xb8, 0xb0, 0x9c))
VOID = ramp((0x24, 0x20, 0x30))


# ------------------------------------------------------------------ materials

def planks(g, R, h=8, x0=0, y0=0, x1=31, y1=31, offset=0, nails=True):
    """Horizontal planks h px tall: light top edge, dark seam, sparse grain, staggered butt joints."""
    for y in range(y0, y1 + 1):
        k = (y - y0) % h
        for x in range(x0, x1 + 1):
            c = R.base
            if k == 0:
                c = R.light
            elif k == h - 1:
                c = R.deep
            g.p(x, y, c)
    row = 0
    for yy in range(y0, y1 + 1, h):
        seed = (row * 7 + offset) % 5
        for (gx, gl) in ((3 + seed * 3, 6), (17 + seed * 2, 5)):
            g.line(x0 + gx % (x1 - x0 + 1), yy + 3, min(x1, x0 + gx % (x1 - x0 + 1) + gl), yy + 3, R.dark)
        g.line(x0 + (9 + seed * 4) % 28, yy + 5, min(x1, x0 + (9 + seed * 4) % 28 + 4), yy + 5, R.light)
        j = x0 + (row * 13 + offset) % (x1 - x0 + 1)
        g.line(j, yy + 1, j, min(y1, yy + h - 2), R.deep)
        if nails:
            g.p(j + 2, yy + 2, IRON.light); g.p(j - 2, yy + h - 3, IRON.dark)
        row += 1


def iron_band(g, y0, y1, x0=0, x1=31, rivets=(4, 27)):
    g.rect(x0, y0, x1, y1, IRON.base)
    g.line(x0, y0, x1, y0, IRON.light); g.line(x0, y1, x1, y1, IRON.deep)
    for x in rivets:
        g.p(x, y0 + 1, IRON.hi); g.p(x + 1, y0 + 1, IRON.dark)


def thread_seam(g, x0, y, x1):
    """A teal thread seam with gold stitches crossing it."""
    g.line(x0, y, x1, y, TEAL.base); g.line(x0, y + 1, x1, y + 1, TEAL.dark)
    for x in range(x0 + 1, x1, 4):
        g.p(x, y - 1, GOLD.light); g.p(x + 1, y + 2, GOLD.dark)


def bricks(g, R, bw=16, bh=8, x0=0, y0=0, x1=31, y1=31):
    for y in range(y0, y1 + 1):
        row = (y - y0) // bh
        k = (y - y0) % bh
        for x in range(x0, x1 + 1):
            kx = (x - x0 + (bw // 2 if row % 2 else 0)) % bw
            c = R.base
            if k == 0 or kx == 0:
                c = R.light
            if k == bh - 1 or kx == bw - 1:
                c = R.deep
            elif k == bh - 2 or kx == bw - 2:
                c = R.dark if c == R.base else c
            g.p(x, y, c)


# ------------------------------------------------------------------ tether thread

def tether_thread():
    """Basket-woven tether: 8 px teal cords over and under, a gold seam thread every half block."""
    g = Px()
    for y in range(32):
        for x in range(32):
            cx, cy = x // 8, y // 8
            horiz = (cx + cy) % 2 == 0
            k = (y % 8) if horiz else (x % 8)
            lane = k // 4                      # two cords per weave cell
            kk = k % 4
            c = TEAL.light if kk == 0 else TEAL.base if kk < 3 else TEAL.dark
            along = (x % 8) if horiz else (y % 8)
            if along in (0, 7):
                c = TEAL.deep
            if lane == 1 and kk == 1 and (cx + cy) % 4 == 0:
                c = GOLD.base
            g.p(x, y, c)
    return g


def tether_thread_side():
    """Slab edge: the cut ends of the woven mat, top and bottom of each half; the rest is open."""
    g = Px()
    for top in (0, 16):
        for x in range(32):
            k = x % 4
            g.p(x, top, TEAL.light if k < 3 else TEAL.dark)
            g.p(x, top + 1, TEAL.base if k < 3 else TEAL.deep)
            g.p(x, top + 2, TEAL.dark if k < 3 else TEAL.deep)
        for x in range(0, 32, 8):
            g.p(x + 5, top + 1, GOLD.base)
        for x in range(32):
            g.p(x, top + 14, TEAL.base if x % 4 else TEAL.dark); g.p(x, top + 15, TEAL.deep)
    return g


# ------------------------------------------------------------------ wreck chest

def wreck_chest(face):
    g = Px()
    if face == "top":
        planks(g, CHEST_WOOD, offset=3)
        for x0 in (6, 25):
            g.rect(x0, 0, x0 + 1, 31, IRON.base); g.line(x0, 0, x0, 31, IRON.light)
            for y in (4, 20):
                g.p(x0, y, IRON.hi)
        thread_seam(g, 0, 15, 31)
        return g
    planks(g, CHEST_WOOD, offset=1 if face == "side" else 5)
    iron_band(g, 4, 6)
    iron_band(g, 28, 30)
    g.rect(0, 13, 31, 13, CHEST_WOOD.deep)
    thread_seam(g, 0, 11, 31)
    if face == "front":
        g.fill(rect_cells(13, 10, 18, 18), GOLD)
        g.rect(15, 13, 16, 15, INK); g.p(15, 16, INK)
        g.p(14, 11, GOLD.hi)
    # a frayed scar where it tore from its island
    g.line(3, 25, 8, 20, LOOM.base); g.line(4, 25, 9, 20, TEAL.dark)
    return g


# ------------------------------------------------------------------ frayed spawner

def frayed_spawner():
    """A cage of iron bars round a void, frayed threads tangled inside."""
    g = Px()
    g.rect(0, 0, 31, 31, VOID.base)
    for (x0, y0, x1, y1, c) in [(6, 26, 13, 15, LOOM.base), (13, 15, 11, 9, LOOM.light), (11, 9, 22, 5, GOLD.base),
                                (16, 18, 25, 24, TEAL.base), (20, 11, 26, 16, LOOM.dark)]:
        g.line(x0, y0, x1, y1, c)
    for (x, y) in [(9, 12), (22, 20), (18, 8)]:
        g.p(x, y, VOID.light)
    for v in range(0, 32, 8):
        for t in range(32):
            for (x, y) in ((v, t), (t, v)):
                g.p(x, y, IRON.dark)
            g.p(v + 1, t, IRON.base); g.p(t, v + 1, IRON.base)
            g.p(v + 1, t, IRON.light if t % 8 in (2, 3) else IRON.base)
    for v in range(0, 32, 8):
        for w in range(0, 32, 8):
            g.rect(v, w, v + 1, w + 1, IRON.light); g.p(v + 1, w + 1, IRON.deep)
    return g


# ------------------------------------------------------------------ thread pillar

def thread_pillar(lit):
    """Slate drums with a thread wound round them; lit: the thread glows and the core channel shows."""
    g = Px()
    bricks(g, STONE, bw=32, bh=16)
    th = (LOOM.light, LOOM.base, LOOM.hi) if lit else (TEAL.dark, TEAL.deep, TEAL.base)
    if lit:
        g.rect(13, 0, 18, 31, LOOM.base); g.rect(14, 0, 17, 31, LOOM.light); g.rect(15, 0, 16, 31, LOOM.hi)
    else:
        g.rect(13, 0, 18, 31, STONE.deep); g.rect(14, 0, 14, 31, VOID.base)
    for y0 in range(-8, 32, 8):
        for x in range(32):
            y = y0 + x // 4
            if 0 <= y < 32:
                g.p(x, y, th[0]); g.p(x, y + 1, th[1])
        if lit and 0 <= y0 + 2 < 32:
            g.p(8, y0 + 2, th[2])
    return g


def thread_pillar_top():
    g = Px()
    bricks(g, STONE, bw=16, bh=16)
    g.fill(ring_cells(15.5, 15.5, 9.5, 6.5), SLATE)
    g.pts(ring_cells(15.5, 15.5, 8, 7), TEAL.base)
    g.fill(ellipse_cells(15.5, 15.5, 5), GOLD, rim=True)
    g.fill(ellipse_cells(15.5, 15.5, 2.2), VOID)
    return g


# ------------------------------------------------------------------ thread idol

def thread_idol():
    """A driftwood cat idol (cols 10..21, rows 6..25), bound in teal thread; plain wood elsewhere."""
    g = Px()
    for x in range(32):
        for y in range(32):
            g.p(x, y, DRIFT.base if (x + y // 3) % 7 else DRIFT.dark)
    # ears and head
    g.fill(poly_cells([(10, 6), (13, 6), (12, 9)]), WOOD); g.fill(poly_cells([(18, 6), (21, 6), (19, 9)]), WOOD)
    g.fill(rect_cells(10, 8, 21, 15), WOOD)
    g.rect(12, 11, 13, 12, LOOM.light); g.rect(18, 11, 19, 12, LOOM.light)
    g.p(12, 11, LOOM.hi); g.p(18, 11, LOOM.hi)
    g.p(15, 13, WOOD.deep); g.p(16, 13, WOOD.deep); g.line(14, 14, 17, 14, WOOD.dark)
    # bound body
    g.fill(rect_cells(10, 16, 21, 25), WOOD)
    for y in range(17, 25, 2):
        g.line(10, y, 21, y + 1, TEAL.base)
        if y < 23:
            g.line(10, y + 1, 21, y + 2, TEAL.dark)
    g.line(10, 20, 21, 20, GOLD.base)
    return g


def thread_idol_top():
    g = Px()
    for x in range(32):
        for y in range(32):
            g.p(x, y, WOOD.base if (x + y // 3) % 7 else WOOD.dark)
    for y0 in (2, 26):
        g.rect(0, y0, 31, y0 + 3, WOOD.dark); g.line(0, y0, 31, y0, WOOD.light)
    g.pts(ring_cells(15.5, 15.5, 7.5, 5.5), TEAL.base)
    g.pts(ring_cells(15.5, 15.5, 7.5, 6.5), TEAL.light)
    g.fill(ellipse_cells(15.5, 15.5, 3), GOLD)
    return g


# ------------------------------------------------------------------ thread lock

def thread_lock():
    """A lattice of teal and gold thread; open diamonds between (hard alpha)."""
    g = Px()
    for y in range(32):
        for x in range(32):
            a, b = (x + y) % 16, (x - y) % 16
            if a in (0, 1) or b in (0, 1):
                gold = (x // 16 + y // 16) % 2 == 0
                R = GOLD if (a in (0, 1) and gold) else TEAL
                g.p(x, y, R.light if (a == 0 or b == 0) else R.dark)
    for (x, y) in [(0, 0), (8, 8), (16, 0), (0, 16), (16, 16), (24, 8), (8, 24), (24, 24)]:
        g.fill(ellipse_cells(x + 0.5, y + 0.5, 2), GOLD)
    return g


# ------------------------------------------------------------------ rift tear

def rift_tear():
    """A jagged vertical tear in the sky: violet bands, teal thread-light at its lips."""
    g = Px()
    for y in range(32):
        w = 2 + 5 * math.sin((y + 0.5) / 32 * math.pi)
        cx = 15.5 + 2.2 * math.sin(y * 0.55) + (1 if y % 5 == 0 else 0)
        for x in range(32):
            d = abs(x + 0.5 - cx)
            if d < w:
                t = d / w
                c = RIFT.hi if t < 0.2 else RIFT.light if t < 0.45 else RIFT.base if t < 0.7 else RIFT.dark if t < 0.86 else LOOM.base
                g.p(x, y, c)
    for y in (6, 13, 21):
        g.p(round(15.5 + 2.2 * math.sin(y * 0.55)), y, LOOM.hi)
    return g


# ------------------------------------------------------------------ salvage crate

def _crate_frame(g):
    """Light frame boards round the face with iron corner plates."""
    for (x0, y0, x1, y1) in ((0, 0, 31, 3), (0, 28, 31, 31), (0, 0, 3, 31), (28, 0, 31, 31)):
        g.rect(x0, y0, x1, y1, CRATE_WOOD.light)
    g.line(0, 0, 31, 0, CRATE_WOOD.hi); g.line(0, 0, 0, 31, CRATE_WOOD.hi)
    g.line(4, 4, 27, 4, CRATE_WOOD.deep); g.line(4, 4, 4, 27, CRATE_WOOD.deep)
    g.line(3, 28, 28, 28, CRATE_WOOD.dark); g.line(28, 3, 28, 28, CRATE_WOOD.dark)
    g.line(0, 31, 31, 31, CRATE_WOOD.deep); g.line(31, 0, 31, 31, CRATE_WOOD.deep)
    for (x, y) in ((0, 0), (27, 0), (0, 27), (27, 27)):
        g.rect(x, y, x + 4, y + 4, IRON.base)
        g.line(x, y, x + 4, y, IRON.light); g.line(x, y, x, y + 4, IRON.light)
        g.p(x + 2, y + 2, IRON.hi)


def salvage_crate_side():
    """Crate side: frame, planks, a diagonal brace, a teal rope lashed round."""
    g = Px()
    planks(g, CRATE_WOOD, h=8, offset=2, nails=False)
    for i in range(24):
        x, y = 4 + i, 27 - i
        g.p(x, y, CRATE_WOOD.light); g.p(x + 1, y, CRATE_WOOD.base); g.p(x + 2, y, CRATE_WOOD.dark)
    _crate_frame(g)
    for y in (14, 15, 16):
        for x in range(32):
            g.p(x, y, TEAL.light if y == 14 else TEAL.base if y == 15 else TEAL.dark)
    for x in range(2, 32, 5):
        g.p(x, 15, TEAL.deep)
    return g


def salvage_crate_top():
    """Crate lid: frame, planks, a gold seam-knot where the teal rope crosses."""
    g = Px()
    planks(g, CRATE_WOOD, h=8, offset=4, nails=False)
    _crate_frame(g)
    for i in range(6, 26):
        g.p(i, i, CRATE_WOOD.dark); g.p(31 - i, i, CRATE_WOOD.dark)
    for x in range(32):
        g.p(x, 15, TEAL.light if (x // 2) % 2 else TEAL.base); g.p(x, 16, TEAL.dark)
    g.fill(ellipse_cells(16, 16, 3.5), GOLD)
    g.p(14, 14, GOLD.hi)
    return g


# ------------------------------------------------------------------ salvager's frame

def salvagers_frame_wood():
    """Frame beams: driftwood with vertical grain, lighter at the top-left."""
    g = Px()
    for x in range(32):
        k = x % 4
        for y in range(32):
            c = WOOD.light if k == 0 else WOOD.base if k < 3 else WOOD.dark
            if (x * 7 + y // 5) % 11 == 0:
                c = WOOD.deep
            g.p(x, y, c)
    for y in (0, 16):
        g.line(0, y, 31, y, WOOD.hi); g.line(0, y + 15, 31, y + 15, WOOD.deep)
    return g


def salvagers_frame_warp():
    """Warp threads on the frame (cols 6..25, rows 8..21), a hand of bone weft woven in at the bottom."""
    g = Px()
    for x in range(6, 26):
        if x % 2 == 0:
            R = GOLD if x % 8 == 2 else TEAL
            for y in range(8, 22):
                g.p(x, y, R.light if y < 16 else R.base)
    for y in range(17, 22):
        for x in range(6, 26):
            over = (x + y) % 2
            g.p(x, y, BONE.light if (over and y % 2) else BONE.base if over else BONE.dark)
    g.line(6, 16, 25, 16, TEAL.dark)
    return g


# ------------------------------------------------------------------ trophy plinth

def trophy_plinth_side():
    """Marble plinth body: gold rails and a panel (rows 12..25) with a teal thread inlay."""
    g = Px()
    for y in range(32):
        for x in range(32):
            g.p(x, y, MARBLE.dark if (x * 3 + y * 5) % 23 == 0 else MARBLE.base)
    g.line(0, 0, 31, 0, MARBLE.light)
    g.rect(0, 12, 31, 12, GOLD.light); g.rect(0, 13, 31, 13, GOLD.dark)
    g.rect(0, 24, 31, 24, GOLD.light); g.rect(0, 25, 31, 25, GOLD.dark)
    g.rect(7, 16, 24, 21, MARBLE.dark); g.rect(8, 17, 23, 20, MARBLE.base)
    g.line(8, 17, 23, 17, MARBLE.light)
    g.line(9, 19, 22, 19, TEAL.base); g.p(15, 19, GOLD.hi); g.p(16, 19, GOLD.base)
    return g


def trophy_plinth_top():
    """Plinth slab: bevelled marble edges, a gold display ring with a teal thread circle inside."""
    g = Px()
    for y in range(32):
        for x in range(32):
            g.p(x, y, MARBLE.base)
    for i in range(2):
        g.line(i, i, 31 - i, i, MARBLE.light); g.line(i, i, i, 31 - i, MARBLE.light)
        g.line(i, 31 - i, 31 - i, 31 - i, MARBLE.dark); g.line(31 - i, i, 31 - i, 31 - i, MARBLE.dark)
    ring = ring_cells(15.5, 15.5, 8.5, 7)
    g.pts(ring, GOLD.base)
    g.pts({c for c in ring if c[0] + c[1] < 30}, GOLD.light)
    g.pts(ring_cells(15.5, 15.5, 5, 4), TEAL.base)
    for (x, y) in [(5, 5), (26, 5), (5, 26), (26, 26)]:
        g.p(x, y, GOLD.light)
    return g


# ------------------------------------------------------------------ tribe banners

def tribe_banner(tribe):
    """Cloth in the tribe colour (cols 2..29, rows 2..31), the canonical glyph at 2x in bone, a teal-mended tear at
    the lower-left (salvaged), a fringed hem; rows 0..1 carry the rod the item icon hangs from."""
    R = ramp(TRIBE_COLORS[tribe])
    g = Px()
    g.rect(0, 0, 31, 1, WOOD.base); g.line(0, 0, 31, 0, WOOD.light); g.p(0, 1, GOLD.base); g.p(31, 1, GOLD.base)
    g.rect(2, 2, 29, 31, R.base)
    g.rect(3, 5, 6, 26, R.light)
    g.rect(15, 5, 16, 26, R.dark); g.rect(26, 5, 28, 26, R.dark)
    g.rect(2, 2, 29, 4, R.deep); g.line(2, 2, 29, 2, R.dark)
    for x in range(4, 29, 4):
        g.p(x, 3, BONE.dark)
    g.line(2, 2, 2, 27, R.deep); g.line(29, 2, 29, 27, R.deep)
    g.line(2, 27, 29, 27, R.deep)
    for x in range(2, 30):
        if x % 3 == 2:
            for y in range(28, 32):
                g.clear(x, y)
        else:
            for y in range(28, 32 - (x % 2)):
                g.p(x, y, R.dark if y < 30 else R.deep)
    g.glyph(tribe, 7, 8, BONE.light, scale=2, shadow=R.deep)
    for i in range(6):
        g.p(3 + i, 25 - i, TEAL.base); g.p(4 + i, 25 - i, TEAL.dark)
    for (x, y) in [(4, 23), (6, 21), (8, 19)]:
        g.p(x, y, GOLD.light)
    return g


BLOCKS = {
    "tether_thread": tether_thread, "tether_thread_side": tether_thread_side,
    "wreck_chest_front": lambda: wreck_chest("front"), "wreck_chest_side": lambda: wreck_chest("side"),
    "wreck_chest_top": lambda: wreck_chest("top"), "frayed_spawner": frayed_spawner,
    "thread_pillar_off": lambda: thread_pillar(False), "thread_pillar_on": lambda: thread_pillar(True),
    "thread_pillar_top": thread_pillar_top, "thread_idol": thread_idol, "thread_idol_top": thread_idol_top,
    "thread_lock": thread_lock, "rift_tear": rift_tear, "salvage_crate_side": salvage_crate_side,
    "salvage_crate_top": salvage_crate_top, "salvagers_frame_wood": salvagers_frame_wood,
    "salvagers_frame_warp": salvagers_frame_warp, "trophy_plinth_side": trophy_plinth_side,
    "trophy_plinth_top": trophy_plinth_top,
}
