"""Driftwrecks Keepsakes, part 1: Pad-keepers (soil), Grit-singers (stone), Rootbinders (sprout), Edge-walkers (claw).

Each function draws one keepsake object into a 32x32 Px, P = the tribe's ramp. The object keeps clear of the
bottom-right corner (x, y >= 19), where generate_driftwrecks_art hangs the bone tag with the canonical tribe glyph.
"""
from __future__ import annotations

import math

from driftwrecks_art_lib import (CLAY, COPPER, DRIFT, GOLD, IRON, LEAF, LOOM, PAPER, RED, SLATE, TEAL, WAX,
                                 WOOD, hexc, ellipse_cells, poly_cells, ramp, rect_cells, ring_cells, tone)

GOLDEN_NUT = ramp(hexc(0xb07a3e))


def ramp_of(P, k):
    """A darker variant of the tribe ramp (k=0 leather/cover, k=1 seal)."""
    return ramp(tone(P.base, 0.7 if k == 0 else 0.85, 0.05, -0.02))


# ------------------------------------------------------------------ soil: Pad-keepers

def soil_shrine(g, P):
    """Cracked Root-Bell: bronze bell on a root loop, a crack down its shoulder."""
    g.fill(ring_cells(14.5, 4.5, 3.2, 1.6), WOOD)
    bell = poly_cells([(10, 7), (19, 7), (21, 12), (22, 19), (25, 22), (4, 22), (7, 19), (8, 12)])
    g.solid(bell, COPPER, spec=[(10, 9), (10, 10)])
    g.rect(6, 17, 22, 18, P.base); g.rect(6, 17, 9, 17, P.light); g.rect(20, 18, 22, 18, P.dark)
    g.line(15, 8, 13, 12, COPPER.deep); g.line(13, 12, 15, 15, COPPER.deep); g.p(16, 9, COPPER.hi)
    g.fill(ellipse_cells(14.5, 24.5, 2.2), SLATE)


def soil_watchtower(g, P):
    """Soil-Reading Rod: a probe rod with a brass reading-bulb, pushed in at a slant."""
    g.rod(5, 26, 19, 10, WOOD, w=2)
    g.line(3, 28, 5, 25, IRON.base); g.p(3, 28, IRON.light); g.p(2, 29, IRON.dark)
    for (x, y) in [(8, 21), (11, 18), (14, 15)]:
        g.p(x, y, P.light); g.p(x + 1, y, P.dark)
    g.ball(21.5, 7.5, 5, R=GOLD)
    g.fill(ellipse_cells(21.5, 7.5, 2.4), TEAL); g.p(20, 6, TEAL.hi)
    g.line(21, 5, 23, 9, RED.base)


def soil_library(g, P):
    """Pressed Seed Ledger: an open ledger, seeds pressed in the harvest columns."""
    left = poly_cells([(2, 7), (13, 9), (13, 25), (2, 23)])
    right = poly_cells([(15, 9), (26, 7), (26, 23), (15, 25)])
    g.fill(poly_cells([(1, 8), (14, 10), (27, 8), (27, 25), (14, 27), (1, 25)]), ramp_of(P, 0))
    g.fill(left, PAPER); g.fill(right, PAPER)
    g.rect(14, 9, 14, 26, P.deep)
    for y in (12, 15, 18, 21):
        g.line(4, y - 1, 11, y, PAPER.dark)
    for (x, y) in [(18, 12), (21, 12), (24, 11), (18, 16), (22, 15), (19, 20)]:
        g.p(x, y, P.base); g.p(x + 1, y, P.dark)
    g.rect(24, 17, 25, 18, LEAF.base)


def soil_forge(g, P):
    """Worn Mattock Head: a broad adze blade one side, a pick the other, the eye empty."""
    adze = poly_cells([(12, 10), (5, 12), (2, 22), (5, 23), (8, 15), (12, 15)])
    pick = poly_cells([(16, 10), (22, 8), (27, 3), (25, 9), (16, 15)])
    g.solid(adze, IRON, spec=[(3, 21)])
    g.solid(pick, IRON)
    g.solid(rect_cells(11, 7, 17, 18), IRON)
    for x in range(13, 16):
        for y in range(10, 16):
            g.clear(x, y)
    g.line(2, 22, 5, 23, IRON.hi)
    g.line(11, 7, 17, 7, P.light); g.line(11, 18, 17, 18, P.dark)


