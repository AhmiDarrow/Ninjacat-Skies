#!/usr/bin/env python3
"""Driftwreck block plans: 6 cores x 3 tiers (+ the Heartwreck), written as role-keyed NCGA plans.

    python tools/wreck_factory.py                 # write mods/driftwrecks/.../data/driftwrecks/wreck/*.ncga
    python tools/wreck_factory.py --render DIR    # also write an isometric render sheet per plan + a contact sheet

Pure Python (Pillow only for renders). Every plan names *roles*, not blocks: the Strand skin rolled in game turns
wall/floor/trim/... into that tribe's palette (StrandSkin.java). Keys starting with "mc:" are literal blocks; keys
starting with "h_" belong to the hidden room and become the plan's fill role when the room is closed.

Coordinates: x east, z south, y up; origin x/z at the wreck centre, y 0 = main deck top surface (blocks at y 0 are
the deck, people stand at y 1). Deterministic: the same seed always writes the same bytes.
"""
from __future__ import annotations

import argparse
import math
import random
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mods/driftwrecks/src/main/resources/data/driftwrecks/wreck"
TIERS = {"raft": 1, "ruin": 2, "hold": 3}
MAX_SIZE = {1: 15, 2: 31, 3: 48}
MAX_HEIGHT = {1: 12, 2: 24, 3: 40}
PILLARS = {1: 3, 2: 4, 3: 5}
CHESTS = {1: 2, 2: 4, 3: 6}
SPAWNERS = {1: 1, 2: 2, 3: 4}
SOLIDISH = ("keel", "keel2", "floor", "wall", "wall2", "trim", "beam", "roof", "accent", "soil", "metal", "slab", "glass")
# markers (chests, pillars, spawners...) only go on real floors people walk: never roofs, wall tops or stair slabs
WALKABLE = ("floor", "soil", "keel", "keel2", "accent", "trim", "metal")


