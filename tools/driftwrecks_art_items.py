"""Driftwrecks items at 32x32: thread goods (weft, spool, frayed core), the two lures, the Weft Key, paper goods
(map scroll, hint page, Wreck Atlas), salvage (bundle, rift shard, seal) and the Drift Needle's 32 frames.

Family marks: every thread item carries teal tether thread with a gold seam; paper goods share one bone paper and
teal ink; the lures share a gold swivel on a teal line; the needle keeps one brass case and turns only its needle.
"""
from __future__ import annotations

import math

from art_tribe_glyphs import TRIBE_COLORS, TRIBES
from driftwrecks_art_lib import (BONE, DRIFT, GOLD, INK, IRON, LOOM, PAPER, RED, RIFT, TEAL, Px, ellipse_cells,
                                 poly_cells, ramp, rect_cells, ring_cells, tone)

BURLAP = ramp((0xa8, 0x8a, 0x5c))
VOID = ramp((0x2e, 0x26, 0x3e))


def salvaged_weft():
    """A hank of teal weft: two looped skeins twisted in the middle and bound with a gold seam."""
    g = Px()
    for cx in (9, 22):
        loop = ellipse_cells(cx, 16, 7.5, 6.5) - ellipse_cells(cx, 16, 4, 3)
        g.solid(loop, TEAL)
        for a in range(0, 360, 40):
            t = math.radians(a + cx * 7)
            g.p(round(cx + math.cos(t) * 5.8), round(16 + math.sin(t) * 4.8), TEAL.deep)
    g.solid(rect_cells(14, 11, 17, 21), GOLD, spec=[(14, 12)])
    for y in (13, 16, 19):
        g.line(14, y, 17, y, GOLD.deep)
    g.line(3, 22, 1, 27, LOOM.base); g.line(5, 22, 4, 28, TEAL.light)
    return g.outline()


def frayed_core():
    """A dark knotted core, frayed threads springing out of it, a gold stitch holding it shut."""
    g = Px()
    for i in range(8):
        a = i / 8 * math.tau + 0.3
        r = 13 if i % 2 else 11
        g.line(16, 16, round(16 + math.cos(a) * r), round(16 + math.sin(a) * r), LOOM.base if i % 3 else TEAL.light)
    g.ball(16, 16, 8, R=VOID)
    g.pts(ring_cells(16, 16, 8, 6.8), TEAL.dark)
    g.line(11, 11, 21, 21, GOLD.base, w=2); g.line(21, 11, 11, 21, GOLD.base, w=2)
    g.p(16, 16, GOLD.hi); g.p(12, 12, LOOM.hi)
    return g.outline()


def driftwreck_seal():
    """Red wax seal, gold cross-stitch, two teal thread tails."""
    g = Px()
    g.line(12, 21, 8, 29, TEAL.base, w=2); g.line(19, 21, 23, 29, TEAL.dark, w=2)
    blob = ellipse_cells(16, 14, 11, 10.5)
    for a in range(12):
        t = a / 12 * math.tau
        blob |= ellipse_cells(16 + math.cos(t) * 10.5, 14 + math.sin(t) * 10, 1.8)
    g.solid(blob, RED, spec=[(8, 8), (9, 7)])
    g.pts(ring_cells(16, 14, 7.5, 6.3), RED.deep)
    g.line(12, 14, 20, 14, GOLD.light, w=2); g.line(15, 10, 15, 18, GOLD.light, w=2)
    g.p(15, 14, GOLD.hi)
    return g.outline()


def rift_shard():
    """A violet shard of torn sky, a teal crack of thread-light down its heart."""
    g = Px()
    shard = poly_cells([(15, 2), (22, 9), (21, 20), (16, 29), (10, 22), (9, 10)])
    g.solid(shard, RIFT, spec=[(12, 8), (12, 9)])
    g.line(15, 4, 14, 11, LOOM.light); g.line(14, 11, 17, 17, LOOM.light); g.line(17, 17, 15, 26, LOOM.base)
    g.p(15, 12, LOOM.hi)
    g.fill(poly_cells([(22, 11), (26, 8), (25, 15)]), RIFT)
    g.fill(poly_cells([(9, 14), (5, 17), (9, 19)]), RIFT)
    return g.outline()