def soil_garden(g, P):
    """Clay Seed Jar: round-bellied, wax over the mouth and a thumbprint in it."""
    body = ellipse_cells(13.5, 17.5, 9, 8.5) | rect_cells(9, 6, 18, 10)
    g.solid(body, CLAY, spec=[(8, 13), (8, 14)])
    g.fill(rect_cells(8, 4, 19, 7), WAX)
    g.fill(ellipse_cells(13.5, 5.5, 1.6), ramp_of(P, 1))
    for x in range(7, 21, 3):
        g.p(x, 18, CLAY.deep); g.p(x + 1, 19, CLAY.deep)


def soil_vault(g, P):
    """Sealed Seed Tin: a squat tin with a pressed lid and a Pad-keeper label band."""
    g.cyl(5, 9, 22, 24, IRON)
    g.fill(rect_cells(4, 6, 23, 9), IRON)
    g.rect(5, 6, 22, 6, IRON.hi)
    g.cyl(5, 13, 22, 20, P)
    g.rect(9, 15, 17, 18, PAPER.base); g.rect(9, 15, 17, 15, PAPER.light)
    g.line(10, 17, 16, 17, P.deep)
    g.rect(5, 24, 22, 24, IRON.deep)


# ------------------------------------------------------------------ stone: Grit-singers

def stone_shrine(g, P):
    """Echo Shard Pendant: a singing shard on a cord."""
    g.line(6, 2, 13, 9, WOOD.dark); g.line(21, 2, 14, 9, WOOD.base)
    g.fill(rect_cells(12, 8, 15, 10), GOLD)
    shard = poly_cells([(13, 10), (19, 14), (17, 24), (13, 28), (9, 21), (9, 14)])
    g.solid(shard, P, spec=[(11, 14), (11, 15)])
    g.line(13, 12, 13, 25, P.hi)
    g.line(20, 17, 22, 15, LOOM.base); g.line(21, 20, 24, 18, LOOM.base)


def stone_watchtower(g, P):
    """Tuning Fork of Slate: two long tines on a U, a stem to strike it by."""
    fork = rect_cells(8, 2, 10, 15) | rect_cells(16, 2, 18, 15) | (ring_cells(13.5, 14.5, 5.5, 2.6) & rect_cells(0, 15, 31, 31))
    g.solid(fork, SLATE, spec=[(8, 3), (16, 3)])
    g.solid(rect_cells(12, 19, 15, 28), P)
    g.p(12, 20, P.hi)
    for x, y0 in ((4, 5), (22, 5)):
        g.line(x, y0, x, y0 + 5, LOOM.base)
    g.line(2, 3, 2, 12, LOOM.dark); g.line(24, 3, 24, 12, LOOM.dark)


def stone_library(g, P):
    """Scale of Grit Notes: a carved slate stave, pitch-marks on five lines."""
    g.fill(poly_cells([(4, 3), (22, 3), (24, 5), (24, 27), (4, 27)]), SLATE)
    for y in (8, 12, 16, 20, 24):
        g.line(6, y, 22, y, SLATE.deep)
    for (x, y) in [(8, 7), (11, 11), (14, 15), (17, 11), (20, 19), (9, 23)]:
        g.rect(x, y, x + 1, y + 1, P.light); g.p(x + 1, y + 1, P.dark)
    g.rect(22, 3, 24, 5, SLATE.dark)


def stone_forge(g, P):
    """Singing Chisel: a stone-cutter's chisel, rings drawn off its edge."""
    g.rod(4, 26, 12, 18, WOOD, w=3)
    g.fill(rect_cells(12, 15, 14, 18), GOLD)
    g.solid(poly_cells([(14, 14), (21, 6), (24, 6), (24, 9), (17, 17)]), IRON)
    g.line(22, 6, 24, 6, IRON.hi)
    for r in ((26, 3, 28, 5), (27, 9, 29, 10)):
        g.line(*r, LOOM.base)
    g.line(20, 2, 23, 2, LOOM.dark)


def stone_garden(g, P):
    """Lichen Stone: a river pebble grown with ring lichen."""
    g.ball(13.5, 15.5, 11, 9.5, R=P)
    for r in (7.5, 5, 2.5):
        g.pts(ring_cells(12.5, 14.5, r, r - 1) & ellipse_cells(13.5, 15.5, 10, 8.5), LEAF.light if r < 6 else LEAF.base)
    g.p(12, 14, WAX.light)


def stone_vault(g, P):
    """Resonance Key: a stone key whose bit is a tuning fork."""
    g.fill(ring_cells(8.5, 8.5, 6.5, 3.2), P)
    g.p(5, 5, P.hi)
    g.rod(12, 12, 23, 23, P, w=3)
    g.fill(rect_cells(21, 15, 22, 21), P); g.fill(rect_cells(17, 21, 19, 23), P)
    g.fill(ellipse_cells(8.5, 8.5, 1.6), LOOM)


