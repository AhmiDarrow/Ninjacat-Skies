"""Driftwrecks Keepsakes, part 2: Drumhearts (spark), Pattern-weavers (clock), Colony-keepers (swarm),
Seal-carvers (sigil), Loom-stitchers (spindle); the Heart of the Weave; the glyph tag; the registry.
"""
from __future__ import annotations

import math

from art_tribe_glyphs import TRIBE_COLORS, TRIBES
from driftwrecks_art_keepsakes1 import ramp_of
import driftwrecks_art_keepsakes1 as k1
from driftwrecks_art_lib import (BONE, COPPER, GOLD, INK, IRON, LEAF, LOOM, PAPER, RED, SLATE, TEAL, WAX, WOOD, Px,
                                 ellipse_cells, line_cells, mix, poly_cells, ramp, rect_cells, ring_cells, tone)


# ------------------------------------------------------------------ the tag

def tag(g, tribe):
    """Bone keepsake tag, bottom-right, carrying the canonical tribe glyph; tied on with teal thread."""
    R = ramp(TRIBE_COLORS[tribe])
    for y in range(19, 32):
        for x in range(19, 32):
            g.clear(x, y)
    g.line(18, 18, 20, 20, TEAL.base)
    g.p(17, 17, TEAL.light)
    g.rect(20, 20, 30, 30, BONE.base)
    g.line(20, 20, 30, 20, BONE.light); g.line(20, 20, 20, 30, BONE.light)
    g.line(21, 30, 30, 30, BONE.dark); g.line(30, 21, 30, 30, BONE.dark)
    g.clear(20, 20)
    g.p(21, 21, TEAL.dark)
    g.glyph(tribe, 21, 21, R.deep if tribe in ("spark", "swarm", "spindle", "stone") else R.dark)


# ------------------------------------------------------------------ spark: Drumhearts

def spark_shrine(g, P):
    """Ember Drumstick: a beater with its head still glowing."""
    g.rod(4, 26, 17, 13, WOOD, w=3)
    g.line(6, 22, 9, 19, P.dark)
    g.ball(20.5, 9.5, 6, R=COPPER)
    g.fill(ellipse_cells(20.5, 9.5, 3.4), ramp((0xe8, 0x70, 0x30)), rim=False)
    g.p(19, 8, GOLD.hi); g.p(20, 8, GOLD.light); g.p(21, 10, (0xf0, 0xa0, 0x40))


def spark_watchtower(g, P):
    """Copper Signal Horn: a straight flared horn, mouthpiece low-left, bell open to the upper right."""
    horn = set()
    for i in range(30):
        t = i / 29
        cx, cy = 4 + t * 15, 26 - t * 15
        horn |= ellipse_cells(cx, cy, 1.3 + t ** 2.4 * 4.2)
    horn |= ellipse_cells(20.5, 9.5, 6.5)
    g.solid(horn, COPPER, spec=[(15, 8), (16, 6)])
    g.fill(ellipse_cells(21.5, 8.5, 4), ramp(tone(COPPER.deep, 0.6)), rim=False)
    g.pts(ellipse_cells(22, 8, 2.2), tone(COPPER.deep, 0.4))
    for t in (0.3, 0.55):
        cx, cy = 4 + t * 15, 26 - t * 15
        g.line(round(cx - 2), round(cy - 2), round(cx + 2), round(cy + 2), GOLD.light)
    g.fill(rect_cells(2, 26, 4, 28), GOLD)
    g.line(8, 22, 5, 16, P.base); g.line(5, 16, 9, 12, P.base)