class Plan:
    def __init__(self, name: str, tier: int, seed: int):
        self.name, self.tier = name, tier
        self.rng = random.Random(seed)
        self.v: dict[tuple[int, int, int], str] = {}
        self.markers: list[tuple[str, int, int, int, int]] = []
        self.reserved: set[tuple[int, int, int]] = set()
        self.fill = "wall"
        # module mode: structure only. The Java composer supplies keel, deck, seam and the spread markers; air carved
        # at or below the deck is recorded as "x_air" so it cuts through the composer's rock.
        self.module = False
        self.variant = 0

    # ---------------------------------------------------------------- primitives
    def set(self, x, y, z, key):
        if key is None or key == "air":
            if self.module and key == "air" and y <= 0:
                self.v[(x, y, z)] = "x_air"
                return
            self.v.pop((x, y, z), None)
        else:
            self.v[(x, y, z)] = key

    def get(self, x, y, z):
        return self.v.get((x, y, z))

    def box(self, x0, y0, z0, x1, y1, z1, key):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, key)

    def hollow(self, x0, y0, z0, x1, y1, z1, key, inner="air"):
        self.box(x0, y0, z0, x1, y1, z1, key)
        self.box(x0 + 1, y0 + 1, z0 + 1, x1 - 1, y1 - 1, z1 - 1, inner)

    def walls(self, x0, y0, z0, x1, y1, z1, key):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, z0, key); self.set(x, y, z1, key)
            for z in range(z0, z1 + 1):
                self.set(x0, y, z, key); self.set(x1, y, z, key)

    def disc(self, cx, y, cz, r, key, only_empty=False):
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                if x * x + z * z <= r * r + r * 0.8:
                    if only_empty and self.get(cx + x, y, cz + z):
                        continue
                    self.set(cx + x, y, cz + z, key)

    def ring(self, cx, y, cz, r, key, width=1):
        for x in range(-r - 1, r + 2):
            for z in range(-r - 1, r + 2):
                d = math.sqrt(x * x + z * z)
                if r - width < d <= r + 0.5:
                    self.set(cx + x, y, cz + z, key)

    def column(self, x, y0, z, h, key, cap=None):
        for y in range(y0, y0 + h):
            self.set(x, y, z, key)
        if cap:
            self.set(x, y0 + h, z, cap)

    def mark(self, kind, x, y, z, data=0):
        self.markers.append((kind, x, y, z, data))
        self.reserved.add((x, y, z))

    # ---------------------------------------------------------------- shared DNA
    def keel(self, r: int, depth: int, cx=0, cz=0, y_top=-1):
        """An irregular rock keel under a deck: tapering, lumpy, with a soil skin on top."""
        if self.module:
            return
        rng = self.rng
        lumps = [(rng.uniform(0, math.tau), rng.uniform(0.6, 1.25)) for _ in range(7)]
        for d in range(depth):
            frac = d / max(1, depth)
            rr = r * (1 - frac ** 1.25) + 0.6
            for x in range(-r - 2, r + 3):
                for z in range(-r - 2, r + 3):
                    ang = math.atan2(z, x)
                    wob = 1 + 0.18 * sum(math.cos(ang * (i + 2) + a) * s for i, (a, s) in enumerate(lumps)) / len(lumps)
                    if math.hypot(x, z) <= min(rr * wob, r + 0.4):
                        key = "soil" if d == 0 else ("keel2" if (x * 7 + z * 13 + d * 5) % 5 == 0 else "keel")
                        self.set(cx + x, y_top - d, cz + z, key)
        # drip stones under the keel
        for _ in range(r):
            a = rng.uniform(0, math.tau); rr = rng.uniform(0, r * 0.4)
            x, z = int(cx + math.cos(a) * rr), int(cz + math.sin(a) * rr)
            for d in range(depth, depth + rng.randint(1, 3)):
                self.set(x, y_top - d, z, "keel")

    def seam(self, r: int, depth: int):
        """The frayed seam where the piece was cut loose: a glowing jagged crack down one side of the keel."""
        if self.module:
            return
        rng = self.rng
        a = rng.uniform(0, math.tau)
        for d in range(0, depth):
            rr = r * (1 - (d / max(1, depth)) ** 1.25)
            jitter = rng.uniform(-0.25, 0.25)
            for w in (-1, 0, 1):
                ang = a + jitter + w * 0.08
                x, z = round(math.cos(ang) * rr), round(math.sin(ang) * rr)
                y = -1 - d
                if self.get(x, y, z):
                    self.set(x, y, z, "seam" if (d + w) % 3 else "seam2")
        # loose threads trailing off the deck edge
        for i in range(3 + self.tier):
            ang = a + (i - 1) * 0.15
            x, z = round(math.cos(ang) * r), round(math.sin(ang) * r)
            for d in range(1, rng.randint(2, 4)):
                self.set(x, -d, z, "mc:cyan_wool" if i % 2 else "mc:yellow_wool")

    def deck(self, r: int, y=0, key="floor", cx=0, cz=0):
        if self.module:
            return
        self.disc(cx, y, cz, r, key)

    def erode(self, prob: float, top_only_above=1):
        """Break the rim: exposed edge blocks above the deck drop out, so the wreck reads as torn, not built."""
        rng = self.rng
        keys = list(self.v.items())
        for (x, y, z), k in keys:
            if y < top_only_above or k.startswith("mc:") or k.startswith("h_") or k.startswith("seam"):
                continue
            exposed = sum(1 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + dx, y, z + dz) not in self.v)
            if exposed >= 2 and (x, y + 1, z) not in self.v and rng.random() < prob:
                self.v.pop((x, y, z), None)

    # ---------------------------------------------------------------- markers
    def standable(self, x, y, z):
        below = self.get(x, y - 1, z)
        return (below is not None and below in WALKABLE and not self._under_roof_top(x, y, z)
                and (x, y, z) not in self.v and (x, y + 1, z) not in self.v and (x, y, z) not in self.reserved)

    def _under_roof_top(self, x, y, z):
        """True on a wall top: the cell sits level with the top of a wall run (no wall-height space above it inside)."""
        return self.get(x, y - 2, z) in ("wall", "wall2", "beam") and self.get(x, y - 1, z) in ("wall", "wall2", "trim", "beam")

    def free_cells(self, y_min=-60, y_max=80):
        cells = []
        for (x, y, z), k in self.v.items():
            if k.startswith("h_") or k.startswith("mc:") or k.startswith("seam"):
                continue
            if y_min <= y + 1 <= y_max and self.standable(x, y + 1, z):
                cells.append((x, y + 1, z))
        cells.sort()
        return cells

    def spread(self, kind, n, cells, data_fn=lambda i: 0, min_gap=3):
        """Place n markers of a kind spread around the wreck by angle, keeping a gap from other markers."""
        chosen = []
        if not cells:
            return chosen
        buckets = {}
        for c in cells:
            ang = (math.atan2(c[2], c[0]) + math.tau) % math.tau
            buckets.setdefault(int(ang / math.tau * max(1, n) * 2), []).append(c)
        order = sorted(buckets)
        self.rng.shuffle(order)
        for b in order:
            if len(chosen) >= n:
                break
            opts = [c for c in buckets[b] if all(abs(c[0] - m[1]) + abs(c[2] - m[3]) + abs(c[1] - m[2]) >= min_gap for m in self.markers)]
            if opts:
                c = self.rng.choice(opts)
                self.mark(kind, *c, data_fn(len(chosen)))
                chosen.append(c)
        while len(chosen) < n:
            opts = [c for c in cells if c not in self.reserved and all(abs(c[0] - m[1]) + abs(c[2] - m[3]) >= 2 for m in self.markers)]
            if not opts:
                break
            c = self.rng.choice(opts)
            self.mark(kind, *c, data_fn(len(chosen)))
            chosen.append(c)
        return chosen

    def standard_markers(self, deck_r: int, heart, idol, hidden_chest=None, rift=None, echo=None, center=None):
        t = self.tier
        self.mark("chest", *heart, 1)
        self.mark("idol", *idol, 0)
        if hidden_chest:
            self.mark("chest", *hidden_chest, 2)
        if rift:
            self.mark("rift", *rift, 0)
        if self.module:
            if center:
                self.mark("center", *center, 0)
            return
        cells = self.free_cells()
        self.spread("pillar", PILLARS[t], cells, data_fn=lambda i: i, min_gap=4)
        self.spread("chest", CHESTS[t] - 1, cells, min_gap=4)
        self.spread("spawner", SPAWNERS[t], cells, min_gap=5)
        self.spread("mob", 2 + 2 * t, cells, min_gap=3)
        if echo:
            self.mark("echo", *echo, 0)
        else:
            self.spread("echo", 1, cells)
        if center:
            self.mark("center", *center, 0)
        else:
            self.mark("center", 0, 1, 0, 0) if self.standable(0, 1, 0) else self.spread("center", 1, cells)
        # tether landings: the deck edge at the four bearings
        for i, (dx, dz) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
            for rr in range(deck_r + 2, 0, -1):
                x, z = dx * rr, dz * rr
                if self.get(x, 0, z) and self.get(x, 1, z) is None:
                    self.mark("dock", x, 0, z, i)
                    break

    # ---------------------------------------------------------------- output
    def clamp_height(self):
        """Trim the bottom of the keel so the plan fits its tier's height budget; the deck and above never move."""
        lim = MAX_HEIGHT.get(self.tier)
        if not lim:
            return
        top = max(p[1] for p in self.v)
        floor_y = top - lim + 1
        for pos in [p for p in self.v if p[1] < floor_y]:
            del self.v[pos]

    def check(self):
        self.clamp_height()
        xs = [p[0] for p in self.v]; ys = [p[1] for p in self.v]; zs = [p[2] for p in self.v]
        w, h, d = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) - min(zs) + 1
        lim = MAX_SIZE[self.tier] if self.tier in MAX_SIZE else 999
        assert w <= lim and d <= lim, (self.name, "footprint", w, d, lim)
        assert h <= (MAX_HEIGHT.get(self.tier, 999)), (self.name, "height", h)
        for m in self.markers:
            assert m[2] - 1 >= min(ys) or m[0] == "dock", (self.name, "marker below the trimmed keel", m)
        kinds = {m[0] for m in self.markers}
        for need in ("chest", "idol", "pillar", "spawner", "dock", "echo", "center"):
            assert need in kinds, (self.name, "missing marker", need)
        assert sum(1 for m in self.markers if m[0] == "chest" and m[4] == 1) == 1, (self.name, "one heart chest")
        return w, h, d

    def write(self, path: Path):
        keys = sorted(set(self.v.values()))
        assert len(keys) <= 255, (self.name, len(keys))
        idx = {k: i for i, k in enumerate(keys)}
        out = bytearray()
        out += struct.pack("<IIH", 0x4147434E, 1, len(keys))
        for k in keys:
            b = k.encode("utf-8"); out += struct.pack("<H", len(b)) + b
        blocks = sorted(self.v.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2]))   # keel first: builds bottom-up
        out += struct.pack("<I", len(blocks))
        for (x, y, z), k in blocks:
            out += struct.pack("<hhhB", x, y, z, idx[k])
        f = self.fill.encode("utf-8"); out += struct.pack("<H", len(f)) + f
        out += struct.pack("<H", len(self.markers))
        for kind, x, y, z, data in self.markers:
            b = kind.encode("utf-8"); out += struct.pack("<H", len(b)) + b + struct.pack("<hhhB", x, y, z, data)
        path.write_bytes(bytes(out))


def crypt_stair(p: Plan, x: int, z0: int, walk_top: int, floor_y: int):
    """A one-wide stair from a landing at (x, walk_top, z0 + 1) down, northward, to a crypt floor at floor_y.
    The whole run must lie inside the crypt's air in x and z; above the crypt it cuts through deck and keel."""
    n = walk_top - floor_y - 2
    p.box(x, walk_top, z0 + 1, x, walk_top + 1, z0 + 1, "air")               # the landing
    for k in range(1, n + 1):
        z = z0 - (k - 1)
        p.box(x, walk_top - k, z, x, walk_top + 1, z, "air")                 # headroom and the opening
        p.set(x, walk_top - 1 - k, z, "stair_s")                             # climbs south, back toward the landing


# ==================================================================== cores