# ------------------------------------------------------------------ sprout: Rootbinders

def sprout_shrine(g, P):
    """Living Knot Charm: a living twig tied in a knot, still putting out leaves."""
    g.fill(ring_cells(10.5, 12.5, 7, 4.5), WOOD)
    g.fill(ring_cells(17.5, 14.5, 7, 4.5) - ellipse_cells(10.5, 12.5, 7), WOOD)
    g.line(11, 6, 12, 8, WOOD.deep)
    for (x, y) in [(4, 4), (22, 6), (8, 21)]:
        g.fill(poly_cells([(x, y), (x + 4, y - 2), (x + 5, y + 1), (x + 1, y + 3)]), P)
    g.line(14, 22, 14, 27, WOOD.base)


def sprout_watchtower(g, P):
    """Vine-Wound Spyglass: a brass glass with a green vine grown around it."""
    for i, w in enumerate((5, 4, 3)):
        x0, y0 = 3 + i * 7, 20 - i * 6
        g.rod(x0, y0, x0 + 7, y0 - 6, GOLD, w=w)
    g.fill(ellipse_cells(5, 21.5, 2.5), GOLD); g.p(4, 20, GOLD.hi)
    for i in range(0, 20, 4):
        g.p(5 + i, 23 - i, P.base); g.p(6 + i, 21 - i, P.dark)
    for (x, y) in [(9, 13), (18, 9)]:
        g.fill(poly_cells([(x, y), (x + 3, y - 2), (x + 3, y + 1)]), P)


def sprout_library(g, P):
    """Pressed-Flower Frame: nine flower spaces, one empty."""
    g.fill(rect_cells(3, 3, 25, 25), WOOD)
    g.fill(rect_cells(6, 6, 22, 22), PAPER, rim=False)
    cols = [RED.base, GOLD.light, (0x8a, 0x5f, 0xc7), (0x6a, 0x8c, 0xe0), RED.light, GOLD.base, (0xe0, 0x90, 0xa0), P.light]
    k = 0
    for j in range(3):
        for i in range(3):
            x, y = 8 + i * 5, 8 + j * 5
            if (i, j) == (2, 2):
                g.rect(x, y, x + 2, y + 2, PAPER.dark)
                continue
            g.p(x + 1, y, cols[k]); g.p(x, y + 1, cols[k]); g.p(x + 2, y + 1, cols[k]); g.p(x + 1, y + 1, GOLD.hi)
            g.p(x + 1, y + 2, P.dark); k += 1


def sprout_forge(g, P):
    """Grafting Knife: a hooked blade folding out of a wooden grip, a twist of binding on it."""
    g.rod(4, 25, 13, 16, WOOD, w=3)
    g.line(6, 22, 9, 19, P.base); g.line(7, 23, 10, 20, P.dark)
    blade = poly_cells([(13, 15), (21, 6), (26, 4), (24, 9), (18, 15), (15, 18)])
    g.solid(blade, IRON)
    g.line(14, 15, 22, 6, IRON.hi)
    g.fill(rect_cells(12, 15, 14, 18), GOLD)


def sprout_garden(g, P):
    """Sprouting Acorn: a split acorn pushing out a shoot."""
    g.solid(ellipse_cells(13.5, 18.5, 7, 8), GOLDEN_NUT, spec=[(10, 15)])
    g.fill(poly_cells([(6, 12), (21, 12), (20, 15), (7, 15)]), WOOD)
    for x in range(8, 20, 2):
        g.p(x, 13, WOOD.deep)
    g.line(14, 11, 15, 5, P.base); g.line(15, 11, 16, 5, P.dark)
    g.fill(poly_cells([(15, 6), (20, 2), (23, 4), (19, 7)]), P)
    g.fill(poly_cells([(15, 7), (10, 3), (8, 5), (12, 8)]), P)
    g.line(12, 22, 16, 18, WOOD.deep)


def sprout_vault(g, P):
    """Heartwood Box: a box grown shut, bark on the edges, the lid a slice of rings."""
    g.fill(rect_cells(3, 11, 24, 25), DRIFT)
    g.solid(rect_cells(5, 13, 22, 23), WOOD)
    for r in (7, 5, 3, 1):
        g.pts(ring_cells(13.5, 18, r + 0.6, r - 0.4) & rect_cells(5, 13, 22, 23), WOOD.light if r % 4 == 3 else WOOD.dark)
    g.fill(poly_cells([(3, 11), (7, 6), (21, 6), (24, 11)]), P)
    g.line(8, 7, 20, 7, P.hi)
    g.line(4, 16, 4, 22, P.base)