def tether_spool():
    """A driftwood spool wound with teal tether, the free end running off with a gold hook."""
    g = Px()
    g.solid(rect_cells(6, 3, 21, 7), DRIFT, axis="y"); g.solid(rect_cells(6, 24, 21, 28), DRIFT, axis="y")
    g.cyl(8, 8, 19, 23, TEAL)
    for y in range(9, 23, 2):
        g.line(8, y, 19, y + 1, TEAL.deep)
    g.line(8, 15, 19, 16, GOLD.light)
    g.fill(ellipse_cells(13.5, 5, 1.6, 1), INK)
    g.line(20, 18, 25, 21, TEAL.light); g.line(25, 21, 27, 26, TEAL.base)
    g.pts(ring_cells(27, 28, 2.6, 1.3) & rect_cells(0, 27, 31, 31), GOLD.base)
    g.p(25, 27, GOLD.light)
    return g.outline()


def _lure_line(g):
    g.line(16, 1, 16, 7, TEAL.light)
    g.pts(ring_cells(16, 8.5, 2.2, 1), GOLD.base)
    g.p(15, 7, GOLD.hi)


def _hook(g, x, y):
    g.line(x, y, x, y + 4, IRON.light)
    g.pts(ring_cells(x - 2, y + 4, 2.5, 1.2) & rect_cells(0, y + 4, 31, 31), IRON.base)
    g.p(x - 4, y + 3, IRON.hi)


def driftlure():
    """A gold spoon lure with a teal eye, swivel and hook: hang it on a Tension Post."""
    g = Px()
    _lure_line(g)
    spoon = ellipse_cells(16, 17, 6, 8)
    g.solid(spoon, GOLD, spec=[(12, 12), (12, 13)])
    g.fill(ellipse_cells(16.5, 14.5, 2.4), TEAL); g.p(16, 14, LOOM.hi)
    g.line(12, 20, 20, 22, GOLD.deep)
    _hook(g, 16, 25)
    return g.outline()