def shrine(t: int, seed: int, v: int = 0, module: bool = False) -> Plan:
    p = Plan(f"shrine_{['', 'raft', 'ruin', 'hold'][t]}", t, seed)
    p.module, p.variant = module, v
    R = {1: 6, 2: 13, 3: 18}[t]
    depth = {1: 5, 2: 9, 3: 12}[t]
    p.keel(R, depth); p.deck(R)
    p.ring(0, 0, 0, R, "trim")
    ring_r = {1: 4, 2: 9, 3: 12}[t] - (p.variant % 2)
    n = {1: (6, 5, 8), 2: (10, 8, 12), 3: (12, 10, 14)}[t][p.variant % 3]
    h = {1: 3, 2: 5, 3: 7}[t] + (1 if p.variant == 2 else 0) - (1 if t == 1 and p.variant == 2 else 0)
    for i in range(n):
        a = i / n * math.tau
        x, z = round(math.cos(a) * ring_r), round(math.sin(a) * ring_r)
        broken = p.rng.random() < 0.3
        p.column(x, 1, z, h - (p.rng.randint(1, h - 1) if broken else 0), "beam", None if broken else "trim")
    if t >= 2:   # lintels between standing pillars
        for i in range(n):
            a0, a1 = i / n * math.tau, (i + 1) / n * math.tau
            if p.rng.random() < 0.6:
                for s in range(8):
                    a = a0 + (a1 - a0) * s / 7
                    p.set(round(math.cos(a) * ring_r), h + 1, round(math.sin(a) * ring_r), "slab")
    # raised altar with steps
    ar = {1: 1, 2: 2, 3: 3}[t]
    p.box(-ar, 1, -ar, ar, 1, ar, "trim")
    if t >= 2:
        p.box(-ar + 1, 2, -ar + 1, ar - 1, 2, ar - 1, "accent")
        for s in range(-ar, ar + 1):
            p.set(s, 1, ar + 1, "stair_n")
    top = 2 if t == 1 else 3
    p.set(0, top - 1, 0, "accent")
    p.set(0, top, -1 if t == 1 else 0, "mc:decorated_pot")
    # hidden room under the altar
    p.box(-1, -4, -1, 1, -2, 1, "h_air")
    p.set(0, -1, ar + 2, "h_air"); p.set(0, -2, ar + 2, "h_air"); p.set(0, -3, ar + 2, "h_air")
    p.box(0, -4, 1, 0, -2, ar + 2, "h_air")
    p.set(0, 0, ar + 2, "h_mc:spruce_trapdoor[half=top,facing=south]")
    p.set(-1, -2, -1, "h_light")
    heart = (0, 1, -ar - 2)
    idol = (0, top, 1) if t == 1 else (0, top, 0)
    if t == 1:
        idol = (0, 2, 1)
    rift = None
    if t == 3:   # crypt level carved into the keel with the sealed rift
        p.box(-7, -9, -7, 7, -5, 7, "air")
        p.hollow(-8, -10, -8, 8, -4, 8, "wall", inner="air")
        p.box(-7, -10, -7, 7, -10, 7, "floor")
        for x in (-5, 0, 5):
            for z in (-5, 5):
                p.column(x, -9, z, 5, "beam")
        crypt_stair(p, -7, 7, 1, -10)   # stair down along the west wall
        rift = (0, -9, 0)
        for x, z in ((-6, -6), (6, -6), (6, 6)):
            p.set(x, -8, z, "light")
        # upper broken halo of arches
        for i in range(16):
            a = i / 16 * math.tau
            if p.rng.random() < 0.7:
                p.set(round(math.cos(a) * 15), 12, round(math.sin(a) * 15), "roof")
                p.set(round(math.cos(a) * 15), 11, round(math.sin(a) * 15), "seam" if i % 4 == 0 else "trim")
    for i in range(4 * t):   # lanterns on the rim
        a = i / (4 * t) * math.tau + 0.2
        x, z = round(math.cos(a) * (R - 1)), round(math.sin(a) * (R - 1))
        if p.get(x, 1, z) is None:
            p.set(x, 1, z, "light")
    p.seam(R, depth)
    p.erode(0.25)
    p.standard_markers(R, heart, idol, hidden_chest=(0, -3, 0), rift=rift)
    return p


def watchtower(t: int, seed: int, v: int = 0, module: bool = False) -> Plan:
    p = Plan(f"watchtower_{['', 'raft', 'ruin', 'hold'][t]}", t, seed)
    p.module, p.variant = module, v
    R = {1: 6, 2: 12, 3: 18}[t]
    depth = {1: 3, 2: 5, 3: 9}[t]
    p.keel(R, depth); p.deck(R)
    tr = {1: 3, 2: 5, 3: 7}[t] - (1 if p.variant == 1 and t > 1 else 0)   # tower half-width
    floors = {1: 2, 2: 3, 3: 4}[t] - (1 if p.variant == 2 and t > 1 else 0)
    fh = {1: 3, 2: 4, 3: 5}[t]
    top_y = floors * fh
    # the spire: square hollow shaft with floors, windows, a spiral stair with gaps
    for f in range(floors):
        y0 = 1 + f * fh
        p.walls(-tr, y0, -tr, tr, y0 + fh - 1, tr, "wall" if f % 2 == 0 else "wall2")
        for c in ((-tr, -tr), (tr, -tr), (-tr, tr), (tr, tr)):
            p.column(c[0], y0, c[1], fh, "beam")
        if f > 0:
            p.box(-tr + 1, y0 - 1, -tr + 1, tr - 1, y0 - 1, tr - 1, "floor")
            p.box(-tr + 1, y0 - 1, -tr + 1, -tr + 2, y0 - 1, -tr + 2, "air")   # stair well
        for side in range(4):
            wx, wz = [(0, -tr), (tr, 0), (0, tr), (-tr, 0)][side]
            p.set(wx, y0 + 1, wz, "glass"); p.set(wx, y0 + 2, wz, "glass")
        p.set(0, y0 + fh - 2, 0, "mc:lantern[hanging=true]") if f > 0 else None
    # door
    p.box(-1, 1, tr, 1, 3, tr, "air"); p.set(0, 4, tr, "trim")
    # spiral stair (with gaps) up the inside of the walls
    ring = []
    for x in range(-tr + 1, tr):
        ring.append((x, -tr + 1))
    for z in range(-tr + 2, tr):
        ring.append((tr - 1, z))
    for x in range(tr - 2, -tr, -1):
        ring.append((x, tr - 1))
    for z in range(tr - 2, -tr + 1, -1):
        ring.append((-tr + 1, z))
    y = 1
    i = 0
    while y < top_y:
        x, z = ring[i % len(ring)]
        if p.rng.random() > 0.12:     # gaps: the stair is broken in places
            p.set(x, y, z, "slab" if i % 2 == 0 else "slab_top")
            if i % 2 == 1:
                y += 1
        else:
            if i % 2 == 1:
                y += 1
        i += 1
    # collapsed crown: cracked beacon cap
    p.box(-tr, top_y + 1, -tr, tr, top_y + 1, tr, "roof")
    p.box(-tr + 1, top_y + 1, -tr + 1, tr - 1, top_y + 1, tr - 1, "floor")
    p.set(0, top_y + 2, 0, "mc:beacon" if t == 3 else "accent")
    # the broken spiral never reaches the crown: a ladder up the stair-well corner, out through the crown floor
    for yy in range(1, top_y + 2):
        p.set(-tr + 1, yy, -tr + 1, "mc:ladder[facing=south]")
    for c in ((-tr, -tr), (tr, -tr), (-tr, tr), (tr, tr)):
        p.column(c[0], top_y + 2, c[1], t, "beam", "light")
    p.set(1, top_y + 2, 1, "mc:spyglass_placeholder") if False else None
    # fallen masonry on the deck
    for _ in range(6 * t):
        a = p.rng.uniform(0, math.tau); rr = p.rng.uniform(tr + 2, R - 1)
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        p.set(x, 1, z, p.rng.choice(["wall", "wall2", "keel2", "slab"]))
    # hidden room behind the stair's third landing: a pocket in the wall at floor 1 (y = 1 + fh)
    hy = 1 + min(floors - 1, 1) * fh
    p.box(tr + 1, hy, -1, tr + 3, hy + 2, 1, "h_air")
    p.hollow(tr, hy - 1, -2, tr + 4, hy + 3, 2, "wall") if True else None
    p.box(tr + 1, hy, -1, tr + 3, hy + 2, 1, "h_air")
    p.set(tr, hy, 0, "h_air"); p.set(tr, hy + 1, 0, "h_air")
    heart = (-1, top_y + 2, 0)
    idol = (1, 1, -1)
    rift = None
    if t == 3:
        p.box(-6, -7, -6, 6, -3, 6, "air")
        p.walls(-7, -8, -7, 7, -2, 7, "wall")
        p.box(-6, -8, -6, 6, -8, 6, "floor")
        for yy in range(-7, 1):
            p.set(-tr + 1, yy, -tr + 1, "mc:ladder[facing=south]")
        p.set(-tr + 1, 0, -tr + 1, "mc:ladder[facing=south]")
        rift = (0, -7, 0)
    p.seam(R, depth)
    p.erode(0.3)
    p.standard_markers(R, heart, idol, hidden_chest=(tr + 2, hy, 0), rift=rift)
    return p