# ------------------------------------------------------------------ claw: Edge-walkers

def claw_shrine(g, P):
    """Claw-Marked Stone: four scratches, the last one unfinished."""
    g.ball(14, 15.5, 11.5, 10, R=SLATE)
    for i, ln in enumerate((12, 12, 11, 6)):
        x = 8 + i * 4
        g.line(x, 9, x - 2, 9 + ln, SLATE.deep); g.line(x + 1, 9, x - 1, 9 + ln, P.base)


def claw_watchtower(g, P):
    """Rim-Walker's Lantern: an iron cage lantern, the flame still lit."""
    g.fill(ring_cells(14, 5, 4, 2.5) - rect_cells(9, 5, 19, 10), IRON)
    g.fill(poly_cells([(8, 8), (20, 8), (23, 11), (5, 11)]), IRON)
    g.fill(rect_cells(7, 11, 21, 24), IRON)
    g.fill(rect_cells(9, 12, 19, 22), WAX, rim=False)
    g.rect(9, 12, 19, 22, GOLD.light); g.fill(ellipse_cells(14, 18, 3, 4.5), GOLD, rim=False)
    g.rect(13, 16, 14, 20, GOLD.hi); g.rect(13, 21, 15, 22, P.base)
    for x in (11, 17):
        g.line(x, 12, x, 22, IRON.dark)
    g.fill(rect_cells(5, 24, 23, 26), IRON)


def claw_library(g, P):
    """Knotted Route Cord: a hanging cord of footholds; read it with your fingers."""
    for y in range(3, 29):
        x = 13 + round(4 * math.sin(y * 0.35))
        g.p(x, y, P.light); g.p(x + 1, y, P.base); g.p(x + 2, y, P.dark)
    for y in (6, 11, 16, 21, 26):
        x = 13 + round(4 * math.sin(y * 0.35))
        g.fill(ellipse_cells(x + 1.5, y + 0.5, 2.6, 2), P)
        g.p(x + 1, y - 1, P.hi)
    g.fill(rect_cells(9, 1, 18, 3), WOOD)


def claw_forge(g, P):
    """Spiked Boot-Iron: a crampon frame, strap buckled, teeth down."""
    frame = poly_cells([(3, 12), (24, 12), (26, 15), (24, 18), (3, 18)])
    g.solid(frame, IRON, axis="y")
    g.fill(rect_cells(8, 13, 20, 16), P, rim=False); g.line(8, 13, 20, 13, P.light)
    for x in (5, 10, 15, 20, 24):
        g.fill(poly_cells([(x - 1, 19), (x + 2, 19), (x, 24)]), IRON)
    g.fill(rect_cells(12, 6, 15, 12), P)
    g.fill(ring_cells(13.5, 7, 3, 1.5), GOLD)


def claw_garden(g, P):
    """Cliff-Rose Cutting: a red rose on a thorned stem."""
    g.line(14, 13, 12, 28, LEAF.dark); g.line(15, 13, 13, 28, LEAF.base)
    for (x, y) in [(12, 18), (15, 23), (12, 25)]:
        g.p(x, y, LEAF.deep)
    g.fill(poly_cells([(15, 20), (21, 16), (22, 19), (17, 21)]), LEAF)
    g.ball(14.5, 8.5, 6.5, 6, R=RED)
    g.line(11, 6, 14, 9, RED.deep); g.line(17, 5, 15, 9, RED.deep); g.line(12, 11, 17, 11, RED.dark)


def claw_vault(g, P):
    """Gold Claw Clasp: three hooked gold talons closing on a stone, on a gold cuff."""
    g.ball(14, 12, 5, R=P)
    for (pts, hook) in [([(5, 18), (4, 12), (6, 6), (9, 4)], (10, 6)), ([(14, 17), (14, 10), (14, 3), (15, 2)], (16, 3)),
                        ([(23, 18), (24, 12), (22, 6), (19, 4)], (18, 6))]:
        for a, b in zip(pts, pts[1:]):
            g.line(*a, *b, GOLD.base, w=2)
        g.p(*hook, GOLD.light)
        g.p(pts[0][0], pts[0][1] - 5, GOLD.hi)
    g.fill(poly_cells([(3, 17), (25, 17), (23, 23), (5, 23)]), GOLD)
    g.line(6, 19, 22, 19, GOLD.hi)
    g.fill(ellipse_cells(14, 20.5, 1.6), RED)