def strand_lure():
    """The Strand Lure: the same swivel on a violet bead body, a nine-colour Strand tassel below."""
    g = Px()
    _lure_line(g)
    g.solid(poly_cells([(16, 10), (21, 15), (16, 21), (11, 15)]), RIFT, spec=[(14, 13)])
    for i, t in enumerate(TRIBES):
        R = ramp(TRIBE_COLORS[t])
        x = 12 + i
        g.line(x, 21, x + (i - 4) // 2, 28 - abs(i - 4) // 2, R.base)
    g.fill(rect_cells(13, 20, 19, 22), GOLD)
    g.p(16, 15, LOOM.hi)
    return g.outline()


def weft_key():
    """A gold key: bow wound with teal weft, bit cut like a needle's eye."""
    g = Px()
    g.solid(ring_cells(9, 9, 7, 3.6), GOLD, spec=[(5, 5)])
    for a in range(0, 360, 45):
        t = math.radians(a)
        g.p(round(9 + math.cos(t) * 5.2), round(9 + math.sin(t) * 5.2), TEAL.base)
    g.fill(ellipse_cells(9, 9, 2), LOOM)
    g.rod(13, 13, 26, 26, GOLD, w=3)
    g.fill(rect_cells(24, 17, 26, 23) - {(25, 19), (25, 20)}, GOLD)
    g.fill(rect_cells(19, 22, 21, 26), GOLD)
    return g.outline()


def salvage_bundle():
    """A burlap bundle knotted at the neck with teal thread, a gold seam across its belly."""
    g = Px()
    g.solid(ellipse_cells(16, 20, 11, 9.5), BURLAP, spec=[(8, 15), (9, 14)])
    g.fill(poly_cells([(11, 11), (21, 11), (24, 3), (19, 6), (16, 2), (13, 6), (8, 3)]), BURLAP)
    g.fill(rect_cells(11, 10, 21, 12), TEAL)
    g.line(11, 10, 21, 10, TEAL.light)
    g.line(21, 11, 26, 14, TEAL.base)
    g.line(7, 22, 25, 22, GOLD.base)
    for x in range(8, 25, 3):
        g.p(x, 21, GOLD.light)
    for (x, y) in [(10, 25), (19, 18), (23, 25), (14, 27)]:
        g.p(x, y, BURLAP.deep)
    return g.outline()


def wreck_atlas():
    """The Wreck Atlas: a teal-bound book, nine columns by six rows of cells tooled in gold on the cover."""
    g = Px()
    g.fill(rect_cells(4, 3, 27, 29), ramp(tone(TEAL.base, 0.7)))
    g.fill(rect_cells(24, 4, 28, 28), PAPER)
    for y in range(6, 28, 2):
        g.p(27, y, PAPER.dark)
    g.fill(rect_cells(4, 3, 7, 29), ramp(tone(TEAL.base, 0.5)))
    g.rect(8, 6, 23, 26, GOLD.dark)
    for j in range(6):
        for i in range(9):
            x, y = 9 + round(i * 1.65), 8 + j * 3
            g.p(x, y, GOLD.light if (i + j) % 4 else LOOM.light); g.p(x, y + 1, GOLD.base if (i + j) % 4 else LOOM.base)
    return g.outline()


def _paper(g, cells):
    g.fill(cells, PAPER)


def wreck_map_scroll():
    """A map scroll: rolled ends of driftwood, a teal route to a red X."""
    g = Px()
    _paper(g, rect_cells(6, 6, 25, 25))
    for y0 in (3, 25):
        g.solid(rect_cells(4, y0, 27, y0 + 3), PAPER, axis="y")
        g.fill(rect_cells(2, y0, 3, y0 + 3), DRIFT); g.fill(rect_cells(28, y0, 29, y0 + 3), DRIFT)
    for (a, b) in [((8, 21), (12, 16)), ((12, 16), (17, 18)), ((17, 18), (21, 11))]:
        g.line(*a, *b, TEAL.base)
    g.line(20, 10, 23, 13, RED.base, w=1); g.line(23, 10, 20, 13, RED.base)
    g.fill(ellipse_cells(10, 11, 2.5), PAPER); g.pts(ring_cells(10, 11, 2.6, 1.5), TEAL.dark)
    return g.outline()


def hint_page():
    """A torn Codex page: teal-ink lines and a gold Codex stamp in the corner."""
    g = Px()
    page = poly_cells([(6, 3), (26, 3), (26, 27), (22, 29), (18, 26), (13, 29), (9, 27), (6, 29)])
    g.fill(page, PAPER)
    for y in (8, 11, 14, 17):
        g.line(9, y, 23 - (y % 3) * 2, y, TEAL.dark)
    g.fill(ellipse_cells(20, 22, 3), GOLD); g.p(19, 21, GOLD.hi)
    g.line(9, 21, 15, 21, TEAL.dark)
    return g.outline()


def drift_needle(i):
    """Frame i of 32: brass case, bone dial, needle pointing (i - 16) / 32 turns clockwise from up."""
    g = Px()
    g.ball(16, 16.5, 13, R=GOLD, spec=False)
    g.fill(ellipse_cells(16, 16.5, 10.5), BONE, rim=False)
    g.pts(ring_cells(16, 16.5, 10.5, 9.5), BONE.dark)
    for k in range(8):
        t = k / 8 * math.tau
        g.p(round(15.5 + math.cos(t) * 8.4), round(16 + math.sin(t) * 8.4), BONE.deep if k % 2 == 0 else BONE.dark)
    a = (i - 16) / 32 * math.tau - math.pi / 2
    ca, sa = math.cos(a), math.sin(a)
    cx, cy = 15.5, 16
    tip = (cx + ca * 9, cy + sa * 9)
    tail = (cx - ca * 6, cy - sa * 6)
    px, py = -sa * 2.1, ca * 2.1
    g.poly([(cx + px, cy + py), tip, (cx - px, cy - py)], TEAL.base)
    g.poly([(cx + px, cy + py), tail, (cx - px, cy - py)], INK)
    g.p(round(cx + ca * 7.5), round(cy + sa * 7.5), LOOM.light)
    g.fill(ellipse_cells(16, 16.5, 1.6), GOLD, rim=False); g.p(15, 16, GOLD.hi)
    g.p(8, 7, GOLD.hi); g.p(9, 6, GOLD.light)
    return g.outline()


ITEMS = {
    "salvaged_weft": salvaged_weft, "frayed_core": frayed_core, "driftwreck_seal": driftwreck_seal,
    "rift_shard": rift_shard, "tether_spool": tether_spool, "driftlure": driftlure, "strand_lure": strand_lure,
    "weft_key": weft_key, "salvage_bundle": salvage_bundle, "wreck_atlas": wreck_atlas,
    "wreck_map_scroll": wreck_map_scroll, "hint_page": hint_page,
}