def library(t: int, seed: int, v: int = 0, module: bool = False) -> Plan:
    p = Plan(f"library_{['', 'raft', 'ruin', 'hold'][t]}", t, seed)
    p.module, p.variant = module, v
    R = {1: 6, 2: 13, 3: 20}[t]
    depth = {1: 4, 2: 7, 3: 10}[t]
    p.keel(R, depth)
    hw = {1: 3, 2: 9, 3: 13}[t]
    hd = {1: 5, 2: 12, 3: 16}[t]
    if p.variant == 1:
        hw, hd = hd - 1, hw + 1          # a wide reading room instead of a long hall
    elif p.variant == 2 and t > 1:
        hd -= 3
    H = {1: 4, 2: 7, 3: 7}[t]
    p.box(-hw - 1, 0, -hd - 1, hw + 1, 0, hd + 1, "floor")
    p.walls(-hw, 1, -hd, hw, H, hd, "wall")
    for x in range(-hw, hw + 1, 3 if t > 1 else 2):
        p.column(x, 1, -hd, H, "beam"); p.column(x, 1, hd, H, "beam")
    for z in range(-hd, hd + 1, 3 if t > 1 else 2):
        p.column(-hw, 1, z, H, "beam"); p.column(hw, 1, z, H, "beam")
    # windows high on the long walls
    for z in range(-hd + 2, hd - 1, 3):
        p.set(-hw, H - 1, z, "glass"); p.set(hw, H - 1, z, "glass")
    # roof, half fallen in
    for x in range(-hw, hw + 1):
        for z in range(-hd, hd + 1):
            if p.rng.random() < (0.55 if t == 1 else 0.7):
                p.set(x, H + 1, z, "roof")
    # shelves in rows
    for x in range(-hw + 2, hw - 1, 3):
        for z in range(-hd + 2, hd - 2):
            if z % 5 == 0:
                continue
            for y in range(1, min(H - 1, 4)):
                p.set(x, y, z, "mc:bookshelf" if p.rng.random() > 0.2 else "mc:chiseled_bookshelf")
    p.box(-1, 1, hd, 1, 3, hd, "air")
    # lectern with the guaranteed page, facing the door
    p.set(0, 1, -hd + 2, "mc:lectern[facing=south]")
    if t >= 2:   # a gallery floor
        g = 3
        p.box(-hw + 1, g + 1, -hd + 1, -hw + 2, g + 1, hd - 1, "slab_top")
        p.box(hw - 2, g + 1, -hd + 1, hw - 1, g + 1, hd - 1, "slab_top")
        for z in range(-hd + 1, hd, 4):
            p.set(-hw + 2, g + 2, z, "fence"); p.set(hw - 2, g + 2, z, "fence")
        for s in range(g):
            p.set(-hw + 1 + 1, 1 + s, hd - 2 - s, "stair_n")
    # hidden room behind a false bookshelf in the east wall
    p.box(hw + 1, 1, -2, hw + 3, 3, 2, "h_air")
    p.walls(hw + 1, 1, -3, hw + 4, 4, 3, "wall")
    p.box(hw + 1, 1, -2, hw + 3, 3, 2, "h_air")
    p.set(hw + 1, 4, 0, "roof")
    p.set(hw, 1, 0, "h_air"); p.set(hw, 2, 0, "h_mc:bookshelf")   # the false shelf: one gap under a shelf
    heart = (0, 1, -hd + 1)
    idol = (1, 1, -hd + 2)
    rift = None
    if t == 3:
        p.box(-8, -7, -8, 8, -2, 8, "air")
        p.walls(-9, -8, -9, 9, -1, 9, "wall")
        p.box(-8, -8, -8, 8, -8, 8, "floor")
        crypt_stair(p, -7, 7, 1, -8)
        rift = (0, -7, 0)
        for x in range(-7, 8, 3):
            for y in range(-7, -4):
                p.set(x, y, -8, "mc:bookshelf")
    p.seam(R, depth)
    p.erode(0.2)
    p.standard_markers(max(hw, hd) + 1, heart, idol, hidden_chest=(hw + 2, 1, 0), rift=rift)
    return p


def forge(t: int, seed: int, v: int = 0, module: bool = False) -> Plan:
    p = Plan(f"forge_{['', 'raft', 'ruin', 'hold'][t]}", t, seed)
    p.module, p.variant = module, v
    R = {1: 7, 2: 14, 3: 20}[t]
    depth = {1: 4, 2: 7, 3: 10}[t]
    p.keel(R, depth); p.deck(R)
    w = {1: 4, 2: 8, 3: 11}[t] - (1 if p.variant == 1 else 0)
    H = {1: 4, 2: 6, 3: 7}[t] + (1 if p.variant == 2 and t > 1 else 0)
    # open workshop: back wall + side half-walls + beams carrying a roof
    p.box(-w, 1, -w, w, H, -w, "wall")
    p.box(-w, 1, -w, -w, 2, w, "wall2"); p.box(w, 1, -w, w, 2, w, "wall2")
    for x in (-w, w):
        for z in range(-w, w + 1, 4):
            p.column(x, 1, z, H, "beam")
    for x in range(-w, w + 1):
        for z in range(-w, w + 1):
            if (x + z) % 7 != 0 or t == 1:
                p.set(x, H + 1, z, "roof")
    # chimney
    ch = {1: 4, 2: 7, 3: 11}[t]
    p.hollow(-w + 1, 1, -w - 2, -w + 3, H + ch, -w, "wall")
    p.set(-w + 2, 1, -w - 1, "mc:campfire[lit=false]")
    # anvil + quench pool + tool on the anvil
    p.set(0, 1, 0, "mc:anvil[facing=east]")
    p.set(0, 0, 0, "metal")
    p.box(2, 0, -1, 4, 0, 1, "mc:water"); p.walls(1, 0, -2, 5, 0, 2, "trim"); p.box(2, 0, -1, 4, 0, 1, "mc:water")
    p.set(-2, 1, -w + 1, "mc:blast_furnace[facing=south]"); p.set(-1, 1, -w + 1, "mc:smithing_table")
    p.set(1, 1, -w + 1, "mc:grindstone[face=floor,facing=south]")
    if t >= 2:
        for x in range(-w + 2, w - 1, 3):
            p.set(x, 1, w - 1, "metal"); p.set(x, 2, w - 1, "mc:chain")
        p.box(-w + 1, H - 1, -w + 1, w - 1, H - 1, -w + 1, "mc:chain")
    # hidden room below the anvil
    p.box(-1, -3, -1, 1, -1, 1, "h_air")
    p.set(0, 0, 0, "h_mc:iron_trapdoor[half=top]")
    p.set(0, -2, 0, "h_air")
    heart = (0, 1, -w + 1)
    idol = (-1, 1, 1)
    rift = None
    if t == 3:
        p.box(-7, -8, -7, 7, -4, 7, "air")
        p.walls(-8, -9, -8, 8, -3, 8, "wall")
        p.box(-7, -9, -7, 7, -9, 7, "floor")
        p.box(-3, -9, -3, 3, -9, 3, "mc:magma_block")
        p.box(-2, -9, -2, 2, -9, 2, "floor")
        crypt_stair(p, 6, 6, 1, -9)
        rift = (0, -8, 0)
    p.seam(R, depth)
    p.erode(0.25)
    p.standard_markers(R, heart, idol, hidden_chest=(0, -2, -1), rift=rift)
    return p