def spark_library(g, P):
    """Rhythm Score Tablet: a copper plate, beats punched in four rows."""
    g.fill(rect_cells(3, 4, 25, 25), COPPER)
    g.rect(5, 6, 23, 23, COPPER.dark)
    g.rect(5, 6, 23, 6, COPPER.deep)
    for j, row in enumerate(("x.x.xx.x", "xx.x.x.x", "x..xx.xx", "x.x.")):
        for i, ch in enumerate(row):
            x, y = 6 + i * 2 + (i // 4), 8 + j * 4
            if ch == "x":
                g.rect(x, y, x, y + 1, COPPER.hi if j % 2 else P.light)
            else:
                g.p(x, y + 1, COPPER.deep)
    for (x, y) in ((4, 5), (24, 5), (4, 24), (24, 24)):
        g.p(x, y, GOLD.light)


def spark_forge(g, P):
    """Bellows Nozzle: a tapered copper nozzle with a leather collar."""
    for x in range(8, 27):
        h = 6.5 - (x - 8) * 0.25
        g.solid(rect_cells(x, round(14 - h), x, round(14 + h)), COPPER, axis="y")
    g.fill(rect_cells(3, 5, 8, 23), ramp_of(P, 0))
    for y in (8, 12, 16, 20):
        g.line(4, y, 7, y, GOLD.light)
    g.fill(rect_cells(24, 11, 27, 16), GOLD)
    g.p(27, 13, INK); g.p(27, 14, INK)
    g.line(9, 9, 22, 11, COPPER.hi)


def spark_garden(g, P):
    """Pepper-Flower Pod: a hooked fire-pepper, green cap."""
    pts = []
    for i in range(22):
        t = i / 21
        cx, cy = 8 + t * 13 + math.sin(t * 3) * 1.5, 7 + t * 17
        r = 4.2 * (1 - t) + 0.9
        pts.append((cx, cy, r))
    body = set()
    for cx, cy, r in pts:
        body |= ellipse_cells(cx, cy, r)
    g.solid(body, RED, spec=[(6, 9), (6, 10), (7, 12)])
    g.fill(poly_cells([(4, 5), (13, 4), (12, 7), (5, 8)]), LEAF)
    g.line(8, 4, 11, 1, LEAF.dark)


def spark_vault(g, P):
    """Sealed Spark Coil: copper wound on a spool, capped, humming."""
    g.fill(rect_cells(5, 3, 22, 6), IRON); g.fill(rect_cells(5, 23, 22, 26), IRON)
    g.cyl(8, 7, 19, 22, COPPER)
    for y in range(8, 22, 2):
        g.line(8, y, 19, y + 1, COPPER.deep)
    g.line(24, 10, 27, 8, LOOM.light); g.line(25, 14, 28, 14, LOOM.base); g.line(1, 13, 3, 11, LOOM.light)
    g.fill(rect_cells(12, 1, 15, 3), P)


# ------------------------------------------------------------------ clock: Pattern-weavers

def clock_shrine(g, P):
    """Escapement Wheel: a brass rim with raked hook teeth, three spokes and a hub."""
    wheel = ring_cells(13.5, 13.5, 8.5, 6)
    for i in range(10):
        a = i / 10 * math.tau
        p0 = (13.5 + math.cos(a) * 8, 13.5 + math.sin(a) * 8)
        p1 = (13.5 + math.cos(a + 0.42) * 12.5, 13.5 + math.sin(a + 0.42) * 12.5)
        p2 = (13.5 + math.cos(a + 0.5) * 8, 13.5 + math.sin(a + 0.5) * 8)
        wheel |= poly_cells([p0, p1, p2])
    for a in (0.3, 2.4, 4.5):
        wheel |= line_cells(13, 13, round(13.5 + math.cos(a) * 6.5), round(13.5 + math.sin(a) * 6.5), w=2)
    g.solid(wheel, GOLD)
    g.fill(ellipse_cells(13.5, 13.5, 2.5), P)
    g.p(13, 13, P.hi)


def clock_watchtower(g, P):
    """Brass Sun-Dial: a dial plate on a column, gnomon casting a line."""
    g.cyl(11, 17, 16, 27, SLATE)
    g.fill(rect_cells(8, 26, 19, 28), SLATE)
    g.solid(ellipse_cells(13.5, 12, 11.5, 5.5), GOLD, axis="y")
    for i in range(9):
        a = math.pi + i / 8 * math.pi
        g.p(round(13.5 + math.cos(a) * 9), round(12 + math.sin(a) * 4), GOLD.deep)
    g.fill(poly_cells([(13, 12), (13, 2), (19, 12)]), P)
    g.line(13, 12, 5, 14, GOLD.deep)


def clock_library(g, P):
    """Loop-Stitched Manual: an upright book, spine stitched in loops, a loop on the cover."""
    R = ramp_of(P, 0)
    g.fill(rect_cells(6, 3, 23, 27), R)
    g.fill(rect_cells(21, 4, 24, 26), PAPER)
    for y in range(6, 26, 3):
        g.p(6, y, GOLD.light); g.p(7, y + 1, GOLD.base)
    g.pts(ring_cells(12, 14, 3, 2) | ring_cells(17, 14, 3, 2), GOLD.light)
    g.rect(9, 22, 19, 23, P.light)


def clock_forge(g, P):
    """Cog of Nine Teeth: nine square teeth, one broken off, a hub bored through."""
    body = ellipse_cells(13.5, 13.5, 8.5)
    for i in range(9):
        if i == 3:
            continue
        a = i / 9 * math.tau - math.pi / 2
        cx, cy = 13.5 + math.cos(a) * 10, 13.5 + math.sin(a) * 10
        body |= ellipse_cells(cx, cy, 2.2)
    body -= ellipse_cells(13.5, 13.5, 2.8)
    g.solid(body, IRON)
    g.pts(ring_cells(13.5, 13.5, 5, 4) & body, P.base)


def clock_garden(g, P):
    """Clockwork Seed: a brass seed with a winding key in its side."""
    seed = ellipse_cells(13, 16, 7.5, 10) | poly_cells([(9, 8), (13, 2), (17, 8)])
    g.solid(seed, GOLD, spec=[(9, 11), (9, 12)])
    for y in (10, 16, 22):
        g.line(7, y, 19, y, GOLD.dark)
    g.fill(rect_cells(20, 14, 22, 16), IRON)
    g.fill(poly_cells([(22, 11), (26, 11), (26, 19), (22, 19)]) - rect_cells(23, 13, 25, 17), P)


def clock_vault(g, P):
    """Timed Lock-Box: an iron-bound box with a clock face for a lock."""
    g.fill(rect_cells(3, 8, 25, 26), ramp_of(P, 0))
    g.fill(rect_cells(3, 8, 25, 11), P)
    for x in (3, 25):
        g.line(x, 8, x, 26, IRON.base)
    g.ball(14, 18, 5, R=PAPER)
    g.pts(ring_cells(14, 18, 5, 4), GOLD.base)
    g.line(14, 18, 14, 15, INK); g.line(14, 18, 16, 18, INK)


# ------------------------------------------------------------------ swarm: Colony-keepers

def swarm_shrine(g, P):
    """Queen's Wax Idol: a wax queen, wings folded, banded body."""
    g.fill(ellipse_cells(7, 11, 4.5, 3), PAPER); g.fill(ellipse_cells(21, 11, 4.5, 3), PAPER)
    g.solid(ellipse_cells(14, 7, 3.5), WAX)
    body = ellipse_cells(14, 18, 5, 8)
    g.solid(body, WAX, spec=[(11, 14)])
    for y in (15, 19, 23):
        g.pts({(x, y) for x in range(8, 21)} & body, INK)
    g.p(13, 6, INK); g.p(15, 6, INK)
    g.line(12, 3, 11, 1, WAX.dark); g.line(16, 3, 17, 1, WAX.dark)


def swarm_watchtower(g, P):
    """Swarm-Reading Glass: a lens with bees caught in it."""
    g.rod(18, 18, 26, 26, WOOD, w=3)
    g.fill(ring_cells(11.5, 11.5, 9, 7), GOLD)
    g.fill(ellipse_cells(11.5, 11.5, 7), ramp(mix(LOOM.base, (255, 255, 255), 0.4)), rim=False)
    for (x, y) in [(9, 9), (14, 12), (10, 15)]:
        g.rect(x, y, x + 1, y, WAX.base); g.p(x, y - 1, PAPER.hi); g.p(x + 2, y, INK)
    g.line(6, 7, 7, 6, (255, 255, 255))


def swarm_library(g, P):
    """Wax-Sealed Ledger: three wax tablets, stacked and sealed with a hex."""
    for i in range(3):
        y = 20 - i * 6
        g.fill(poly_cells([(4 + i, y), (24 - i, y), (26 - i, y + 5), (2 + i, y + 5)]), WAX if i != 1 else ramp(tone(WAX.base, 0.9)))
        g.line(6 + i, y + 2, 21 - i, y + 2, WAX.dark)
    hexa = poly_cells([(14, 5), (18, 7), (18, 11), (14, 13), (10, 11), (10, 7)])
    g.fill(hexa, RED)
    g.p(13, 8, RED.hi)


def swarm_forge(g, P):
    """Smoker Can: a tin can with a spouted lid, bellows on the side, a puff of smoke."""
    g.cyl(6, 11, 17, 26, IRON)
    g.fill(poly_cells([(6, 11), (8, 7), (15, 7), (17, 11)]), IRON)
    g.fill(rect_cells(10, 4, 13, 7), IRON)
    g.fill(poly_cells([(18, 13), (24, 11), (24, 25), (18, 23)]), ramp_of(P, 0))
    g.line(19, 16, 23, 15, P.light); g.line(19, 20, 23, 20, P.light)
    for (x, y, r) in [(9, 2, 1.6), (5, 3, 1.2)]:
        g.fill(ellipse_cells(x, y, r + 0.4), PAPER)


def swarm_garden(g, P):
    """Honey-Flower Bulb: a papery bulb, roots below, a flower opening above."""
    g.solid(ellipse_cells(12, 19, 7, 6.5) | poly_cells([(9, 14), (12, 9), (15, 14)]), BONE, spec=[(8, 16)])
    g.line(12, 13, 12, 22, BONE.dark)
    for x in (9, 12, 15):
        g.line(x, 25, x - 1, 28, WOOD.base)
    g.line(12, 9, 14, 3, LEAF.base)
    for a in range(5):
        t = a / 5 * math.tau
        g.fill(ellipse_cells(15 + math.cos(t) * 2.8, 4.5 + math.sin(t) * 2.8, 1.6), WAX)
    g.p(15, 4, RED.base)


def swarm_vault(g, P):
    """Royal Jelly Jar: a hex-sided jar, cloth tied over the mouth."""
    jar = poly_cells([(7, 9), (21, 9), (23, 13), (23, 25), (20, 27), (8, 27), (5, 25), (5, 13)])
    g.solid(jar, ramp((0xc8, 0xd8, 0xd4)))
    g.fill(rect_cells(7, 14, 21, 25), PAPER, rim=False)
    g.rect(7, 14, 9, 25, PAPER.hi)
    g.fill(poly_cells([(5, 5), (23, 5), (22, 9), (6, 9)]), P)
    g.line(6, 9, 22, 9, WOOD.dark)
    g.p(13, 3, P.dark); g.p(15, 3, P.dark)


# ------------------------------------------------------------------ sigil: Seal-carvers

def sigil_shrine(g, P):
    """Ward-Key Sigil: a diamond ward plate on a short key."""
    plate = poly_cells([(12, 1), (22, 10), (12, 19), (2, 10)])
    g.solid(plate, P)
    g.pts(ring_cells(12, 10, 4.5, 3.3), GOLD.light)
    g.p(12, 10, GOLD.hi)
    g.fill(rect_cells(11, 19, 13, 28), GOLD)
    g.fill(rect_cells(14, 23, 17, 24), GOLD); g.fill(rect_cells(14, 26, 16, 27), GOLD)


def sigil_watchtower(g, P):
    """Warding Lantern: a tall hexagonal lantern with a peaked roof and violet glass."""
    g.fill(poly_cells([(14, 1), (22, 8), (6, 8)]), IRON)
    g.fill(rect_cells(7, 9, 21, 25), IRON)
    g.fill(rect_cells(9, 10, 19, 23), P, rim=False)
    g.rect(9, 10, 11, 23, P.light); g.rect(17, 10, 19, 23, P.dark)
    g.fill(ellipse_cells(14, 16.5, 2.4, 4), ramp(mix(P.hi, (255, 255, 255), 0.4)), rim=False)
    g.line(13, 10, 13, 23, IRON.dark); g.line(15, 10, 15, 11, IRON.dark)
    g.fill(rect_cells(5, 25, 23, 27), IRON)


def sigil_library(g, P):
    """Rubbing of the First Seal: charcoal on paper, the seal's ring and cross."""
    g.fill(poly_cells([(3, 3), (25, 2), (26, 26), (4, 27)]), PAPER)
    ch = (0x3a, 0x3c, 0x48)
    g.pts(ring_cells(14.5, 14.5, 8.5, 6.8), ch)
    g.line(14, 8, 14, 21, ch); g.line(8, 14, 21, 14, ch)
    for (x, y) in [(10, 10), (18, 10), (10, 18), (18, 18)]:
        g.p(x, y, ch)
    g.line(23, 23, 25, 25, PAPER.dark)


def sigil_forge(g, P):
    """Engraving Burin: a mushroom grip and a thin, lozenge-pointed shaft."""
    g.solid(ellipse_cells(7.5, 21, 5.5, 4.5) | rect_cells(6, 17, 11, 21), ramp_of(P, 0), spec=[(4, 19)])
    g.rod(11, 17, 24, 4, IRON, w=2)
    g.fill(poly_cells([(23, 3), (27, 1), (25, 5)]), IRON)
    g.p(27, 1, IRON.hi)
    g.fill(rect_cells(10, 16, 12, 18), GOLD)


def sigil_garden(g, P):
    """Amethyst Seedling: violet crystals growing from a calcite knuckle."""
    g.fill(ellipse_cells(14, 23.5, 10, 4), BONE)
    for (cx, top, w) in [(9, 11, 3), (14, 4, 4), (19, 9, 3), (22, 16, 2)]:
        c = poly_cells([(cx - w, 23), (cx - w, top + w), (cx, top), (cx + w, top + w), (cx + w, 23)])
        g.solid(c, P, spec=[(cx - w + 1, top + w)])
        g.line(cx, top + 1, cx, 21, P.hi if w > 3 else P.light)


def sigil_vault(g, P):
    """Unbroken Seal: a thick wax seal on two ribbon tails, stamped."""
    g.fill(poly_cells([(9, 17), (13, 17), (9, 28), (6, 26)]), ramp_of(P, 0))
    g.fill(poly_cells([(15, 17), (19, 17), (22, 26), (19, 28)]), ramp_of(P, 0))
    blob = ellipse_cells(14, 12, 10, 9.5)
    for a in range(10):
        t = a / 10 * math.tau
        blob |= ellipse_cells(14 + math.cos(t) * 9.5, 12 + math.sin(t) * 9, 1.6)
    g.solid(blob, P)
    g.pts(ring_cells(14, 12, 6.5, 5.3), P.deep)
    g.line(11, 10, 17, 14, P.light); g.line(17, 10, 11, 14, P.light)


# ------------------------------------------------------------------ spindle: Loom-stitchers

def spindle_shrine(g, P):
    """Spindle-Whorl Charm: a drop spindle, a cop of thread wound above the whorl."""
    g.fill(rect_cells(13, 1, 14, 28), WOOD)
    g.solid(ellipse_cells(13.5, 10, 5, 5.5), P)
    for y in range(6, 15, 2):
        g.line(10, y, 17, y + 1, P.dark)
    g.solid(ellipse_cells(13.5, 21, 7.5, 2.5), BONE, axis="y")
    g.line(15, 1, 19, 4, P.light)


def spindle_watchtower(g, P):
    """Weaver's Beacon: a three-legged stand holding a glowing thread-lamp."""
    g.line(14, 14, 6, 28, WOOD.dark, w=2); g.line(14, 14, 22, 28, WOOD.base, w=2); g.line(14, 14, 14, 28, WOOD.light)
    g.fill(poly_cells([(7, 11), (21, 11), (18, 16), (10, 16)]), COPPER)
    g.ball(14, 7, 4.5, R=LOOM)
    g.p(14, 7, (255, 255, 255))
    for (x0, y0, x1, y1) in [(5, 3, 7, 5), (23, 3, 21, 5), (14, 0, 14, 1)]:
        g.line(x0, y0, x1, y1, LOOM.light)


def spindle_library(g, P):
    """Pattern Card of the Old Sky: a punched loom card, a thread path across it."""
    g.fill(poly_cells([(2, 5), (26, 5), (26, 24), (5, 24), (2, 21)]), BONE)
    for j in range(4):
        for i in range(7):
            if (i * 5 + j * 3) % 4 != 1:
                g.p(5 + i * 3, 9 + j * 4, BONE.deep)
    g.line(4, 15, 24, 11, P.base)


def spindle_forge(g, P):
    """Bone Shuttle: a boat shuttle with pointed ends, a bobbin of thread inside."""
    body = set()
    for x in range(1, 28):
        h = 5.5 * math.sin((x - 0.5) / 27.5 * math.pi) ** 0.7
        body |= {(x, y) for y in range(round(14 - h), round(14 + h) + 1)}
    g.solid(body, BONE, axis="y")
    g.fill(rect_cells(9, 12, 18, 16), ramp(tone(BONE.deep, 0.7)), rim=False)
    g.cyl(10, 13, 17, 15, P)
    g.line(17, 14, 27, 20, P.light)


def spindle_garden(g, P):
    """Flax Bloom: three slim stems of blue flax."""
    for (x0, x1, top) in [(8, 7, 9), (14, 15, 4), (20, 21, 11)]:
        g.line(x0, 27, x1, top + 3, LEAF.dark if x0 != 14 else LEAF.base)
    blue = ramp((0x5a, 0x7c, 0xd8))
    for (cx, cy) in [(7, 8), (15, 4), (21, 10)]:
        for a in range(5):
            t = a / 5 * math.tau - math.pi / 2
            g.fill(ellipse_cells(cx + 0.5 + math.cos(t) * 2.2, cy + 0.5 + math.sin(t) * 2.2, 1.5), blue)
        g.p(cx, cy, GOLD.light)
    g.fill(poly_cells([(9, 20), (5, 16), (6, 20)]), LEAF)


def spindle_vault(g, P):
    """Unfinished Tapestry: nine tribe stripes on a rod, one thread hanging loose."""
    g.rod(1, 3, 27, 3, WOOD, w=2)
    for i, t in enumerate(TRIBES):
        R = ramp(TRIBE_COLORS[t])
        x = 3 + i * 2 + (1 if i > 4 else 0)
        g.rect(x, 5, x + 1, 22 - (i % 3), R.base); g.p(x, 5, R.light)
    g.rect(3, 5, 23, 5, P.dark)
    g.line(23, 20, 26, 26, P.light)


def heart_keepsake():
    """Heart of the Weave: a warm gold heart knotted with teal, nine tribe threads trailing from it (no tag: it is
    every tribe's)."""
    g = Px()
    for i, t in enumerate(TRIBES):
        R = ramp(TRIBE_COLORS[t])
        x1 = 4 + i * 3
        g.line(15, 22, x1, 29 - abs(i - 4) // 2, R.base)
        g.p(x1, 29 - abs(i - 4) // 2, R.light)
    heart = ellipse_cells(10, 10, 6.5) | ellipse_cells(21, 10, 6.5) | poly_cells([(4, 13), (27, 13), (15.5, 25)])
    g.solid(heart, GOLD, spec=[(7, 6), (8, 5)])
    for (a, b) in [((6, 9), (25, 17)), ((25, 9), (6, 17)), ((15, 6), (15, 22))]:
        g.line(*a, *b, TEAL.base)
    g.fill(ellipse_cells(15.5, 13.5, 3), LOOM)
    g.p(14, 12, LOOM.hi)
    g.outline()
    return g


CORES = ("shrine", "watchtower", "library", "forge", "garden", "vault")
SHAPES = {name: fn for name, fn in
          list(vars(k1).items()) + list(globals().items())
          if callable(fn) and "_" in name and name.split("_")[0] in TRIBES
          and name.split("_", 1)[1] in CORES}
assert len(SHAPES) == 54, len(SHAPES)


def keepsake(tribe, core):
    g = Px()
    SHAPES[f"{tribe}_{core}"](g, ramp(TRIBE_COLORS[tribe]))
    g.outline()
    tag(g, tribe)
    g.outline()
    return g