def garden(t: int, seed: int, v: int = 0, module: bool = False) -> Plan:
    p = Plan(f"garden_{['', 'raft', 'ruin', 'hold'][t]}", t, seed)
    p.module, p.variant = module, v
    R = {1: 7, 2: 14, 3: 22}[t]
    depth = {1: 4, 2: 6, 3: 9}[t]
    p.keel(R, depth); p.deck(R, key="soil")
    # terraces stepping down from the centre
    levels = {1: 2, 2: 3, 3: 4}[t] - (1 if p.variant == 1 and t > 1 else 0)
    for lv in range(levels):
        rr = R - 2 - lv * (R // (levels + 1))
        p.disc(0, lv + 1, 0, rr, "soil")
        p.ring(0, lv + 1, 0, rr, "trim")
        for i in range(8 + 4 * lv):
            a = i / (8 + 4 * lv) * math.tau
            x, z = round(math.cos(a) * (rr - 1)), round(math.sin(a) * (rr - 1))
            p.set(x, lv + 2, z, p.rng.choice(["mc:potted_fern", "mc:flower_pot", "mc:potted_azalea_bush", "growth"]))
    top = levels + 1
    # dry fountain on the top terrace
    fr = {1: 2, 2: 3, 3: 4}[t]
    p.disc(0, top, 0, fr, "trim")
    p.disc(0, top, 0, fr - 1, "floor")
    p.ring(0, top + 1, 0, fr, "slab")
    p.column(0, top + 1, 0, 2 + t, "beam", "accent")
    # trellises
    for i in range(3 * t):
        a = i / (3 * t) * math.tau + 0.3
        x, z = round(math.cos(a) * (R - 2)), round(math.sin(a) * (R - 2))
        p.column(x, 1, z, 3, "fence", "slab")
        p.set(x + 1, 1, z, "mc:rooted_dirt")
    # rare seed pots
    for i in range(2 * t):
        a = i / (2 * t) * math.tau + 1.1
        x, z = round(math.cos(a) * 3), round(math.sin(a) * 3)
        p.set(x, top + 1, z, "mc:decorated_pot")
    # hidden room inside the fountain base
    p.box(-1, top - 2, -1, 1, top - 1, 1, "h_air")
    p.set(fr - 1, top, 0, "h_mc:spruce_trapdoor[half=top,facing=west]")
    p.box(fr - 1, top - 2, 0, fr - 1, top - 1, 0, "h_air")
    heart = (-fr - 1, top, 0)      # on the top terrace (y = top - 1), beside the fountain
    idol = (fr + 1, top, 0)
    rift = None
    if t == 3:
        p.box(-8, -7, -8, 8, -3, 8, "air")
        p.walls(-9, -8, -9, 9, -2, 9, "wall")
        p.box(-8, -8, -8, 8, -8, 8, "soil")
        p.box(-8, -7, -8, 8, -7, 8, "growth") if False else None
        for x in range(-7, 8, 3):
            for z in (-7, 7):
                p.column(x, -7, z, 4, "beam")
        # the stair starts on whichever terrace covers its landing
        land = [y for y in range(0, top + 1) if p.get(7, y, 7) in ("soil", "trim", "floor")]
        crypt_stair(p, 7, 6, 1 + max(land, default=0), -8)
        rift = (0, -7, 0)
    p.seam(R, depth)
    p.erode(0.2)
    p.standard_markers(R, heart, idol, hidden_chest=(0, top - 2, 0), rift=rift, center=(0, top, -fr - 1))
    return p


def vault(t: int, seed: int, v: int = 0, module: bool = False) -> Plan:
    p = Plan(f"vault_{['', 'raft', 'ruin', 'hold'][t]}", t, seed)
    p.module, p.variant = module, v
    R = {1: 7, 2: 14, 3: 21}[t]
    depth = {1: 4, 2: 7, 3: 10}[t]
    p.keel(R, depth); p.deck(R)
    s = {1: 3, 2: 6, 3: 8}[t] - (1 if p.variant == 1 and t > 1 else 0)
    H = {1: 4, 2: 6, 3: 8}[t] + (1 if p.variant == 2 else 0) - (1 if p.variant == 1 else 0)
    p.fill = "trim"
    # sealed stone box, one door with a thread lock
    p.hollow(-s, 0, -s, s, H + 1, s, "trim")
    p.box(-s + 1, 0, -s + 1, s - 1, 0, s - 1, "floor")
    for c in ((-s, -s), (s, -s), (-s, s), (s, s)):
        p.column(c[0], 1, c[1], H + 2, "beam", "light")
    p.box(-1, 1, s, 1, 3, s, "air")
    p.set(0, 4, s, "seam"); p.set(-1, 4, s, "seam2"); p.set(1, 4, s, "seam2")
    # door puzzle: a thread lock fills the doorway until both plates are held down at once (Java places the lock)
    for x in (-2, 2):
        p.set(x, 0, s + 1, "floor")
        p.set(x, 1, s + 1, "mc:oak_pressure_plate")
        p.mark("plate", x, 1, s + 1)
    for x in (-1, 0, 1):
        for y in (1, 2, 3):
            p.mark("lock", x, y, s)
    if t >= 2:   # an inner ring of pillars and a vault floor pattern
        for i in range(8):
            a = i / 8 * math.tau
            p.column(round(math.cos(a) * (s - 2)), 1, round(math.sin(a) * (s - 2)), H, "wall2")
        for x in range(-s + 1, s):
            for z in range(-s + 1, s):
                if (x + z) % 2 == 0:
                    p.set(x, 0, z, "accent" if (x * z) % 3 == 0 else "floor")
        # outer yard walls, knee-high
        p.ring(0, 1, 0, R - 2, "wall")
        for i in range(4):
            a = i / 4 * math.tau + math.pi / 4
            p.set(round(math.cos(a) * (R - 2)), 1, round(math.sin(a) * (R - 2)), "air")
    # hidden room: a second vault wall, 1 block thick, behind the back wall
    p.box(-2, 1, -s - 3, 2, 3, -s - 1, "h_air")
    p.walls(-3, 0, -s - 4, 3, 4, -s, "trim")
    p.box(-2, 0, -s - 3, 2, 0, -s - 1, "floor")
    p.box(-2, 1, -s - 3, 2, 3, -s - 1, "h_air")
    p.box(-2, 4, -s - 3, 2, 4, -s - 1, "trim")
    p.set(0, 1, -s, "h_air"); p.set(0, 2, -s, "h_air")
    heart = (0, 1, -s + 1)
    idol = (0, 1, s - 2)
    rift = None
    if t == 3:
        p.box(-6, -7, -6, 6, -3, 6, "air")
        p.walls(-7, -8, -7, 7, -2, 7, "trim")
        p.box(-6, -8, -6, 6, -8, 6, "floor")
        p.box(s - 2, -7, s - 2, s - 1, 0, s - 1, "air")
        for yy in range(-7, 1):
            p.set(s - 1, yy, s - 1, "mc:ladder[facing=north]")
        rift = (0, -7, 0)
    p.seam(R, depth)
    p.erode(0.15)
    p.standard_markers(R, heart, idol, hidden_chest=(0, 1, -s - 2), rift=rift, center=(0, 1, 0))
    return p


CORES = {"shrine": shrine, "watchtower": watchtower, "library": library, "forge": forge, "garden": garden, "vault": vault}


def heartwreck(seed: int) -> Plan:
    """The heart of the old world: nine districts round a central hall. One per Clowder, hand-shaped here."""
    p = Plan("heartwreck", 4, seed)
    R = 31
    p.keel(R, 14); p.deck(R)
    strands = ["soil", "stone", "sprout", "claw", "spark", "clock", "swarm", "sigil", "spindle"]
    # central hall
    p.hollow(-8, 0, -8, 8, 12, 8, "wall", inner="air")
    p.box(-7, 0, -7, 7, 0, 7, "floor")
    for c in ((-8, -8), (8, -8), (-8, 8), (8, 8)):
        p.column(c[0], 1, c[1], 16, "beam", "seam")
    for i in range(4):
        dx, dz = [(0, -1), (1, 0), (0, 1), (-1, 0)][i]
        p.box(dx * 8 - (1 if dx == 0 else 0), 1, dz * 8 - (1 if dz == 0 else 0), dx * 8 + (1 if dx == 0 else 0), 4, dz * 8 + (1 if dz == 0 else 0), "air")
    p.disc(0, 13, 0, 7, "roof")
    p.disc(0, 13, 0, 3, "glass")
    p.set(0, 1, 0, "seam2"); p.set(0, 2, 0, "accent")
    # nine districts: each a small raised plaza with a pillar, in its own literal Strand material
    mats = {"soil": "mc:mud_bricks", "stone": "mc:deepslate_bricks", "sprout": "mc:mossy_stone_bricks", "claw": "mc:polished_blackstone_bricks",
            "spark": "mc:cut_copper", "clock": "mc:dark_oak_planks", "swarm": "mc:honeycomb_block", "sigil": "mc:purpur_block", "spindle": "mc:spruce_planks"}
    for i, st in enumerate(strands):
        a = i / 9 * math.tau
        cx, cz = round(math.cos(a) * 20), round(math.sin(a) * 20)
        p.disc(cx, 1, cz, 5, mats[st])
        p.ring(cx, 2, cz, 5, "slab")
        for k in range(6):
            b = k / 6 * math.tau
            p.column(cx + round(math.cos(b) * 4), 2, cz + round(math.sin(b) * 4), 3 + (k % 3), mats[st])
        p.mark("district", cx, 2, cz, i)
        # walkway to the hall
        for s in range(9, 16):
            x, z = round(math.cos(a) * s), round(math.sin(a) * s)
            p.set(x, 0, z, "trim")
    p.fill = "wall"
    p.mark("chest", 0, 1, -5, 1)
    p.mark("idol", 0, 1, 5, 0)
    p.mark("center", 0, 1, 3, 0)
    p.mark("echo", 3, 1, 0, 0)
    cells = p.free_cells()
    p.spread("chest", 8, cells, min_gap=6)
    p.spread("mob", 6, cells)
    p.mark("pillar", 0, 1, 0, 0) if False else None
    for i, (dx, dz) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
        for rr in range(R + 2, 0, -1):
            x, z = dx * rr, dz * rr
            if p.get(x, 0, z) and p.get(x, 1, z) is None:
                p.mark("dock", x, 0, z, i)
                break
    p.seam(R, 14)
    return p




# ==================================================================== annexes (shared, placed by the composer)
#
# Small ruins the Java composer (WreckComposer) scatters around a wreck's core, rotated in 90° steps. y 0 is deck
# level (an annex may lay its own floor there), everything else stands on it. Radius <= 4, height <= 7.

def annex(name, seed):
    p = Plan(name, 0, seed)
    p.module = True
    return p


def a_ruined_wall(seed):
    p = annex("ruined_wall", seed)
    for x in range(-3, 4):
        h = 1 + int(3 * (1 - abs(x) / 4) + p.rng.random() * 1.5)
        p.column(x, 1, 0, h, "wall" if (x + h) % 3 else "wall2")
    p.set(-1, 2, 0, "glass"); p.set(-1, 1, 1, "slab"); p.set(2, 1, -1, "keel2")
    p.mark("mob", 0, 1, 2)
    return p


def a_broken_arch(seed):
    p = annex("broken_arch", seed)
    for x in (-2, 2):
        p.column(x, 1, 0, 4, "trim")
    p.box(-2, 5, 0, 0, 5, 0, "trim"); p.set(1, 5, 0, "slab")        # the right half of the lintel fell
    p.set(1, 1, 1, "trim"); p.set(2, 1, 2, "slab")
    p.set(-2, 6, 0, "seam")
    return p


def a_watch_post(seed):
    p = annex("watch_post", seed)
    for x, z in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        p.column(x, 1, z, 4, "beam")
    p.box(-1, 5, -1, 1, 5, 1, "floor")
    p.set(0, 6, 0, "light")
    for y in range(1, 5):
        p.set(0, y, -2, "mc:ladder[facing=north]") if False else None
    p.set(0, 1, 0, "mc:barrel[facing=up]")
    p.mark("chest", 0, 6, 1, 0)
    return p


def a_shed(seed):
    p = annex("shed", seed)
    p.box(-2, 0, -2, 2, 0, 2, "floor")
    p.walls(-2, 1, -2, 2, 3, 2, "wall2")
    p.box(-1, 1, 2, 0, 2, 2, "air")
    for x in range(-3, 4):
        p.set(x, 4, -1, "roof"); p.set(x, 4, 0, "roof") if x % 3 else None; p.set(x, 4, 1, "roof")
    p.mark("chest", 1, 1, -1, 0)
    return p


def a_well(seed):
    p = annex("well", seed)
    p.ring(0, 1, 0, 2, "trim")
    p.box(-1, 0, -1, 1, -2, 1, "x_air")
    p.walls(-2, -2, -2, 2, -1, 2, "keel"); p.box(-2, -3, -2, 2, -3, 2, "keel")   # its own basin: near a rim the keel is too thin to hold water
    p.set(0, -2, 0, "mc:water")
    for x in (-2, 2):
        p.column(x, 2, 0, 2, "fence")
    p.box(-2, 4, 0, 2, 4, 0, "beam"); p.set(0, 3, 0, "mc:chain")
    return p


def a_statue(seed):
    p = annex("statue", seed)
    p.box(-1, 1, -1, 1, 1, 1, "trim")
    p.column(0, 2, 0, 3, "accent"); p.set(0, 5, 0, "light")
    p.set(1, 3, 0, "accent"); p.set(-1, 4, 0, "slab")                    # one arm raised, the other gone
    p.mark("mob", 2, 1, 1)
    return p


def a_garden_bed(seed):
    p = annex("garden_bed", seed)
    p.walls(-2, 1, -2, 2, 1, 2, "trim")
    p.box(-1, 1, -1, 1, 1, 1, "soil")
    for x in (-1, 1):
        for z in (-1, 1):
            p.set(x, 2, z, p.rng.choice(["growth", "mc:potted_fern", "mc:sweet_berry_bush[age=2]"]))
    p.set(0, 2, 0, "mc:composter")
    return p


def a_stair_ruin(seed):
    p = annex("stair_ruin", seed)
    for i in range(5):
        p.box(-1, 1, i - 2, 1, 1 + i, i - 2, "wall")
        p.set(-1 + (i % 2), 2 + i, i - 2, "stair_s")
    p.set(1, 6, 2, "light")
    p.mark("chest", 0, 2, -2, 0) if False else None
    return p


def a_tower_stump(seed):
    p = annex("tower_stump", seed)
    p.ring(0, 1, 0, 3, "wall")
    for y in range(2, 6):
        for x in range(-3, 4):
            for z in range(-3, 4):
                d = (x * x + z * z) ** 0.5
                if 2.2 < d <= 3.3 and p.rng.random() < 0.9 - y * 0.15:
                    p.set(x, y, z, "wall" if y % 2 else "wall2")
    p.box(-1, 1, 3, 1, 3, 3, "air")
    p.box(-2, 0, -2, 2, 0, 2, "floor")
    p.mark("chest", 0, 1, -1, 0)
    return p


def a_column_field(seed):
    p = annex("column_field", seed)
    for x, z in ((-3, -3), (3, -3), (-3, 3), (3, 3), (0, 0)):
        h = p.rng.randint(1, 5)
        p.column(x, 1, z, h, "beam", "trim" if h > 3 else None)
    p.set(1, 1, -2, "slab"); p.set(-2, 1, 1, "slab")
    p.mark("mob", 1, 1, 2)
    return p


def a_market_stall(seed):
    p = annex("market_stall", seed)
    for x, z in ((-2, -1), (2, -1), (-2, 1), (2, 1)):
        p.column(x, 1, z, 3, "fence")
    for x in range(-3, 4):
        for z in (-2, -1, 0, 1, 2):
            if p.rng.random() < 0.8:
                p.set(x, 4, z, "mc:cyan_wool" if (x + z) % 2 else "mc:white_wool")
    p.box(-1, 1, 0, 1, 1, 0, "mc:barrel[facing=up]")
    p.mark("chest", 0, 1, -1, 0)
    return p


def a_gazebo(seed):
    p = annex("gazebo", seed)
    p.disc(0, 0, 0, 3, "floor")
    for k in range(6):
        import math as _m
        a = k / 6 * _m.tau
        p.column(round(_m.cos(a) * 3), 1, round(_m.sin(a) * 3), 3, "fence")
    p.disc(0, 4, 0, 3, "slab"); p.disc(0, 5, 0, 1, "roof")
    p.set(0, 1, 0, "mc:lectern[facing=south]") if False else p.set(0, 1, 0, "accent")
    return p


def a_obelisk(seed):
    p = annex("obelisk", seed)
    p.box(-1, 1, -1, 1, 1, 1, "trim")
    p.column(0, 2, 0, 5, "wall")
    for y in (3, 5):
        p.set(0, y, -1, "seam" if y == 3 else "seam2")
    p.set(0, 7, 0, "light")
    return p


def a_lantern_row(seed):
    p = annex("lantern_row", seed)
    for x in range(-4, 5, 2):
        h = 2 + (x // 2) % 2
        if p.rng.random() < 0.8:
            p.column(x, 1, 0, h, "fence", "light")
    p.mark("mob", 0, 1, 2)
    return p


def a_fallen_bell(seed):
    p = annex("fallen_bell", seed)
    p.box(-2, 1, -1, 2, 1, -1, "beam"); p.box(-2, 1, 1, 2, 1, 1, "beam")
    p.set(0, 1, 0, "mc:bell[attachment=floor,facing=north]")
    p.column(-3, 1, 0, 2, "beam"); p.set(3, 1, 0, "slab")
    return p


def a_cistern(seed):
    p = annex("cistern", seed)
    p.box(-2, 0, -2, 2, -2, 2, "x_air")
    p.walls(-3, -2, -3, 3, 1, 3, "wall")
    p.box(-2, -2, -2, 2, -2, 2, "floor")
    p.box(-1, -1, -1, 1, -1, 1, "mc:water")
    p.box(-1, 1, 3, 1, 1, 3, "air")
    p.mark("chest", 2, -1, 2, 0)
    return p


def a_kiln(seed):
    p = annex("kiln", seed)
    p.hollow(-2, 1, -2, 2, 4, 2, "metal")
    p.box(-1, 1, 2, 1, 2, 2, "air")
    p.set(0, 1, 0, "mc:campfire[lit=false]"); p.column(0, 5, 0, 2, "metal")
    p.mark("mob", 3, 1, 0)
    return p


def a_loom_ruin(seed):
    p = annex("loom_ruin", seed)
    for x in (-2, 2):
        p.column(x, 1, 0, 4, "beam")
    p.box(-2, 4, 0, 2, 4, 0, "beam")
    for x in range(-1, 2):
        p.column(x, 1, 0, 3, "mc:cyan_wool" if x % 2 else "mc:yellow_wool") if p.rng.random() < 0.7 else None
    p.set(0, 1, 1, "mc:loom[facing=south]")
    p.mark("chest", -1, 1, 1, 0)
    return p


ANNEXES = [a_ruined_wall, a_broken_arch, a_watch_post, a_shed, a_well, a_statue, a_garden_bed, a_stair_ruin, a_tower_stump,
           a_column_field, a_market_stall, a_gazebo, a_obelisk, a_lantern_row, a_fallen_bell, a_cistern, a_kiln, a_loom_ruin]
VARIANTS = 3


def read_ncga(path: Path) -> Plan:
    """Read an NCGA plan back (composed previews exported by the game tests)."""
    b = path.read_bytes()
    o = 0
    def u(fmt):
        nonlocal o
        v = struct.unpack_from(fmt, b, o); o += struct.calcsize(fmt); return v
    magic, ver, nk = u("<IIH")
    keys = []
    for _ in range(nk):
        (n,) = u("<H"); keys.append(b[o:o + n].decode()); o += n
    (n,) = u("<I")
    p = Plan(path.stem, 9, 0)
    for _ in range(n):
        x, y, z, k = u("<hhhB")
        p.v[(x, y, z)] = keys[k]
    (n,) = u("<H"); p.fill = b[o:o + n].decode(); o += n
    (m,) = u("<H")
    for _ in range(m):
        (n,) = u("<H"); kind = b[o:o + n].decode(); o += n
        x, y, z, d = u("<hhhB")
        p.markers.append((kind, x, y, z, d))
    return p


# ==================================================================== render

ROLE_RGB = {
    "keel": (92, 84, 78), "keel2": (70, 64, 60), "soil": (96, 72, 48), "floor": (150, 130, 104), "wall": (130, 122, 116),
    "wall2": (104, 82, 60), "trim": (180, 170, 150), "beam": (84, 62, 44), "roof": (70, 70, 84), "accent": (110, 150, 80),
    "light": (250, 220, 140), "glass": (60, 70, 90), "growth": (80, 140, 60), "metal": (190, 150, 90), "fence": (84, 62, 44),
    "slab": (160, 150, 130), "seam": (60, 210, 190), "seam2": (230, 190, 70),
}


def rgb(key: str):
    if key == "x_air":
        return None
    if key.startswith("h_"):
        return (200, 60, 200)
    if key.startswith("mc:"):
        k = key[3:]
        if "water" in k: return (50, 90, 200)
        if "wool" in k: return (60, 190, 190) if "cyan" in k else (230, 200, 60)
        if "shelf" in k: return (150, 100, 60)
        if "magma" in k: return (200, 90, 30)
        return (170, 170, 170)
    if key.startswith("stair"):
        return ROLE_RGB["slab"]
    return ROLE_RGB.get(key, (140, 140, 140))


def render(plan: Plan, path: Path, scale=6):
    from PIL import Image, ImageDraw
    pts = list(plan.v.items())
    xs = [p[0][0] for p in pts]; ys = [p[0][1] for p in pts]; zs = [p[0][2] for p in pts]
    def iso(x, y, z):
        return ((x - z) * scale, (x + z) * scale * 0.5 - y * scale)
    corners = [iso(x, y, z) for x in (min(xs), max(xs) + 1) for y in (min(ys), max(ys) + 1) for z in (min(zs), max(zs) + 1)]
    minx = min(c[0] for c in corners) - 20; miny = min(c[1] for c in corners) - 40
    W = int(max(c[0] for c in corners) - minx + 20); H = int(max(c[1] for c in corners) - miny + 20)
    img = Image.new("RGB", (W, H), (22, 26, 34)); d = ImageDraw.Draw(img)
    for (x, y, z), k in sorted(pts, key=lambda kv: (kv[0][0] + kv[0][2], kv[0][1])):
        c = rgb(k)
        if c is None:
            continue
        def P(a, b, cc):
            X, Y = iso(a, b, cc); return (X - minx, Y - miny)
        top = [P(x, y + 1, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)]
        left = [P(x, y + 1, z + 1), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1), P(x, y, z + 1)]
        right = [P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1), P(x + 1, y, z)]
        d.polygon(top, fill=c)
        d.polygon(left, fill=tuple(int(v * 0.72) for v in c))
        d.polygon(right, fill=tuple(int(v * 0.55) for v in c))
    for kind, x, y, z, data in plan.markers:
        X, Y = iso(x + 0.5, y + 0.5, z + 0.5); X -= minx; Y -= miny
        col = {"chest": (255, 200, 40), "spawner": (230, 40, 40), "pillar": (60, 220, 255), "idol": (255, 255, 255), "dock": (40, 255, 120),
               "rift": (200, 60, 255), "echo": (255, 150, 220), "center": (255, 255, 0), "mob": (160, 60, 60), "district": (255, 120, 0)}.get(kind, (255, 255, 255))
        d.ellipse([X - 3, Y - 3, X + 3, Y + 3], fill=col, outline=(0, 0, 0))
    d.text((8, 8), f"{plan.name}  blocks={len(plan.v)}  markers={len(plan.markers)}", fill=(230, 230, 230))
    img.save(path)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", default="")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--render-dir", default="", help="render every .ncga in this folder (composed previews) to a contact sheet")
    a = ap.parse_args()
    if a.render_dir:
        rd = Path(a.render_dir)
        from PIL import Image
        imgs = [render(read_ncga(f), f.with_suffix(".png"), scale=4) for f in sorted(rd.glob("*.ncga"))]
        thumbs = []
        for im in imgs:
            im = im.copy(); im.thumbnail((300, 300)); thumbs.append(im)
        cols = 6; rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 300, rows * 300), (14, 16, 22))
        for i, im in enumerate(thumbs):
            sheet.paste(im, ((i % cols) * 300 + (300 - im.width) // 2, (i // cols) * 300 + (300 - im.height) // 2))
        sheet.save(rd / "composed_sheet.png")
        print("sheet ->", rd / "composed_sheet.png")
        return
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    plans = []
    for old in out.glob("*_*.ncga"):
        if old.stem != "heartwreck":
            old.unlink()                              # the fixed 18 plans are gone: wrecks are composed in game
    (out / "core").mkdir(exist_ok=True); (out / "annex").mkdir(exist_ok=True)
    for ci, (name, fn) in enumerate(CORES.items()):
        for tname, t in TIERS.items():
            for v in range(VARIANTS):
                plan = fn(t, seed=1000 + ci * 10 + t + v * 101, v=v, module=True)
                plan.name = f"{name}_{tname}_{v}"
                assert plan.v, plan.name
                kinds = {m[0] for m in plan.markers}
                assert {"chest", "idol"} <= kinds, (plan.name, kinds)
                if t == 3:
                    assert "rift" in kinds, plan.name
                r = max((x * x + z * z) ** 0.5 for x, y, z in plan.v)
                plan.write(out / "core" / f"{plan.name}.ncga")
                plans.append(plan)
                print(f"core  {plan.name:22s} r={r:4.1f} blocks={len(plan.v):6d} markers={len(plan.markers)}")
    for i, fn in enumerate(ANNEXES):
        plan = fn(7000 + i)
        r = max((x * x + z * z) ** 0.5 for x, y, z in plan.v)
        hgt = max(y for x, y, z in plan.v)
        assert r <= 4.9 and hgt <= 7, (plan.name, r, hgt)
        plan.write(out / "annex" / f"{plan.name}.ncga")
        plans.append(plan)
        print(f"annex {plan.name:22s} r={r:4.1f} h={hgt} blocks={len(plan.v):5d}")
    hw = heartwreck(4242)
    xs = [p[0] for p in hw.v]; ys = [p[1] for p in hw.v]
    hw.write(out / "heartwreck.ncga"); plans.append(hw)
    print(f"{'heartwreck':18s} {max(xs)-min(xs)+1:3d}x{max(ys)-min(ys)+1:3d}  blocks={len(hw.v):6d}  markers={len(hw.markers)}")
    if a.render:
        from PIL import Image
        rd = Path(a.render); rd.mkdir(parents=True, exist_ok=True)
        imgs = [render(p, rd / f"{p.name}.png", scale=6 if p.tier < 3 else 4) for p in plans]
        thumbs = []
        for im in imgs:
            im = im.copy(); im.thumbnail((420, 420)); thumbs.append(im)
        cols = 3; rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 420, rows * 420), (14, 16, 22))
        for i, im in enumerate(thumbs):
            sheet.paste(im, ((i % cols) * 420 + (420 - im.width) // 2, (i // cols) * 420 + (420 - im.height) // 2))
        sheet.save(rd / "wreck_contact_sheet.png")
        print("renders ->", rd)


if __name__ == "__main__":
    main()
