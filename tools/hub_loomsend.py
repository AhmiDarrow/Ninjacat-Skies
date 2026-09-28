"""Loom's End: the Clowder Hall hub, rebuilt as the last knot at the edge of a cut world.

A voxel canvas (last write wins) compressed into the box plan TownPlan applies once per hub revision. Fences, walls
and panes get their connections from their neighbours here, because the plan is written without block updates.

Layout (y 63 is the ground; north is -z; players arrive at 0.5 65 5.5 looking north):
  - the ceremony pad (|x|,|z| <= 7) keeps its chest, lectern, signs, beacon and reweave ring pillars (KEEP cells);
  - the Knot: a round plaza, nine tribe spokes and nine strand stones around the pad;
  - the Cut Loom north of the plaza, its warp severed mid-air, and the broken gate-path beyond it;
  - Market Street east and west: the peoples' shops with counters, wares on the walls, keepers behind the counter;
  - the Purring Hearth, the Stitchers' Chapel, the Leaf Archive, the Gate Lookout, Esther's Roost and the
    Whiskerwind Road gate; the Drum Circle, the paddock and garden, the Artificers' Yard, the apiary, the Old
    Grove, the tribe homes and the Windward Mill; a fountain in the south lawn, islets drifting in the void.
"""
import json
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOP = ROOT / 'pack/overrides/kubejs/data/ninjacatskies/tribalpower/dock_shop'
Y = 63

TRIBES = ['soil', 'stone', 'sprout', 'claw', 'spark', 'clock', 'swarm', 'sigil', 'spindle']
TRIBE_NAMES = {'soil': 'Pad-keepers', 'stone': 'Grit-singers', 'sprout': 'Rootbinders', 'claw': 'Edge-walkers',
               'spark': 'Drumhearts', 'clock': 'Pattern-weavers', 'swarm': 'Colony-keepers', 'sigil': 'Seal-carvers',
               'spindle': 'Loom-stitchers'}
# Nearest dye to each canonical tribe colour (tools/art_tribe_glyphs.py).
DYE = {'soil': 'brown', 'stone': 'light_gray', 'sprout': 'green', 'claw': 'red', 'spark': 'orange',
       'clock': 'blue', 'swarm': 'yellow', 'sigil': 'purple', 'spindle': 'cyan'}

# Ceremony pad pieces placed in Java (ModDimensions / ReweaveRing): the plan never writes these cells.
RING = [(6, -4), (6, -1), (6, 2), (6, 5), (-6, -4), (-6, -1), (-6, 2), (-6, 5), (3, -6), (-3, -6), (3, 6), (-3, 6)]


def keep_cells():
    keep = {(0, 62, 0), (0, 64, 1), (1, 64, 1), (0, 64, 2), (0, 64, -2), (0, 64, -1),   # marker, lectern, chest, signs
            (0, 65, -4)}                                          # beacon
    keep |= {(0, y, 0) for y in range(50, 62)}                   # one revision marker per town plan, 0,61-N,0
    keep |= {(x, 64, z) for x in (-1, 0, 1) for z in (-5, -4, -3)}   # beacon base
    for dx, dz in RING:
        keep |= {(dx, 64, dz), (dx, 65, dz)}
        if abs(dx) == 6:
            keep.add((dx - 1 if dx > 0 else dx + 1, 64, dz))
        else:
            keep.add((dx, 64, dz - 1 if dz > 0 else dz + 1))
    return keep


NONFULL = ('air', '_slab', '_stairs', '_fence', '_wall', 'pane', 'iron_bars', 'lantern', 'torch', 'potted', 'flower_pot',
           'carpet', 'sign', 'door', 'chain', 'button', 'plate', 'rail', '_bed', 'banner', 'candle', 'campfire',
           'sapling', 'grass', 'fern', 'petals', 'roots', 'dripstone', 'lichen', 'vine', 'cluster', '_bud', 'end_rod',
           'bell', 'anvil', 'azalea', 'water', 'lava', 'ladder', 'lectern', 'enchanting', 'brewing', 'cauldron',
           'composter', 'decorated_pot', 'spore', 'leaves', 'chest', 'dandelion', 'poppy', 'orchid', 'allium',
           'bluet', 'tulip', 'daisy', 'cornflower', 'lily', 'grindstone', 'stonecutter', 'hopper', 'bamboo',
           'lilac', 'peony', 'rose_bush', 'sunflower', 'wheat', 'carrots', 'potatoes', 'beetroots', 'farmland',
           'moss_carpet', 'head', 'skull', 'scaffolding', 'sea_pickle', 'pointed', 'amethyst_cluster', 'frame',
           'crop', 'bench', 'table', 'stool', 'chair', 'shelf', 'rack', 'urn', 'totem', 'bowl', 'pedestal', 'glyph',
           'cog', 'shaft', 'sail', 'bearing', 'pot', 'crank', 'coil', 'bridge', 'hammock', 'backpack', 'vane',
           'globe', 'hourglass', 'planter', 'mat', 'plinth', 'idol', 'chime', 'drum', 'brazier', 'altar', 'bloom',
           'board', 'hood', 'oven', 'stove', 'skillet', 'basket', 'sieve', 'crucible', 'fixture', 'panel')


def bid(b):
    return b if ':' in b else 'minecraft:' + b


def base_id(b):
    return b.split('[', 1)[0].split(':', 1)[-1]


# Full cubes whose names happen to contain a NONFULL fragment ('rack' in cracked, 'bell' in bellcap, 'urn' in
# furnace, 'shelf' in bookshelf, 'table' in the crafting tables, 'frame' in Mekanism's teleporter frame).
FULL_ANYWAY = ('cracked_', 'bellcap_log', 'bellcap_planks', 'bellcap_wood', 'furnace', 'furnator', 'bookshelf',
               'crafting_table', 'cartography_table', 'fletching_table', 'smithing_table', 'teleporter_frame')


def is_full(b):
    if b is None:
        return False
    n = base_id(b)
    if any(k in n for k in FULL_ANYWAY):
        return True
    return not any(k in n for k in NONFULL) or n.endswith('_block') and 'slime' not in n and 'honey' not in n


class Canvas:
    def __init__(self, lang_ns='ninjacatpack.hub'):
        self.c = {}
        self.keep = keep_cells()
        self.signs, self.frames, self.residents, self.posts = [], [], [], {}
        self.lang_ns, self.lang = lang_ns, {}
        self.rng = random.Random(9)
        self.paved = set()
        self.surface = set()          # the island's (x, z) cells, filled in by island()

    # -- cells -----------------------------------------------------------------------------------------------------
    def set(self, x, y, z, b):
        if (x, y, z) in self.keep:
            return
        self.c[(x, y, z)] = bid(b)

    def fill(self, x1, y1, z1, x2, y2, z2, b):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, b)

    def get(self, x, y, z):
        return self.c.get((x, y, z))

    def air(self, x, y, z):
        b = self.c.get((x, y, z))
        return b is None or base_id(b) == 'air'

    def pick(self, *choices):
        """Weighted pick: pick(('stone_bricks', 6), ('cracked_stone_bricks', 1))."""
        total = sum(w for _, w in choices)
        r = self.rng.random() * total
        for b, w in choices:
            r -= w
            if r <= 0:
                return b
        return choices[-1][0]

    # -- text and entities -----------------------------------------------------------------------------------------
    def _keys(self, lines):
        base = re.sub(r'[^a-z0-9]+', '_', lines[0].lower()).strip('_').removeprefix('the_')
        slug, n = base, 2
        while any(k.startswith(f'sign.{self.lang_ns}.{slug}.') for k in self.lang):
            slug, n = f'{base}_{n}', n + 1
        keyed = []
        for i, line in enumerate(lines, 1):
            if not line:
                keyed.append('')
                continue
            key = f'sign.{self.lang_ns}.{slug}.{i}'
            self.lang[key] = line
            keyed.append(key)
        return keyed

    def sign(self, x, y, z, block, *lines):
        """block is the full sign state (standing, wall or hanging); lines become lang keys."""
        self.set(x, y, z, block)
        self.signs.append(dict(pos=[x, y, z], lines=self._keys(lines)))

    def frame(self, x, y, z, facing, item, glow=True):
        self.frames.append(dict(pos=[x, y, z], facing=facing, item=item, glow=glow))

    def resident(self, x, y, z, name, kind='minecraft:villager', ai=True, nbt=None, tags=(), show_name=True):
        r = dict(pos=[x + .5, y, z + .5], name=name, type=kind, ai=ai)
        if nbt:
            r['nbt'] = nbt
        if tags:
            r['tags'] = list(tags)
        if not show_name:
            r['show_name'] = False
        self.residents.append(r)

    # -- export ----------------------------------------------------------------------------------------------------
    def connect(self):
        """Fences, walls, panes and bars take their sides from the neighbours, as a block update would."""
        sides = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}

        def kind(b):
            if b is None:
                return None
            n = base_id(b)
            if n.endswith('_fence_gate'):
                return 'gate'
            if n.endswith('_fence'):
                return 'nfence' if n.startswith('nether') else 'fence'
            if n.endswith('_wall') and 'sign' not in n and 'banner' not in n:
                return 'wall'
            if n.endswith('glass_pane') or n == 'iron_bars':
                return 'pane'
            return None

        out = {}
        for (x, y, z), b in self.c.items():
            k = kind(b)
            if k in (None, 'gate') or '[' in b:
                continue
            on = {}
            for s, (dx, dz) in sides.items():
                nb = self.c.get((x + dx, y, z + dz))
                nk = kind(nb)
                if k in ('fence', 'nfence'):
                    ok = nk == k or nk == 'gate' or (is_full(nb) and nk is None)
                elif k == 'wall':
                    ok = nk in ('wall', 'pane', 'gate') or (is_full(nb) and nk is None)
                else:
                    ok = nk in ('pane', 'wall') or (is_full(nb) and nk is None)
                on[s] = ok
            if k == 'wall':
                above = self.c.get((x, y + 1, z))
                straight = (on['north'] and on['south'] and not on['east'] and not on['west']) or \
                           (on['east'] and on['west'] and not on['north'] and not on['south'])
                up = not straight or (above is not None and base_id(above) != 'air')
                st = ','.join(f'{s}={"low" if on[s] else "none"}' for s in sides) + f',up={str(up).lower()}'
            else:
                st = ','.join(f'{s}={str(on[s]).lower()}' for s in sides)
            out[(x, y, z)] = f'{b}[{st}]'
        self.c.update(out)

    def boxes(self, cells):
        rows = {}
        for (x, y, z), b in cells.items():
            rows.setdefault((y, z), []).append((x, b))
        runs = []
        for (y, z), xs in rows.items():
            xs.sort()
            start, prev, cur = xs[0][0], xs[0][0], xs[0][1]
            for x, b in xs[1:]:
                if x == prev + 1 and b == cur:
                    prev = x
                    continue
                runs.append((y, z, start, prev, cur))
                start, prev, cur = x, x, b
            runs.append((y, z, start, prev, cur))
        # merge along z, then along y
        byk = {}
        for y, z, x1, x2, b in runs:
            byk.setdefault((y, x1, x2, b), []).append(z)
        rects = []
        for (y, x1, x2, b), zs in byk.items():
            zs.sort()
            s = p = zs[0]
            for z in zs[1:]:
                if z == p + 1:
                    p = z
                    continue
                rects.append((x1, x2, s, p, y, b))
                s = p = z
            rects.append((x1, x2, s, p, y, b))
        byr = {}
        for x1, x2, z1, z2, y, b in rects:
            byr.setdefault((x1, x2, z1, z2, b), []).append(y)
        out = []
        for (x1, x2, z1, z2, b), ys in byr.items():
            ys.sort()
            s = p = ys[0]
            for y in ys[1:]:
                if y == p + 1:
                    p = y
                    continue
                out.append(dict(**{'from': [x1, s, z1], 'to': [x2, p, z2], 'block': b}))
                s = p = y
            out.append(dict(**{'from': [x1, s, z1], 'to': [x2, p, z2], 'block': b}))
        out.sort(key=lambda o: (o['from'][1], o['from'][2], o['from'][0]))
        return out


class Local:
    """Building-local coordinates: u runs left to right as seen from the street, v runs from the front inward."""
    DIRS = {
        'S': dict(front='south', back='north', right='east', left='west', au='x', av='z'),
        'N': dict(front='north', back='south', right='west', left='east', au='x', av='z'),
        'E': dict(front='east', back='west', right='north', left='south', au='z', av='x'),
        'W': dict(front='west', back='east', right='south', left='north', au='z', av='x'),
    }
    ROT = {'south': 0, 'west': 4, 'north': 8, 'east': 12}

    def __init__(self, cv, face, fx, fz, y=Y):
        self.cv, self.face, self.fx, self.fz, self.y = cv, face, fx, fz, y
        self.d = dict(self.DIRS[face])
        self.d['rot_front'] = self.ROT[self.d['front']]
        self.d['rot_back'] = self.ROT[self.d['back']]

    def xz(self, u, v):
        return {'S': (self.fx + u, self.fz - v), 'N': (self.fx - u, self.fz + v),
                'E': (self.fx - v, self.fz - u), 'W': (self.fx + v, self.fz + u)}[self.face]

    def b(self, block):
        return block.format(**self.d)

    def set(self, u, dy, v, block):
        x, z = self.xz(u, v)
        self.cv.set(x, self.y + dy, z, self.b(block))

    def fill(self, u1, dy1, v1, u2, dy2, v2, block):
        for u in range(min(u1, u2), max(u1, u2) + 1):
            for v in range(min(v1, v2), max(v1, v2) + 1):
                for dy in range(min(dy1, dy2), max(dy1, dy2) + 1):
                    self.set(u, dy, v, block)

    def sign(self, u, dy, v, block, *lines):
        x, z = self.xz(u, v)
        self.cv.sign(x, self.y + dy, z, self.b(block), *lines)

    def frame(self, u, dy, v, facing, item):
        x, z = self.xz(u, v)
        self.cv.frame(x, self.y + dy, z, self.d[facing], item)

    def world(self, u, dy, v):
        x, z = self.xz(u, v)
        return x, self.y + dy, z


# ---------------------------------------------------------------------------------------------------------------------
# terrain

def hash2(x, z, seed):
    h = (x * 374761393 + z * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def noise(x, z, scale, seed):
    gx, gz = x / scale, z / scale
    x0, z0 = math.floor(gx), math.floor(gz)
    tx, tz = gx - x0, gz - z0
    sx, sz = tx * tx * (3 - 2 * tx), tz * tz * (3 - 2 * tz)
    a, b = hash2(x0, z0, seed), hash2(x0 + 1, z0, seed)
    c, d = hash2(x0, z0 + 1, seed), hash2(x0 + 1, z0 + 1, seed)
    return (a + (b - a) * sx) * (1 - sz) + (c + (d - c) * sx) * sz


RX, RZ = 110, 98


def rim(theta):
    return 1 + .045 * math.sin(3 * theta + .5) + .035 * math.sin(5 * theta + 1.7) + .02 * math.sin(11 * theta + .3)


def inside(x, z):
    t = math.atan2(z / RZ, x / RX)
    return math.hypot(x / RX, z / RZ) <= rim(t) * .93


def island(cv):
    surface = {(x, z) for x in range(-RX - 6, RX + 7) for z in range(-RZ - 6, RZ + 7) if inside(x, z)}
    cv.surface = surface
    for (x, z) in surface:
        t = math.atan2(z / RZ, x / RX)
        edge = math.hypot(x / RX, z / RZ) / (rim(t) * .93)          # 0 centre .. 1 rim
        # a shallow lip at the rim, an inverted cone below, and a root-spire under the Knot
        rho = math.hypot(x, z)
        depth = int(3 + (1 - edge) ** 1.4 * 34 + noise(x, z, 7, 3) * 8 + noise(x, z, 2.5, 4) * 4
                    + max(0.0, 1 - rho / 16) ** 1.5 * 22)
        bottom = max(2, Y - depth)
        cv.set(x, Y, z, 'grass_block')
        dirt = 3 + int(noise(x, z, 5, 5) * 2)
        for y in range(bottom, Y):
            d = Y - y
            if d <= dirt:
                b = 'dirt'
            else:
                band = (y + int(noise(x, z, 9, 6) * 6)) % 11
                b = 'stone' if band < 5 else 'andesite' if band < 7 else 'tuff' if band < 9 else 'deepslate'
            cv.set(x, y, z, b)
    # expose ores and texture only where the underside or cliff shows
    for (x, z) in surface:
        for y in range(Y - 45, Y):
            b = cv.get(x, y, z)
            if b is None:
                continue
            exposed = any(cv.get(x + dx, y + dy, z + dz) is None for dx, dy, dz in
                          ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)))
            if not exposed:
                continue
            r = hash2(x * 7 + y, z * 3 - y, 11)
            n = base_id(b)
            if n == 'dirt':
                cv.set(x, y, z, 'rooted_dirt' if r < .35 else 'coarse_dirt' if r < .5 else 'dirt')
            elif r < .03:
                cv.set(x, y, z, 'copper_ore')
            elif r < .05:
                cv.set(x, y, z, 'iron_ore')
            elif r < .06:
                cv.set(x, y, z, 'amethyst_block')
            elif r < .16:
                cv.set(x, y, z, 'mossy_cobblestone' if y > Y - 12 else 'cobbled_deepslate')
    # dangling life on the underside: hanging roots under soil, stalactites and glow lichen under stone
    for (x, z) in sorted(surface):
        y = min(yy for yy in range(Y - 45, Y + 1) if cv.get(x, yy, z) is not None)
        r = hash2(x, z, 21)
        under = base_id(cv.get(x, y, z))
        if r < .05:
            n = 1 + int(hash2(x, z, 22) * 4)
            parts = {1: ['tip'], 2: ['frustum', 'tip'], 3: ['base', 'frustum', 'tip'],
                     4: ['base', 'middle', 'frustum', 'tip']}[n]
            cv.set(x, y, z, 'dripstone_block')
            for i, p in enumerate(parts):
                cv.set(x, y - 1 - i, z, f'pointed_dripstone[vertical_direction=down,thickness={p}]')
        elif r < .11 and under in ('dirt', 'rooted_dirt', 'coarse_dirt'):
            cv.set(x, y - 1, z, 'hanging_roots')
        elif r < .16:
            cv.set(x, y - 1, z, 'glow_lichen[up=true]')
    return surface


def edge_cells(surface):
    return {(x, z) for (x, z) in surface
            if any((x + dx, z + dz) not in surface for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


# ---------------------------------------------------------------------------------------------------------------------
# small pieces

def tree(cv, x, z, kind='oak', h=None, y=Y):
    """A tree rooted at ground level y (the town's ground unless an islet's)."""
    rng = random.Random(x * 31 + z)
    log, leaves = {'oak': ('oak_log', 'oak_leaves'), 'cherry': ('cherry_log', 'cherry_leaves'),
                   'birch': ('birch_log', 'birch_leaves'), 'azalea': ('oak_log', 'flowering_azalea_leaves'),
                   'dark': ('dark_oak_log', 'dark_oak_leaves'),
                   'ancient': ('naturesaura:ancient_log', 'naturesaura:ancient_leaves'),
                   'archwood': ('ars_nouveau:red_archwood_log', 'ars_nouveau:red_archwood_leaves'),
                   'willow': ('tribalpower:willow_log', 'tribalpower:willow_leaves'),
                   'hearthoak': ('tribalpower:hearthoak_log', 'tribalpower:hearthoak_leaves'),
                   'apple': ('oak_log', 'oak_leaves'), 'pear': ('birch_log', 'birch_leaves')}[kind]
    h = h or rng.randint(5, 7)
    cv.set(x, y, z, 'rooted_dirt' if kind == 'azalea' else 'dirt')
    cv.fill(x, y + 1, z, x, y + h, z, log)
    top = y + h
    for dy, r in [(-2, 2.6), (-1, 3.2), (0, 3.0), (1, 2.2), (2, 1.2)]:
        for dx in range(-4, 5):
            for dz in range(-4, 5):
                if dx * dx + dz * dz <= r * r + rng.random() * .8 and not (dx == 0 and dz == 0 and dy <= 0):
                    if cv.air(x + dx, top + dy, z + dz):
                        leaf = leaves
                        if kind == 'azalea' and rng.random() < .5:
                            leaf = 'azalea_leaves'
                        cv.set(x + dx, top + dy, z + dz, leaf + '[persistent=true]')
    fruit = None   # Pam's hanging fruit falls off as free items; the orchard trees stay leafy, Pam's grows in the garden
    if fruit:   # Pam's fruit hangs under the canopy
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                below = (x + dx, top - 3, z + dz)
                if rng.random() < .35 and cv.air(*below) and not cv.air(x + dx, top - 2, z + dz) \
                        and 'leaves' in (cv.get(x + dx, top - 2, z + dz) or ''):
                    cv.set(*below, fruit)
    if kind == 'cherry':
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                if rng.random() < .3 and cv.air(x + dx, y + 1, z + dz) and (x + dx, z + dz) != (x, z) \
                        and base_id(cv.get(x + dx, y, z + dz) or 'air') in ('grass_block', 'moss_block', 'dirt', 'podzol'):
                    cv.set(x + dx, y + 1, z + dz, f'pink_petals[flower_amount={rng.randint(1, 4)},facing=north]')


def lamp_post(cv, x, z, soul=False, h=3):
    cv.set(x, Y + 1, z, 'polished_deepslate_wall')
    cv.fill(x, Y + 2, z, x, Y + h, z, 'dark_oak_fence')
    cv.set(x, Y + h + 1, z, 'soul_lantern' if soul else 'lantern')


FLOWERS = ['dandelion', 'poppy', 'cornflower', 'allium', 'azure_bluet', 'oxeye_daisy', 'lily_of_the_valley',
           'blue_orchid', 'red_tulip', 'white_tulip', 'pink_tulip']


def meadow(cv, reserved):
    """Grass, flowers and moss on every open ground cell."""
    for (x, z) in sorted(cv.surface):
        if (x, z) in reserved or not cv.air(x, Y + 1, z) or base_id(cv.get(x, Y, z) or '') != 'grass_block':
            continue
        r = hash2(x, z, 31)
        n = noise(x, z, 6, 32)
        if n > .72 and r < .5:
            cv.set(x, Y, z, 'moss_block')
            if r < .2:
                cv.set(x, Y + 1, z, 'moss_carpet')
        elif r < .22:
            cv.set(x, Y + 1, z, 'short_grass')
        elif r < .26:
            cv.set(x, Y + 1, z, 'fern')
        elif r < .31:
            cv.set(x, Y + 1, z, FLOWERS[int(hash2(x, z, 33) * len(FLOWERS))])
        elif r < .315:
            cv.set(x, Y + 1, z, 'tall_grass[half=lower]')
            cv.set(x, Y + 2, z, 'tall_grass[half=upper]')


def pave(cv, x, z, style='street'):
    cv.paved.add((x, z))
    r = hash2(x, z, 41)
    if style == 'street':
        b = 'stone_bricks' if r < .55 else 'cracked_stone_bricks' if r < .68 else 'mossy_stone_bricks' if r < .8 \
            else 'andesite' if r < .9 else 'tuff_bricks'
    elif style == 'plaza':
        b = 'polished_tuff' if r < .8 else 'tuff_bricks'
    else:
        b = style
    cv.set(x, Y, z, b)


# ---------------------------------------------------------------------------------------------------------------------
# the Knot: ceremony pad, plaza, nine strand stones

def knot(cv, reserved):
    for x in range(-27, 28):
        for z in range(-27, 28):
            r = math.hypot(x, z)
            if r > 26.5:
                continue
            reserved.add((x, z))
            if max(abs(x), abs(z)) <= 7:
                continue
            if r > 25.3:
                cv.set(x, Y, z, 'polished_deepslate')
            elif r > 24.3:
                cv.set(x, Y, z, 'chiseled_tuff_bricks' if (x + z) % 4 == 0 else 'tuff_bricks')
            else:
                pave(cv, x, z, 'plaza')
    # nine spokes in tribe colours, from the pad to the rim
    for k, t in enumerate(TRIBES):
        a = math.radians(20 + 40 * k)
        for i in range(90, 245):
            rr = i / 10
            x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
            if max(abs(x), abs(z)) > 7:
                cv.set(x, Y, z, f'{DYE[t]}_glazed_terracotta' if rr > 23.5 else f'{DYE[t]}_terracotta')
        # strand stone at r 16: plinth, the tribe's block, its keepsake; a plaque names the people
        sx, sz = round(math.cos(a) * 16), round(math.sin(a) * 16)
        cv.set(sx, Y + 1, sz, 'chiseled_tuff')
        cv.set(sx, Y + 2, sz, f'{DYE[t]}_concrete')
        fx, fz = -math.cos(a), -math.sin(a)                   # plaque on the side facing the pad
        facing = ('west' if fx < 0 else 'east') if abs(fx) > abs(fz) else ('north' if fz < 0 else 'south')
        cv.set(sx, Y + 3, sz, f'driftwrecks:keepsake_{t}_shrine[facing={facing}]')
        back = {'west': (1, 0), 'east': (-1, 0), 'north': (0, 1), 'south': (0, -1)}[facing]
        cv.set(sx + back[0], Y + 1, sz + back[1], 'tribalpower:spirit_lantern')
        dx, dz = {'west': (-1, 0), 'east': (1, 0), 'north': (0, -1), 'south': (0, 1)}[facing]
        cv.sign(sx + dx, Y + 2, sz + dz, f'dark_oak_wall_sign[facing={facing}]',
                TRIBE_NAMES[t], 'hold one strand', '', f'{k + 1} of 9')
    # the pad itself: a knot mosaic in deepslate and teal, copper ring, the path to the beacon
    for x in range(-7, 8):
        for z in range(-7, 8):
            m = abs(x) + abs(z)
            if max(abs(x), abs(z)) == 7:
                b = 'polished_deepslate'
            elif x == 0 and z == 0:
                b = 'chiseled_deepslate'
            elif x == 0 and -6 <= z <= 6:
                b = 'deepslate_tiles'
            elif m <= 2 or m in (5, 6):
                b = 'cyan_terracotta'
            elif m in (9, 10):
                b = 'waxed_oxidized_cut_copper'
            elif abs(x) == abs(z):
                b = 'cyan_terracotta'
            else:
                b = 'polished_deepslate'
            cv.set(x, Y, z, b)
            cv.fill(x, Y - 1, z, x, Y - 1, z, 'deepslate')
    for x, z in ((-7, -7), (7, -7), (-7, 7), (7, 7)):
        cv.set(x, Y + 1, z, 'chiseled_polished_blackstone')
        cv.fill(x, Y + 2, z, x, Y + 3, z, 'stripped_dark_oak_log')
        cv.set(x, Y + 4, z, 'lantern')
    for z in (-2, -1):                                       # carpets flank the path as before
        cv.set(-1, Y + 1, z, 'cyan_carpet')
        cv.set(1, Y + 1, z, 'white_carpet' if z == -1 else 'cyan_carpet')
    cv.set(0, Y + 1, -6, 'sea_lantern')


# ---------------------------------------------------------------------------------------------------------------------
# the Cut Loom and the broken gate-path

LOOM_Z = -38


def cut_loom(cv, reserved):
    z0 = LOOM_Z
    for x in range(-24, 25):
        for z in range(z0 - 10, z0 + 10):
            reserved.add((x, z))
            if abs(x) <= 22 and z >= z0 - 8:
                pave(cv, x, z, 'street' if abs(x) > 3 else 'polished_andesite')
    # the aisle runs on south until it meets the Knot's rim
    for x in range(-3, 4):
        for z in range(z0 + 10, -20):
            if math.hypot(x, z) > 26.5:
                reserved.add((x, z))
                pave(cv, x, z, 'polished_andesite')
    for side in (-1, 1):
        cx = 15 * side
        # plinth
        cv.fill(cx - 2, Y + 1, z0 - 2, cx + 2, Y + 3, z0 + 2, 'polished_blackstone_bricks')
        cv.fill(cx - 2, Y + 4, z0 - 2, cx + 2, Y + 4, z0 + 2, 'polished_blackstone_brick_slab')
        for dx in (-2, 2):
            for dz in (-2, 2):
                cv.fill(cx + dx, Y + 1, z0 + dz, cx + dx, Y + 4, z0 + dz, 'chiseled_polished_blackstone')
                cv.set(cx + dx, Y + 5, z0 + dz, 'soul_lantern')
        # upright: 3x3 timber, banded with copper
        cv.fill(cx - 1, Y + 4, z0 - 1, cx + 1, Y + 28, z0 + 1, 'stripped_dark_oak_wood')
        for yy in (Y + 10, Y + 20):
            cv.fill(cx - 1, yy, z0 - 1, cx + 1, yy, z0 + 1, 'waxed_oxidized_cut_copper')
        # capital
        cv.fill(cx - 2, Y + 27, z0 - 2, cx + 2, Y + 27, z0 + 2, 'polished_blackstone_bricks')
        for dx, dz, f in ((-2, 0, 'west'), (2, 0, 'east'), (0, -2, 'north'), (0, 2, 'south')):
            cv.set(cx + dx, Y + 26, z0 + dz, f'polished_blackstone_brick_stairs[facing={f},half=top]')
    # top beam (warp beam) and the breast beam, logs across
    cv.fill(-17, Y + 29, z0 - 1, 17, Y + 31, z0 + 1, 'dark_oak_log[axis=x]')
    cv.fill(-18, Y + 29, z0, 18, Y + 31, z0, 'dark_oak_log[axis=x]')
    for x in (-18, 18):
        cv.fill(x, Y + 29, z0 - 1, x, Y + 31, z0 + 1, 'waxed_oxidized_copper')
    cv.fill(-13, Y + 8, z0, 13, Y + 9, z0, 'dark_oak_log[axis=x]')
    cv.fill(-13, Y + 8, z0 + 1, 13, Y + 8, z0 + 1, 'dark_oak_slab[type=top]')
    # spores drift down from the warp beam over the plaza side
    for x in range(-12, 13, 4):
        cv.set(x, Y + 28, z0 + 1, 'spore_blossom')
    # the woven cloth: nine warps with weft stripes, finished only up to y+14
    xs = [-12 + 3 * i for i in range(9)]
    for y in range(Y + 10, Y + 15):
        for x in range(-12, 13):
            t = TRIBES[(x + 12) // 3] if x in xs else TRIBES[(y - Y) % 9]
            cv.set(x, y, z0, f'{DYE[t]}_wool')
    # warps above the cloth, cut: the lower ends reach up, the upper ends hang from the beam, a gap between
    rng = random.Random(4)
    for i, x in enumerate(xs):
        t = TRIBES[i]
        lo_top = Y + 15 + rng.randint(1, 3)
        hi_bot = lo_top + rng.randint(6, 8)
        cv.fill(x, Y + 15, z0, x, lo_top, z0, f'{DYE[t]}_wool')
        # frayed ends: a chain of loose fibre, then a spark that still drifts off the cut
        cv.set(x, lo_top + 1, z0, 'chain')
        cv.set(x, lo_top + 2, z0, 'end_rod[facing=up]')
        cv.set(x, hi_bot - 1, z0, 'chain')
        cv.set(x, hi_bot - 2, z0, 'end_rod[facing=down]')
        cv.fill(x, hi_bot, z0, x, Y + 28, z0, f'{DYE[t]}_wool')
    # one loose thread, left long at the edge on purpose
    cv.fill(13, Y + 10, z0, 13, Y + 12, z0, 'cyan_wool')
    cv.fill(14, Y + 7, z0, 14, Y + 10, z0, 'chain')
    # heddle lanterns hang in front of the cloth
    for x in (-8, 8):
        cv.fill(x, Y + 25, z0 + 2, x, Y + 28, z0 + 2, 'chain')
        cv.set(x, Y + 24, z0 + 2, 'lantern[hanging=true]')
    cv.fill(-8, Y + 28, z0 + 1, -8, Y + 28, z0 + 2, 'dark_oak_planks')
    cv.fill(8, Y + 28, z0 + 1, 8, Y + 28, z0 + 2, 'dark_oak_planks')
    # the weaver's bench and a brazier either side of the walk-through
    cv.fill(-4, Y + 1, z0 + 3, -2, Y + 1, z0 + 3, 'dark_oak_stairs[facing=north]')
    cv.fill(2, Y + 1, z0 + 3, 4, Y + 1, z0 + 3, 'dark_oak_stairs[facing=north]')
    for x in (-7, 7):
        cv.set(x, Y + 1, z0 + 3, 'polished_blackstone_bricks')
        cv.set(x, Y + 2, z0 + 3, 'campfire[lit=true,signal_fire=false]')
    cv.sign(0, Y + 1, z0 + 5, 'dark_oak_sign[rotation=0]', 'THE CUT LOOM', 'Nine strands met here', 'until the Cut',
            'Reweave them')


def gate_path(cv, reserved):
    north = min(z for (x, z) in cv.surface if x == 0)
    end = -118
    for z in range(LOOM_Z - 9, end - 1, -1):
        for x in range(-3, 4):
            reserved.add((x, z))
        if z < north:
            cv.fill(-2, Y - 1, z, 2, Y - 1, z, 'tribalpower:march_stone_brick_slab[type=top]')
            cv.set(0, Y - 2, z, 'tribalpower:march_stone_bricks')
        for x in range(-2, 3):
            pave(cv, x, z)
        if z < north:           # rails only out on the span; homes open onto the path inside the rim
            for x in (-3, 3):
                cv.set(x, Y, z, 'tribalpower:march_stone_bricks')
                cv.set(x, Y + 1, z, 'tribalpower:march_stone_brick_wall')
    # arches under the span, every eight blocks
    for z in range(north - 4, end, -8):
        cv.fill(-1, Y - 3, z, 1, Y - 2, z, 'tribalpower:march_stone_bricks')
        cv.set(0, Y - 4, z, 'tribalpower:chiseled_march_stone_bricks')
        cv.fill(0, Y - 12, z, 0, Y - 5, z, 'chain')
        cv.set(0, Y - 13, z, 'soul_lantern[hanging=true]')
    for z in range(north - 2, end, -6):
        for x in (-3, 3):
            cv.fill(x, Y + 2, z, x, Y + 2, z, 'stone_brick_wall')
            cv.set(x, Y + 3, z, 'soul_lantern')
    # the break: a jagged edge, weeping stone, a wall so nobody walks off, fragments drifting beyond
    for x, z in ((-2, end), (-1, end), (1, end), (2, end + 1), (0, end + 1), (-2, end + 1)):
        cv.set(x, Y, z, 'crying_obsidian')
    cv.fill(-2, Y + 1, end, 2, Y + 1, end, 'stone_brick_wall')
    cv.set(2, Y, end, 'air')        # a bite out of the edge under the wall
    frags = [(1, end - 4, -1, 3), (-2, end - 8, -3, 2), (2, end - 13, -6, 2), (-1, end - 19, -10, 1)]
    for x, z, dy, n in frags:
        for i in range(n):
            cv.set(x + (i % 2), Y + dy, z - i // 2, 'cracked_stone_bricks' if i % 2 else 'stone_bricks')
        cv.set(x, Y + dy + 1, z, 'stone_brick_wall')
    cv.fill(-2, Y - 1, end - 1, -2, Y - 7, end - 1, 'chain')
    cv.fill(2, Y - 1, end - 1, 2, Y - 4, end - 1, 'chain')
    cv.sign(0, Y + 1, end + 2, 'dark_oak_sign[rotation=8]', 'THE CUT', 'A gate-path ran on', 'from here once',
            'Mind the edge')


# ---------------------------------------------------------------------------------------------------------------------
# buildings

def tp_wood(name, stripped=True):
    """A Tribal Power wood set (bellcap, cinder, frostpine, hearthoak, strider, willow)."""
    t = 'tribalpower:' + name
    return dict(log=t + '_log', wood=('tribalpower:stripped_' + name + '_log') if stripped else t + '_log',
                plank=t + '_planks', stair=t + '_stairs', slab=t + '_slab', fence=t + '_fence', door=t + '_door',
                trapdoor=t + '_trapdoor')


def tp_stone(name):
    """A Tribal Power stone roof set: march_stone_brick, moonstone_brick, moss_agate_brick."""
    t = 'tribalpower:' + name
    return (t + '_stairs', t + '_slab', t + 's')


# The Hall was raised by the nine tribes; each quarter is built in its people's wood, stone and colour.
PALETTES = {
    'soil': dict(tp_wood('hearthoak'), wall='packed_mud', base='mud_bricks',
                 roof=('mcwroofs:dark_oak_roof', 'dark_oak_slab', 'dark_oak_planks'), dye='brown',
                 glass='tribalpower:brown_quartz_glass_pane', tribe=0),
    'stone': dict(tp_wood('frostpine'), wall='tribalpower:march_stone_bricks', base='tribalpower:polished_march_stone',
                  roof=tp_stone('march_stone_brick'), dye='light_gray', glass='tribalpower:light_gray_quartz_glass_pane',
                  tribe=1),
    'spark': dict(tp_wood('cinder'), wall='tribalpower:polished_moss_agate', base='tribalpower:moss_agate_bricks',
                  roof=tp_wood('cinder'), dye='orange', glass='tribalpower:orange_quartz_glass_pane', tribe=4),
    'swarm': dict(tp_wood('bellcap'), wall='honeycomb_block', base='tribalpower:march_stone_bricks',
                  roof=('mcwroofs:spruce_roof', 'spruce_slab', 'spruce_planks'), dye='yellow', glass='tribalpower:yellow_quartz_glass_pane', tribe=6),
    'sigil': dict(tp_wood('strider'), wall='tribalpower:polished_moonstone', base='tribalpower:moonstone_bricks',
                  roof=tp_stone('moonstone_brick'), dye='purple', glass='tribalpower:purple_quartz_glass_pane', tribe=7),
}


def roof_blocks(roof):
    """(stair, slab or None, full block) from a wood set or a (stair, slab, full) tuple."""
    if isinstance(roof, dict):
        return roof['stair'], roof['slab'], roof['plank']
    return roof


def gable_roof(L, w, d, base_dy, pal, v0=-1, v1=None):
    """Front-gabled roof over u 0..w-1: stairs slopes along u, ridge along v, one block of overhang."""
    v1 = d if v1 is None else v1
    stair, slab, full = roof_blocks(pal['roof'])
    half = (w + 1) // 2
    for r in range(half + 1):
        dy = base_dy + r
        ul, ur = -1 + r, w - r
        if ul > ur:
            break
        if ul == ur:
            L.fill(ul, dy, v0, ul, dy, v1, full)
            if slab:
                L.fill(ul, dy + 1, v0, ul, dy + 1, v1, slab + '[type=bottom]')
            break
        L.fill(ul, dy, v0, ul, dy, v1, stair + '[facing={right}]')
        L.fill(ur, dy, v0, ur, dy, v1, stair + '[facing={left}]')
        if r > 0:   # gable walls, tucked under the stairs
            for v in (0, d - 1):
                L.fill(ul + 1, dy - 1, v, ur - 1, dy - 1, v, pal['plank'])
    return base_dy + half


def shop(cv, reserved, face, fx, fz, pal, title, sub, wares, keeper, blocks):
    """Open-fronted shop, 11 wide, 10 deep: porch v0, shop floor v1..5, counter v6, keeper v7 (a counter return
    at u 2 and 8 closes the corridor), back shelves v8, back wall v9."""
    L = Local(cv, face, fx, fz)
    w, d, h = 11, 10, 5
    tribe = blocks.get('tribe', pal.get('tribe'))
    # walls, with the whole front open
    L.fill(0, 0, 0, w - 1, 0, d - 1, pal['base'])
    L.fill(1, 0, 1, w - 2, 0, d - 2, pal['plank'])
    for u in (0, w - 1):
        L.fill(u, 1, 1, u, h, d - 1, pal['wall'])
        L.fill(u, 1, 1, u, 1, d - 1, pal['base'])
        L.fill(u, 1, 1, u, h, 1, pal['log'])
        L.fill(u, 1, 5, u, h, 5, pal['log'])
        L.fill(u, 2, 7, u, 3, 8, pal.get('glass', 'glass_pane'))
        L.set(u + (-1 if u == 0 else 1), 1, 7, 'flower_pot')
        L.set(u + (-1 if u == 0 else 1), 1, 8, 'potted_red_tulip' if u else 'potted_azure_bluet')
    L.fill(0, 1, d - 1, w - 1, h, d - 1, pal['wall'])
    L.fill(0, 1, d - 1, w - 1, 1, d - 1, pal['base'])
    for u in (0, w - 1):
        L.fill(u, 1, d - 1, u, h, d - 1, pal['log'])
    L.fill(0, h, 1, w - 1, h, 1, pal['log'] + '[axis={au}]')
    L.fill(0, h, d - 1, w - 1, h, d - 1, pal['log'] + '[axis={au}]')
    for u in (0, w - 1):
        L.fill(u, h, 1, u, h, d - 1, pal['log'] + '[axis={av}]')
    L.fill(1, 1, 1, w - 2, h - 1, d - 2, 'air')
    L.fill(1, 1, 0, w - 2, h, 0, 'air')
    # roof, with a lit window in the front gable
    top = gable_roof(L, w, d, h + 1, pal, v0=-1, v1=d)
    L.fill(1, h + 1, 1, w - 2, h + 1, 1, pal['plank'])
    L.fill(3, h + 2, 1, w - 4, h + 2, 1, pal['plank'])
    L.set(5, h + 2, 1, 'tribalpower:lit_orange_quartz_glass' if tribe == 4 else 'glass')
    # a striped awning over the shopfront, stepping down toward the street
    for u in range(0, w):
        stripe = pal['dye'] + '_wool' if u % 2 == 0 else 'white_wool'
        L.set(u, h - 1, -1, stripe)
    # counter: 1.5 blocks, so the keeper stays behind it and customers lean over it
    L.fill(1, 1, 6, w - 2, 1, 6, pal['wood'] + '[axis={au}]')
    L.fill(1, 2, 6, w - 2, 2, 6, pal['slab'] + '[type=bottom]')
    # the keeper's corner: back shelves either side, the space between kept clear; a counter return beside each
    # low crate, since a keeper who could hop onto a crate could step from it over the counter
    for u in (1, 2, w - 3, w - 2):
        L.fill(u, 1, 8, u, 3, 8, blocks.get('shelf', 'barrel[facing={front}]'))
    for u, ret in ((1, 2), (w - 2, w - 3)):
        L.set(u, 1, 7, blocks.get('low', 'barrel[facing=up]'))
        L.set(ret, 1, 7, pal['wood'] + '[axis={av}]')
        L.set(ret, 2, 7, pal['slab'] + '[type=bottom]')
    L.fill(3, 2, d - 2, 7, 2, d - 2, 'tribalpower:wall_shelf[facing={front}]')
    # wares: frames along both side walls (shop floor) and the back wall above the keeper
    spots = [(1, 2, v, 'right') for v in (2, 3, 4)] + [(w - 2, 2, v, 'left') for v in (2, 3, 4)] + \
            [(1, 3, v, 'right') for v in (2, 3, 4)] + [(w - 2, 3, v, 'left') for v in (2, 3, 4)] + \
            [(u, 4, d - 2, 'front') for u in (3, 7)] + [(u, 3, d - 2, 'front') for u in (3, 7)]
    featured = blocks.get('featured')
    if featured:
        # the headline item three times across the back wall, and a board saying what it costs
        for u in (4, 5, 6):
            L.frame(u, 3, d - 2, 'front', featured[0])
        L.sign(5, 4, d - 2, 'spruce_wall_sign[facing={front}]', *featured[1])
    for (u, dy, v, facing), item in zip(spots, wares):
        L.frame(u, dy, v, facing, item)
    # display blocks on the shop floor, under the frames
    for u, v, b in blocks.get('floor', []):
        L.set(u, 1, v, b)
    # light: chains from the ridge with lanterns, one over the counter
    for v in (3, 7):
        L.fill(5, h, v, 5, top - 1, v, 'chain')
        L.set(5, h - 1, v, 'lantern[hanging=true]')
    # front: the tribe's banners on the posts, a hanging sign under the lintel, crates on the porch
    for u in (0, w - 1):
        if tribe is not None:
            L.set(u, h - 2, 0, f'tribalpower:tribe_banner[facing={{front}},tribe={tribe},wall=true]')
        else:
            L.set(u, h - 2, 0, pal['dye'] + '_wall_banner[facing={front}]')
    L.sign(5, h - 1, 1, 'spruce_hanging_sign[rotation={rot_front},attached=false]', title, sub)
    for u, b in blocks.get('porch', []):
        L.set(u, 1, 0, b)
    ku, kdy, kv = L.world(5, 1, 7)
    # keeper looks out of the shop, toward the street
    yaw = {'south': 0, 'north': 180, 'east': -90, 'west': 90}[L.d['front']]
    cv.posts[keeper] = [ku, kdy, kv, yaw]
    # the footprint and the strip in front stay clear of roadside clutter
    reserved.update(L.xz(u, v) for u in range(-1, w + 1) for v in range(-2, d + 1))
    return L


def listing_items(stall):
    items = []
    for path in sorted(SHOP.glob('*.json')):
        e = json.loads(path.read_text(encoding='utf-8'))
        if e['stall'] != stall:
            continue
        item = e['result']['id']
        if item == 'ninjacatskies:frayed_thread':     # Grit's buy-backs: show what they take
            item = e['cost']['id']
        if item not in items:
            items.append(item)
    return items


def market_stall(cv, x, z, face, dye, goods):
    """An open market stall: four posts, a striped canopy, a table of goods."""
    L = Local(cv, face, x, z)
    for u in (0, 4):
        for v in (0, 2):
            L.fill(u, 1, v, u, 3, v, 'spruce_fence')
    for u in range(-1, 6):
        for v in range(-1, 4):
            L.set(u, 4, v, (dye if (u + 10) % 2 == 0 else 'white') + '_wool')
    for u, b in zip(range(1, 4), goods):
        L.set(u, 1, 1, b)
    L.set(2, 3, 1, 'lantern[hanging=true]')


SHOPS = [   # stall id, face, front x, front z, people, sign title, sign line
    ('padkeepers', 'S', -44, -6, 'soil', 'PAD-KEEPERS', 'Saddlery & Stock'),
    ('rootbinders', 'S', -62, -6, 'sprout', 'ROOTBINDERS', 'Seed & Sapling'),
    ('grit', 'S', 34, -6, 'stone', 'GRIT-SINGERS', 'Stone & Exchange'),
    ('patternweavers', 'S', 52, -6, 'clock', 'PATTERN-WEAVERS', 'Clocks & Charts'),
    ('colony', 'N', -34, 6, 'swarm', 'COLONY-KEEPERS', 'Honey & Wax'),
    ('loomstitchers', 'N', -52, 6, 'spindle', 'LOOM-STITCHERS', 'Yarn & Dye'),
    ('spark', 'N', 44, 6, 'spark', 'DRUMHEART CURIOS', 'Rare goods'),
    ('edgewalkers', 'N', 62, 6, 'claw', 'EDGE-WALKERS', 'Rope & Road'),
    ('sealcarvers', 'E', -6, 44, 'sigil', 'SEAL-CARVERS', 'Pages & Gems'),
]
STALL_NAMES = {'padkeepers': 'Pad-keepers', 'rootbinders': 'Rootbinders', 'grit': 'Grit', 'patternweavers': 'Pattern-weavers',
               'colony': 'Colony-keepers', 'loomstitchers': 'Loom-stitchers', 'spark': 'Spark', 'edgewalkers': 'Edge-walkers',
               'sealcarvers': 'Seal-carvers', 'hearth': 'Hearth-keeper', 'whiskerwind': 'Whiskerwind Guide',
               'esther': 'Esther'}
STALL_TRIBE = {'padkeepers': 0, 'grit': 1, 'rootbinders': 2, 'edgewalkers': 3, 'spark': 4, 'patternweavers': 5,
               'colony': 6, 'whiskerwind': 6, 'sealcarvers': 7, 'hearth': 7, 'loomstitchers': 8, 'esther': 6}
SHOP_DRESS = {   # what each keeper keeps on the shop floor (u 1 and 9, v 1..4), the porch and the back shelves
    'padkeepers': dict(featured=('minecraft:saddle', ('SADDLES', 'one block of', 'diamond each', 'ask the keeper')),
                       shelf='barrel[facing={front}]', low='hay_block',
                       floor=[(1, 1, 'farmersdelight:carrot_crate'), (1, 2, 'hay_block'), (1, 3, 'composter[level=7]'),
                              (1, 4, 'farmersdelight:rice_bale'), (9, 1, 'hay_block'), (9, 2, 'tribalpower:hanging_rack[facing={left}]'),
                              (9, 3, 'sophisticatedbackpacks:backpack[facing={left}]'), (9, 4, 'farmersdelight:onion_crate')],
                       porch=[(1, 'hay_block'), (9, 'farmersdelight:beetroot_crate')]),
    'rootbinders': dict(shelf='tribalpower:willow_leaves', low='moss_block',
                        floor=[(1, 1, 'botanypots:terracotta_botany_pot'), (1, 2, 'botanypots:terracotta_botany_pot'),
                               (1, 3, 'potted_oak_sapling'), (1, 4, 'potted_cherry_sapling'), (9, 1, 'potted_flowering_azalea_bush'),
                               (9, 2, 'farmersdelight:cabbage_crate'), (9, 3, 'mysticalagriculture:inferium_block'),
                               (9, 4, 'composter[level=8]')],
                        porch=[(1, 'potted_flowering_azalea_bush'), (9, 'potted_azalea_bush')]),
    'grit': dict(shelf='chiseled_stone_bricks', low='smithing_table',
                 floor=[(1, 1, 'anvil[facing={front}]'), (1, 2, 'blast_furnace[facing={right},lit=true]'),
                        (1, 3, 'silentgear:salvager[facing={right},lit=false]'), (1, 4, 'stonecutter[facing={right}]'),
                        (9, 1, 'exdeorum:oak_sieve'), (9, 2, 'exdeorum:porcelain_crucible'),
                        (9, 3, 'silentgear:material_grader[facing={left},lit=false]'),
                        (9, 4, 'grindstone[face=floor,facing={left}]')],
                 porch=[(1, 'driftwrecks:salvage_crate'), (9, 'exdeorum:stone_barrel')]),
    'patternweavers': dict(shelf='bookshelf', low='cartography_table',
                           floor=[(1, 1, 'supplementaries:globe[facing={right}]'), (1, 2, 'cartography_table'),
                                  (1, 3, 'supplementaries:hourglass[facing=up]'), (1, 4, 'create:clockwork_bearing[facing=up]'),
                                  (9, 1, 'lectern[facing={left}]'), (9, 2, 'create:brass_block'), (9, 3, 'create:cogwheel[axis=y]'),
                                  (9, 4, 'supplementaries:globe_sepia[facing={left}]')],
                           porch=[(1, 'create:andesite_casing'), (9, 'create:brass_casing')]),
    'colony': dict(shelf='honeycomb_block', low='beehive[facing={front},honey_level=5]',
                   floor=[(1, 1, 'productivebees:advanced_oak_beehive[expanded=none,facing={right},honey_level=5]'),
                          (1, 2, 'honey_block'), (1, 3, 'productivebees:centrifuge'), (1, 4, 'candle[candles=3,lit=true]'),
                          (9, 1, 'beehive[facing={left},honey_level=5]'), (9, 2, 'honeycomb_block'), (9, 3, 'honey_block'),
                          (9, 4, 'bee_nest[facing={left},honey_level=3]')],
                   porch=[(1, 'honey_block'), (9, 'potted_flowering_azalea_bush')]),
    'loomstitchers': dict(shelf='white_wool', low='voidloom:tension_barrel',
                          floor=[(1, 1, 'loom[facing={right}]'), (1, 2, 'cyan_wool'), (1, 3, 'purple_wool'),
                                 (1, 4, 'voidloom:loomframe'), (9, 1, 'yellow_wool'), (9, 2, 'red_wool'), (9, 3, 'green_wool'),
                                 (9, 4, 'orange_wool')],
                          porch=[(1, 'white_wool'), (9, 'light_blue_wool')]),
    'spark': dict(shelf='chiseled_bookshelf[facing={front}]', low='note_block',
                  floor=[(1, 1, 'amethyst_block'), (1, 2, 'brewing_stand'), (1, 3, 'irons_spellbooks:book_stack[facing={right}]'),
                         (1, 4, 'tribalpower:drumheart'), (9, 1, 'jukebox'), (9, 2, 'tribalpower:spirit_urn[facing={left}]'),
                         (9, 3, 'ars_nouveau:arcane_pedestal[facing=up]'), (9, 4, 'tribalpower:ember_bowl[lit=true]')],
                  porch=[(1, 'decorated_pot[facing={front}]'), (9, 'decorated_pot[facing={front}]')]),
    'edgewalkers': dict(shelf='barrel[facing={front}]', low='supplementaries:sack',
                        floor=[(1, 1, 'supplementaries:sack'), (1, 2, 'target'), (1, 3, 'fletching_table'),
                               (1, 4, 'irons_spellbooks:armor_pile[facing={right}]'), (9, 1, 'sophisticatedbackpacks:backpack[facing={left}]'),
                               (9, 2, 'scaffolding'), (9, 3, 'lodestone'), (9, 4, 'supplementaries:sack')],
                        porch=[(1, 'mcwbridges:rope_oak_bridge[facing={front},connection=base]'), (9, 'barrel[facing=up]')]),
    'sealcarvers': dict(shelf='bookshelf', low='chiseled_bookshelf[facing={front}]',
                        floor=[(1, 1, 'lectern[facing={right}]'), (1, 2, 'irons_spellbooks:book_stack[facing={right}]'),
                               (1, 3, 'irons_spellbooks:inscription_table[facing={right}]'), (1, 4, 'occultism:large_candle_purple'),
                               (9, 1, 'enchanting_table'), (9, 2, 'emerald_block'), (9, 3, 'lapis_block'),
                               (9, 4, 'occultism:large_candle_white')],
                        porch=[(1, 'tribalpower:offering_table'), (9, 'decorated_pot[facing={front}]')]),
}


def market(cv, reserved):
    for x in list(range(-118, -26)) + list(range(27, 119)):
        for z in range(-4, 5):
            if (x, z) in cv.surface:
                reserved.add((x, z))
                pave(cv, x, z)
    for stall, face, fx, fz, tribe, title, sub in SHOPS:
        wares = [i for i in listing_items(stall) if i != 'minecraft:saddle']
        shop(cv, reserved, face, fx, fz, HOME_STYLE[tribe], title, sub, wares, stall, SHOP_DRESS[stall])
    # open stalls toward the rim, piled with salvage and green (clear of the garden and on solid ground)
    market_stall(cv, -92, -9, 'S', 'lime', ['hay_block', 'farmersdelight:onion_crate', 'melon'])
    market_stall(cv, 96, 9, 'N', 'purple', ['driftwrecks:salvage_crate', 'pumpkin', 'driftwrecks:salvage_crate'])
    market_stall(cv, -68, 9, 'N', 'orange', ['farmersdelight:carrot_crate', 'pumpkin', 'farmersdelight:cabbage_crate'])
    market_stall(cv, 80, 9, 'N', 'cyan', ['supplementaries:sack', 'barrel[facing=up]', 'supplementaries:sack'])
    # lantern lines strung across the street between tall posts
    for x in (-92, -70, -48, -28, 28, 48, 70, 92):
        for z in (-4, 4):
            cv.set(x, Y + 1, z, 'polished_deepslate_wall')
            cv.fill(x, Y + 2, z, x, Y + 5, z, 'dark_oak_fence')
        cv.fill(x, Y + 5, -3, x, Y + 5, 3, 'chain[axis=z]')
        for z in (-2, 0, 2):
            cv.set(x, Y + 4, z, 'lantern[hanging=true]')
    # benches along the kerb
    for x in (-58, -39, 39, 57):
        for z, f in ((-4, 'south'), (4, 'north')):
            if cv.air(x, Y + 1, z) and cv.air(x + 1, Y + 1, z):
                cv.set(x, Y + 1, z, f'tribalpower:spruce_tribal_bench[facing={f},part=left]')
                cv.set(x + 1, Y + 1, z, f'tribalpower:spruce_tribal_bench[facing={f},part=right]')


def roost(cv, reserved):
    """Esther's Roost on the west side of the Whiskerwind Road: a stable with the steward at its counter."""
    shop(cv, reserved, 'E', -5, 78, PALETTES['swarm'], "ESTHER'S ROOST", 'Chocobo steward', [], 'esther',
         dict(shelf='hay_block', low='hay_block',
              floor=[(1, 1, 'hay_block'), (1, 2, 'water_cauldron[level=3]'), (1, 3, 'hay_block'),
                     (9, 1, 'hay_block'), (9, 2, 'hay_block'), (9, 3, 'composter[level=7]')],
              porch=[(1, 'hay_block')]))     # dress_interiors sets a backpack at porch u 9


def booth(cv, reserved):
    """The Whiskerwind Guide's gate booth, east of the road."""
    L = Local(cv, 'W', 5, 66)
    pal = PALETTES['swarm']
    w, d, h = 7, 6, 4
    L.fill(0, 0, 0, w - 1, 0, d - 1, pal['base'])
    for u in (0, w - 1):
        L.fill(u, 1, 1, u, h, d - 1, pal['log'])
    L.fill(0, 1, d - 1, w - 1, h, d - 1, pal['wall'])
    L.fill(0, h, 1, w - 1, h, 1, pal['log'] + '[axis={au}]')
    L.fill(1, 1, 1, w - 2, 1, 1, pal['wood'] + '[axis={au}]')
    L.fill(1, 2, 1, w - 2, 2, 1, pal['slab'] + '[type=bottom]')
    L.fill(1, 1, 2, w - 2, h - 1, d - 2, 'air')
    gable_roof(L, w, d, h + 1, pal, v0=-1, v1=d)
    L.set(1, 1, d - 2, 'beehive[facing={front},honey_level=5]')
    L.set(w - 2, 1, d - 2, 'hay_block')
    L.frame(3, 3, d - 2, 'front', 'minecraft:feather')
    L.frame(2, 3, d - 2, 'front', 'minecraft:saddle')
    L.frame(4, 3, d - 2, 'front', 'minecraft:golden_carrot')
    # the sign hangs from the lintel over the counter
    L.sign(3, h - 1, 1, 'birch_hanging_sign[rotation={rot_front},attached=false]', 'WHISKERWIND', 'Race town road')
    x, y, z = L.world(3, 1, 3)
    cv.posts['whiskerwind'] = [x, y, z, 90]
    reserved.update(L.xz(u, v) for u in range(-1, w + 1) for v in range(-1, d + 1))


def whiskerwind_road(cv, reserved):
    south = max(z for (x, z) in cv.surface if x == 0)
    for z in range(26, south + 1):
        for x in range(-3, 4):
            reserved.add((x, z))
            pave(cv, x, z)
    # the gate arch at the rim, a feathered crest, and the road running on into the sky
    zc = south - 3
    for x in (-5, 5):
        cv.fill(x, Y + 1, zc, x, Y + 8, zc, 'stripped_birch_log')
        cv.set(x, Y + 9, zc, 'lantern')
    cv.fill(-5, Y + 8, zc, 5, Y + 8, zc, 'birch_log[axis=x]')
    for x in range(-4, 5):
        cv.set(x, Y + 9, zc, 'yellow_wool' if x % 2 else 'white_wool')
    cv.fill(-1, Y + 10, zc, 1, Y + 10, zc, 'yellow_wool')
    cv.set(0, Y + 11, zc, 'yellow_wool')
    cv.fill(-3, Y + 1, south, 3, Y + 1, south, 'birch_fence')
    cv.set(0, Y + 1, south - 1, 'yellow_carpet')
    for z in range(30, south - 4, 8):
        lamp_post(cv, -4, z)
        lamp_post(cv, 4, z)
    booth(cv, reserved)
    roost(cv, reserved)


def purring_hearth(cv, reserved):
    """The tavern and inn: stone below, a jettied timber floor above with the townsfolk's beds, a great hearth."""
    pal = PALETTES['sigil']
    fx, fz, w, d = -60, -30, 15, 12          # faces south onto its lane; x -60..-46, z -30..-41
    L = Local(cv, 'S', fx, fz)
    h1 = 5
    # ground floor: stone
    L.fill(0, 0, 0, w - 1, 0, d - 1, pal['base'])
    L.fill(1, 0, 1, w - 2, 0, d - 2, pal['plank'])
    L.fill(0, 1, 0, w - 1, h1, d - 1, pal['base'])
    L.fill(0, 1, 0, w - 1, 1, d - 1, 'tribalpower:march_cobble')
    L.fill(1, 1, 1, w - 2, h1, d - 2, 'air')
    for u in (0, w - 1):
        for v in (0, d - 1):
            L.fill(u, 1, v, u, h1, v, 'tribalpower:chiseled_march_stone_bricks')
    for u in (2, 3, 11, 12):
        L.fill(u, 2, 0, u, 3, 0, pal['glass'])
    for v in (3, 4, 8, 9):
        L.fill(0, 2, v, 0, 3, v, pal['glass'])
        L.fill(w - 1, 2, v, w - 1, 3, v, pal['glass'])
    # upper floor, jettied one block out on every side
    hu = h1 + 1
    L.fill(-1, hu, -1, w, hu, d, pal['plank'])
    L.fill(-1, hu + 1, -1, w, hu + 4, d, pal['wall'])
    for u in (-1, 3, 7, 11, w):
        L.fill(u, hu + 1, -1, u, hu + 4, -1, pal['wood'])
        L.fill(u, hu + 1, d, u, hu + 4, d, pal['wood'])
    for v in (-1, 3, 7, d):
        L.fill(-1, hu + 1, v, -1, hu + 4, v, pal['wood'])
        L.fill(w, hu + 1, v, w, hu + 4, v, pal['wood'])
    L.fill(-1, hu + 4, -1, w, hu + 4, -1, pal['log'] + '[axis={au}]')
    L.fill(-1, hu + 4, d, w, hu + 4, d, pal['log'] + '[axis={au}]')
    for u in (1, 5, 9, 13):
        L.fill(u, hu + 2, -1, u + 1, hu + 3, -1, pal['glass'])
        L.set(u, hu + 1, -2, pal['trapdoor'] + '[facing={front},half=top,open=false]')
        L.set(u + 1, hu + 1, -2, pal['trapdoor'] + '[facing={front},half=top,open=false]')
    for v in (1, 5, 9):
        L.fill(-1, hu + 2, v, -1, hu + 3, v + 1, pal['glass'])
        L.fill(w, hu + 2, v, w, hu + 3, v + 1, pal['glass'])
    L.fill(0, hu + 1, 0, w - 1, hu + 3, d - 1, 'air')
    # corbels under the jetty
    for u in range(0, w, 2):
        L.set(u, h1, -1, pal['stair'] + '[facing={back},half=top]')
    top = gable_roof(Local(cv, 'S', fx - 1, fz + 1), w + 2, d + 2, hu + 5, pal)
    # stairs along the back wall (v 9-10), climbing west from u 7 to u 2, whose top step is flush with the upper
    # floor; a landing by the left wall, and a rail round the stairwell
    for i in range(6):
        u = 7 - i
        L.fill(u, 1 + i, d - 3, u, 1 + i, d - 2, pal['stair'] + '[facing={left}]')
        L.fill(u, 2 + i, d - 3, u, 4 + i, d - 2, 'air')
    L.fill(3, hu, d - 3, 8, hu, d - 2, 'air')
    L.fill(3, hu + 1, d - 4, 8, hu + 1, d - 4, pal['fence'])
    L.fill(9, hu + 1, d - 3, 9, hu + 1, d - 2, pal['fence'])
    # beds upstairs: exactly one per townsperson, so nobody breeds a crowd
    for i, colour in enumerate(['red', 'orange', 'yellow', 'lime', 'cyan', 'light_blue', 'purple', 'brown']):
        u = 1 + (i % 4) * 3 + (1 if i % 4 else 0)
        v = 1 if i < 4 else 5
        L.set(u, hu + 1, v, f'{colour}_bed[facing={{back}},part=foot]')
        L.set(u, hu + 1, v + 1, f'{colour}_bed[facing={{back}},part=head]')
        L.set(u + 1, hu + 1, v, 'tribalpower:march_stool[facing={front}]')
    for u in (3, 7, 11):   # hung from the ceiling beams
        L.set(u, hu + 3, 4, 'lantern[hanging=true]')
    # fireplace on the right wall with a hearth pot over the fire and a chimney that smokes
    L.fill(w - 1, 1, 3, w - 1, top + 2, 7, 'bricks')
    L.fill(w - 2, 1, 4, w - 2, 3, 6, 'bricks')
    L.set(w - 2, 1, 5, 'campfire[lit=true,signal_fire=false,facing={left}]')
    L.set(w - 2, 2, 5, 'tribalpower:hearth_pot[cooking=true]')
    L.fill(w - 1, 2, 5, w - 1, top + 2, 5, 'air')
    L.set(w - 2, 4, 5, 'bricks')
    L.fill(w, 1, 4, w, top + 2, 6, 'bricks')
    L.fill(w, top - 1, 5, w, top + 2, 5, 'air')
    L.set(w, top - 2, 5, 'campfire[lit=true,signal_fire=true]')
    # the bar along the front-left, barrels behind it, and a butcher's smoker: the keeper's pen (u 2-3, v 1-5) is
    # closed by the 1.5-block bar and counter and the two-high barrels, with nothing inside at a hop's height
    # next to them
    L.fill(4, 1, 1, 4, 1, 5, pal['wood'] + '[axis={av}]')
    L.fill(4, 2, 1, 4, 2, 5, pal['slab'] + '[type=bottom]')
    L.fill(1, 1, 2, 1, 2, 5, 'barrel[facing={right}]')
    L.set(2, 1, 1, 'smoker[facing={front},lit=true]')
    L.fill(2, 1, 6, 3, 1, 6, pal['wood'] + '[axis={au}]')
    L.fill(2, 2, 6, 3, 2, 6, pal['slab'] + '[type=bottom]')
    kx, ky, kz = L.world(3, 1, 4)
    cv.posts['hearth'] = [kx, ky, kz, {'south': 0, 'north': 180, 'east': -90, 'west': 90}[L.d['right']]]
    L.set(1, 3, 2, 'tribalpower:hanging_rack[facing={right}]')     # on the left wall, over the barrels
    # tables in the room: Tribal Power tables and stools (dress_interiors adds the Handcrafted pair at u 10)
    for u, v in ((7, 2), (7, 6)):
        L.set(u, 1, v, 'tribalpower:march_table[facing={front}]')
        L.set(u - 1, 1, v, 'tribalpower:march_stool[facing={right}]')
        L.set(u + 1, 1, v, 'tribalpower:march_stool[facing={left}]')
        L.set(u, 1, v + 1, 'tribalpower:march_stool[facing={front}]')
    for v in (3, 6):
        L.set(8, h1, v, 'lantern[hanging=true]')
    L.fill(9, 1, 8, 11, 1, 9, 'tribalpower:woven_mat')
    # the door onto a paved terrace that meets the Hearth lane, tables outside either side of it
    L.set(7, 1, 0, pal['door'] + '[facing={front},half=lower,hinge=left]')
    L.set(7, 2, 0, pal['door'] + '[facing={front},half=upper,hinge=left]')
    for u in range(5, 10):
        for v in range(-3, 0):
            x, _, z = L.world(u, 0, v)
            pave(cv, x, z, pal['base'])
    for u in (2, 14):
        L.set(u, 1, -2, 'tribalpower:march_table[facing={front}]')
        L.set(u - 1, 1, -2, 'tribalpower:march_stool[facing={right}]')
        L.set(u + 1, 1, -2, 'tribalpower:march_stool[facing={left}]')
    L.sign(7, h1, -1, 'spruce_hanging_sign[rotation={rot_front},attached=false]', 'THE PURRING HEARTH', 'Inn & hearth')
    reserved.update((x, z) for x in range(fx - 3, fx + w + 3) for z in range(fz - d - 3, fz + 4))
    return L


def chapel(cv, reserved):
    """The Stitchers' Chapel: a stone nave with stained glass in the nine colours, the loom that was never stopped,
    a spire with the bell."""
    fx, fz = 36, -30
    L = Local(cv, 'S', fx, fz)       # front at z -30, nave runs north
    w, d, h = 11, 18, 7
    L.fill(0, 0, 0, w - 1, 0, d - 1, 'tribalpower:moonstone_bricks')
    L.fill(1, 0, 1, w - 2, 0, d - 2, 'tribalpower:polished_moonstone')
    for u in (0, w - 1):
        L.fill(u, 1, 0, u, h, d - 1, 'tribalpower:moonstone_bricks')
    for v in (0, d - 1):
        L.fill(0, 1, v, w - 1, h, v, 'tribalpower:moonstone_bricks')
    for u in (0, w - 1):
        for v in range(0, d, 4):
            L.fill(u, 1, v, u, h + 1, v, 'tribalpower:chiseled_march_stone_bricks' if v in (0, d - 1) else 'tribalpower:march_stone_bricks')
    L.fill(1, 1, 1, w - 2, h, d - 2, 'air')
    # stained glass, a tribe per window
    for i, v in enumerate((2, 6, 10, 14)):
        for u, t in ((0, TRIBES[i]), (w - 1, TRIBES[i + 4])):
            L.fill(u, 2, v, u, 5, v + 1, f'tribalpower:lit_{DYE[t]}_quartz_glass')
    L.fill(4, 2, d - 1, 6, 6, d - 1, 'tribalpower:lit_cyan_quartz_glass')
    L.fill(5, 7, d - 1, 5, 7, d - 1, 'tribalpower:lit_cyan_quartz_glass')
    # steep roof
    for r in range(7):
        L.fill(-1 + r, h + 1 + r, -1, -1 + r, h + 1 + r, d, 'deepslate_tile_stairs[facing={right}]')
        L.fill(w - r, h + 1 + r, -1, w - r, h + 1 + r, d, 'deepslate_tile_stairs[facing={left}]')
        if r:
            for v in (0, d - 1):
                L.fill(r, h + r, v, w - 1 - r, h + r, v, 'tribalpower:moonstone_bricks')
    L.fill(5, h + 7, -1, 5, h + 7, d, 'deepslate_tiles')
    # doorway and rose window
    L.fill(4, 1, 0, 6, 4, 0, 'air')
    L.set(4, 4, 0, 'tribalpower:march_stone_brick_stairs[facing={right},half=top]')
    L.set(6, 4, 0, 'tribalpower:march_stone_brick_stairs[facing={left},half=top]')
    L.fill(4, 9, 0, 6, 11, 0, 'tribalpower:lit_purple_quartz_glass')
    L.set(5, 10, 0, 'tribalpower:lit_cyan_quartz_glass')
    # pews, aisle carpet, the loom that was never stopped, and its tapestry with a loose thread
    for v in range(3, 12, 2):
        L.fill(1, 1, v, 3, 1, v, 'dark_oak_stairs[facing={front}]')
        L.fill(7, 1, v, 9, 1, v, 'dark_oak_stairs[facing={front}]')
    L.fill(5, 1, 1, 5, 1, 13, 'cyan_carpet')
    L.fill(3, 1, 14, 7, 1, 16, 'polished_deepslate')
    L.fill(3, 1, 14, 7, 1, 14, 'polished_deepslate_stairs[facing={front}]')
    L.set(5, 2, 15, 'loom[facing={front}]')
    for i, t in enumerate(TRIBES):
        L.fill(1 + i, 3, d - 2, 1 + i, 5, d - 2, f'{DYE[t]}_wool')
    L.set(9, 2, d - 2, 'chain')          # the loose thread, down to the Voidloom barrel dress_interiors sets below
    for u in (2, 8):
        L.set(u, 2, 15, 'white_candle[candles=4,lit=true]')
        L.set(u, 1, 15, 'polished_deepslate')
    for v in (4, 8, 12):
        L.fill(5, 8, v, 5, 12, v, 'chain')
        L.set(5, 7, v, 'soul_lantern[hanging=true]')
    # the spire over the front: belfry and bell
    L.fill(3, h + 1, -3, 7, h + 1, 1, 'tribalpower:moonstone_bricks')
    for u in (3, 7):
        for v in (-3, 1):
            L.fill(u, h + 2, v, u, h + 12, v, 'polished_deepslate')
    L.fill(3, h + 12, -3, 7, h + 12, 1, 'polished_deepslate')
    L.fill(4, h + 11, -2, 6, h + 11, 0, 'dark_oak_planks')
    L.set(5, h + 10, -1, 'bell[attachment=ceiling,facing={front}]')
    for r in range(4):
        L.fill(3 + r, h + 13 + r, -3 + r, 7 - r, h + 13 + r, 1 - r, 'waxed_oxidized_cut_copper')
        if r < 3:
            L.fill(4 + r, h + 13 + r, -2 + r, 6 - r, h + 13 + r, 0 - r, 'air')
    L.set(5, h + 17, -1, 'waxed_oxidized_copper')
    L.fill(5, h + 18, -1, 5, h + 19, -1, 'lightning_rod')
    L.sign(5, 5, -1, 'dark_oak_wall_sign[facing={front}]', "STITCHERS' CHAPEL", 'A loom never stopped', 'Add a thread',
           'as you pass')
    reserved.update((x, z) for x in range(fx - 2, fx + w + 2) for z in range(fz - d - 2, fz + 4))


ARCHIVE = (-51, 48, 7)


def archive(cv, reserved):
    """The Leaf Archive: a round tower of books under a green copper dome."""
    cx, cz, r = ARCHIVE
    for x in range(cx - r - 1, cx + r + 2):
        for z in range(cz - r - 1, cz + r + 2):
            reserved.add((x, z))
            dd = math.hypot(x - cx, z - cz)
            if dd <= r + .5:
                cv.set(x, Y, z, 'polished_andesite' if dd > r - .5 else 'tribalpower:willow_planks')
                if dd > r - .5:
                    cv.fill(x, Y + 1, z, x, Y + 9, z, 'tribalpower:moss_agate_bricks')
                    cv.set(x, Y + 1, z, 'tribalpower:march_cobble')
                else:
                    cv.fill(x, Y + 1, z, x, Y + 9, z, 'air')
                    if dd > r - 1.5:
                        cv.fill(x, Y + 1, z, x, Y + 4, z, 'bookshelf' if hash2(x, z, 97) < .6 else
                                'irons_spellbooks:wisewood_bookshelf' if hash2(x, z, 98) < .5 else
                                'chiseled_bookshelf[facing=north]')
    # cornice, then a true dome: a solid copper shell whose radius falls on a circle, a lantern cupola on top
    for x in range(cx - r - 1, cx + r + 2):
        for z in range(cz - r - 1, cz + r + 2):
            if r - .5 < math.hypot(x - cx, z - cz) <= r + 1.2:
                cv.set(x, Y + 10, z, 'polished_andesite')
    H = 8
    for y in range(0, H + 1):
        rr = (r + .3) * math.sqrt(max(0.0, 1 - (y / H) ** 2))
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                if math.hypot(x - cx, z - cz) <= rr + .35:
                    cv.set(x, Y + 11 + y, z, 'waxed_oxidized_copper' if (x + z + y) % 7 else 'waxed_weathered_copper')
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        cv.fill(cx + dx, Y + 12 + H, cz + dz, cx + dx, Y + 13 + H, cz + dz, 'andesite_wall')
    cv.set(cx, Y + 12 + H, cz, 'tribalpower:shard_lamp[lit=true]')
    cv.fill(cx - 1, Y + 14 + H, cz - 1, cx + 1, Y + 14 + H, cz + 1, 'waxed_oxidized_cut_copper_slab[type=bottom]')
    cv.set(cx, Y + 15 + H, cz, 'lightning_rod')
    # buttresses between tall windows
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        bx, bz = round(cx + math.cos(a) * (r + 1)), round(cz + math.sin(a) * (r + 1))
        cv.fill(bx, Y + 1, bz, bx, Y + 8, bz, 'tribalpower:moss_agate_bricks')
        cv.set(bx, Y + 9, bz, 'tribalpower:moss_agate_brick_wall')
        cv.set(bx, Y + 1, bz, 'tribalpower:polished_moss_agate')
    for k in range(8):
        a = math.radians(45 * k)
        wx, wz = round(cx + math.cos(a) * r), round(cz + math.sin(a) * r)
        if (wx, wz) == (cx + r, cz):
            continue
        cv.fill(wx, Y + 5, wz, wx, Y + 8, wz, 'glass_pane')
    # windows between the shelves, facing the paths
    for dx, dz in ((r, 0), (0, r), (-r, 0), (0, -r)):
        cv.fill(cx + dx, Y + 5, cz + dz, cx + dx, Y + 7, cz + dz, 'glass')
    # door facing east toward the south road, an enchanting table ringed by shelves, lecterns
    cv.fill(cx + r, Y + 1, cz, cx + r, Y + 3, cz, 'air')
    cv.fill(cx + r - 1, Y + 1, cz, cx + r - 1, Y + 3, cz, 'air')
    cv.set(cx + r, Y + 1, cz, 'tribalpower:willow_door[facing=east,half=lower,hinge=left]')
    cv.set(cx + r, Y + 2, cz, 'tribalpower:willow_door[facing=east,half=upper,hinge=left]')
    cv.set(cx, Y + 1, cz, 'enchanting_table')
    for dx, dz, f in ((0, -3, 'south'), (0, 3, 'north'), (-3, 0, 'east')):
        cv.set(cx + dx, Y + 1, cz + dz, f'lectern[facing={f}]')
    cv.fill(cx, Y + 10, cz, cx, Y + 14, cz, 'chain')
    cv.set(cx, Y + 9, cz, 'lantern[hanging=true]')
    # pressed leaves on the shelves (one leaf of every plant they tended)
    leaves = ['minecraft:oak_leaves', 'minecraft:cherry_leaves', 'minecraft:azalea_leaves', 'minecraft:fern',
              'minecraft:lily_pad', 'minecraft:big_dripleaf', 'minecraft:birch_leaves', 'minecraft:spore_blossom']
    for i, item in enumerate(leaves):
        a = math.radians(200 + i * 20)
        x, z = cx + round(math.cos(a) * (r - 2)), cz + round(math.sin(a) * (r - 2))
        if cv.get(x, Y + 3, z) and 'bookshelf' in cv.get(x, Y + 3, z):
            fx, fz = cx - x, cz - z
            facing = ('east' if fx > 0 else 'west') if abs(fx) >= abs(fz) else ('south' if fz > 0 else 'north')
            ox, oz = {'east': (1, 0), 'west': (-1, 0), 'south': (0, 1), 'north': (0, -1)}[facing]
            cv.frame(x + ox, Y + 3, z + oz, facing, item)
    cv.sign(cx + r + 1, Y + 1, cz + 2, 'dark_oak_sign[rotation=12]', 'THE LEAF ARCHIVE', 'One leaf of every',
            'plant they tended', 'Read quietly')


LOOKOUT = (66, 52)


def lookout(cv, reserved):
    """The Gate Lookout: a tall tower on the south-east rim, from which the Loom-stitchers watched the paths."""
    cx, cz = LOOKOUT
    for x in range(cx - 4, cx + 5):
        for z in range(cz - 4, cz + 5):
            reserved.add((x, z))
    cv.fill(cx - 3, Y, cz - 3, cx + 3, Y + 26, cz + 3, 'tribalpower:march_stone_bricks')
    cv.fill(cx - 2, Y + 1, cz - 2, cx + 2, Y + 26, cz + 2, 'air')
    for x in (cx - 3, cx + 3):
        for z in (cz - 3, cz + 3):
            cv.fill(x, Y + 1, z, x, Y + 27, z, 'tribalpower:frostpine_log')
    for y in range(Y + 4, Y + 25, 5):
        for dx, dz in ((3, 0), (-3, 0), (0, 3)):      # the north wall carries the ladder: no window there
            cv.fill(cx + dx, y, cz + dz, cx + dx, y + 1, cz + dz, 'tribalpower:lit_blue_quartz_glass_pane')
    # ladder up the inside of the north wall; floors every ten blocks with a hatch
    for y in range(Y + 1, Y + 27):
        cv.set(cx, y, cz - 2, 'ladder[facing=south]')
    for y in (Y + 10, Y + 20):
        cv.fill(cx - 2, y, cz - 2, cx + 2, y, cz + 2, 'tribalpower:frostpine_planks')
        cv.set(cx, y, cz - 2, 'ladder[facing=south]')
        cv.set(cx + 1, y + 1, cz + 1, 'lantern')
    cv.fill(cx - 4, Y + 27, cz - 4, cx + 4, Y + 27, cz + 4, 'tribalpower:march_stone_bricks')
    cv.set(cx, Y + 27, cz - 2, 'tribalpower:frostpine_trapdoor[facing=south,half=top,open=false]')
    for x in range(cx - 4, cx + 5):
        for z in range(cz - 4, cz + 5):
            if max(abs(x - cx), abs(z - cz)) == 4:
                cv.set(x, Y + 28, z, 'tribalpower:march_stone_brick_wall')
    # door on the west side
    cv.set(cx - 3, Y + 1, cz, 'tribalpower:frostpine_door[facing=west,half=lower,hinge=left]')
    cv.set(cx - 3, Y + 2, cz, 'tribalpower:frostpine_door[facing=west,half=upper,hinge=left]')
    cv.sign(cx - 4, Y + 1, cz + 2, 'dark_oak_sign[rotation=4]', 'GATE LOOKOUT', 'They watched the paths', 'from here',
            'Climb, look out')


FOUNTAIN = (-22, 33)


def springs(cv):
    """The fountain in the south lawn, with an axolotl."""
    # fountain west of the south road
    cx, cz = FOUNTAIN
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 3, cz + 4):
            dd = max(abs(x - cx), abs(z - cz))
            cv.set(x, Y, z, 'stone_bricks' if dd == 3 else 'water' if dd < 3 else 'stone_bricks')
            if dd == 3:
                cv.set(x, Y + 1, z, 'stone_brick_slab[type=bottom]')
            elif dd < 3:
                cv.set(x, Y - 1, z, 'mossy_stone_bricks')
    cv.fill(cx, Y, cz, cx, Y + 2, cz, 'chiseled_stone_bricks')
    cv.set(cx, Y + 3, cz, 'water')
    for dx, dz in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
        cv.set(cx + dx, Y, cz + dz, 'sea_pickle[pickles=3,waterlogged=true]')
    return {(x, z) for x in range(cx - 4, cx + 5) for z in range(cz - 4, cz + 5)}


def rim_wall(cv, reserved, openings):
    """A mossy parapet around the rim, lanterns on the posts; the roads keep their own rails."""
    edge = edge_cells(cv.surface)
    for (x, z) in sorted(edge):
        if (x, z) in openings:
            continue
        cv.set(x, Y, z, 'mossy_stone_bricks' if hash2(x, z, 51) < .5 else 'stone_bricks')
        cv.set(x, Y + 1, z, 'mossy_stone_brick_wall' if hash2(x, z, 52) < .5 else 'stone_brick_wall')
        if hash2(x, z, 53) < .06:
            cv.set(x, Y + 2, z, 'lantern')


def islets(cv):
    """Fragments of the old world drifting in the void around the Hall."""
    spots = [(-104, 58, -27, 5, 'cherry'), (97, 72, -51, 6, 'azalea'), (-95, 70, 73, 4, 'amethyst'),
             (95, 55, 58, 4, 'ruin'), (-47, 78, -93, 5, 'archwood'), (52, 60, -92, 4, 'amethyst'),
             (6, 52, 98, 5, 'cherry'), (-108, 66, 25, 3, 'ruin')]     # each clear of the rim by 4 blocks
    for cx, cy, cz, r, kind in spots:
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                dd = math.hypot(x - cx, z - cz) + noise(x, z, 3, cx) * 1.5
                if dd > r:
                    continue
                depth = int((r - dd) * 1.6) + 1
                cv.fill(x, cy - depth, z, x, cy - 1, z, 'stone' if hash2(x, z, 61) < .7 else 'tuff')
                cv.set(x, cy, z, 'grass_block')
                if hash2(x, z, 62) < .1:
                    cv.set(x, cy - depth - 1, z, 'hanging_roots')
        if kind in ('cherry', 'azalea', 'archwood'):
            tree(cv, cx, cz, kind, 5, y=cy)
        elif kind == 'amethyst':
            cv.set(cx, cy, cz, 'budding_amethyst')
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cv.set(cx + dx, cy + 1, cz + dz, 'amethyst_cluster[facing=up]')
            cv.set(cx, cy + 1, cz, 'amethyst_cluster[facing=up]')
        else:
            cv.fill(cx, cy + 1, cz, cx, cy + 3, cz, 'stone_bricks')
            cv.set(cx + 1, cy + 1, cz, 'cracked_stone_bricks')
            cv.set(cx, cy + 4, cz, 'stone_brick_slab[type=bottom]')
            cv.set(cx - 1, cy + 1, cz, 'soul_lantern')


# ---------------------------------------------------------------------------------------------------------------------

DRUM = (40, 34)


def drum_circle(cv, reserved):
    """The Drum Circle: two Songkeeper Drums side by side (duel a friend, or play alone), Drumhearts behind them,
    an audience ring of benches."""
    cx, cz = DRUM
    for x in range(cx - 9, cx + 10):
        for z in range(cz - 8, cz + 9):
            dd = math.hypot(x - cx, z - cz)
            if dd > 8.5 or (x, z) not in cv.surface:
                continue
            reserved.add((x, z))
            cv.set(x, Y, z, 'tribalpower:moss_agate_bricks' if dd > 7.5 else 'tribalpower:polished_moonstone'
                   if dd > 4.5 else 'tribalpower:moonstone_bricks')
    # the stage, one step up, the drums on it facing the audience (south)
    for x in range(cx - 4, cx + 5):
        for z in range(cz - 4, cz):
            if math.hypot(x - cx, (z - cz) * 1.3) <= 4.6:
                cv.set(x, Y + 1, z, 'tribalpower:moss_agate_bricks')
    cv.set(cx - 1, Y + 2, cz - 2, 'tribalpower:songkeeper_drum')
    cv.set(cx + 1, Y + 2, cz - 2, 'tribalpower:songkeeper_drum')
    for x in range(cx - 2, cx + 3):
        cv.set(x, Y + 2, cz - 1, 'tribalpower:woven_mat')
    # Drumhearts and braziers behind, a Drumheart banner, a rain chime to keep time
    for x in (cx - 3, cx + 3):
        cv.set(x, Y + 2, cz - 3, 'tribalpower:drumheart')
        cv.set(x, Y + 3, cz - 3, 'tribalpower:ritual_brazier')
    cv.set(cx, Y + 2, cz - 4, 'tribalpower:drumheart')
    cv.fill(cx - 1, Y + 2, cz - 5, cx + 1, Y + 5, cz - 5, 'tribalpower:moss_agate_bricks')
    cv.set(cx, Y + 4, cz - 4, 'tribalpower:tribe_banner[facing=south,tribe=4,wall=true]')
    cv.set(cx, Y + 6, cz - 5, 'tribalpower:ember_bowl[lit=true]')
    # the audience: a half ring of benches facing the stage
    for a in range(200, 341, 28):
        r = math.radians(a)
        x, z = round(cx + math.cos(r) * -6.5), round(cz - math.sin(r) * 6.5)
        if cv.air(x, Y + 1, z) and cv.air(x + 1, Y + 1, z):
            cv.set(x, Y + 1, z, 'tribalpower:oak_tribal_bench[facing=north,part=left]')
            cv.set(x + 1, Y + 1, z, 'tribalpower:oak_tribal_bench[facing=north,part=right]')
    for x, z in ((cx - 7, cz - 3), (cx + 7, cz - 3), (cx - 6, cz + 4), (cx + 6, cz + 4)):
        cv.set(x, Y + 1, z, 'polished_deepslate_wall')
        cv.fill(x, Y + 2, z, x, Y + 3, z, 'dark_oak_fence')
        cv.set(x, Y + 4, z, 'tribalpower:spirit_lantern')
    cv.sign(cx, Y + 1, cz + 7, 'dark_oak_sign[rotation=0]', 'THE DRUM CIRCLE', 'Stand at a drum', 'Duel a friend',
            'or play alone')


PADDOCK = (-84, -66, 14, 30)
GARDEN = (-86, -70, -22, -8)


def paddock(cv, reserved):
    """The west paddock: tribe-coloured sheep, and the spirit herd grazing."""
    x0, x1, z0, z1 = PADDOCK
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            reserved.add((x, z))
            edge = x in (x0, x1) or z in (z0, z1)
            if edge and (x, z) in cv.surface:
                cv.set(x, Y + 1, z, 'oak_fence')
    cv.set(x0 + 8, Y + 1, z0, 'oak_fence_gate[facing=north,open=false,in_wall=false]')
    cv.fill(x0 + 3, Y + 1, z1 - 4, x0 + 4, Y + 1, z1 - 3, 'hay_block')     # props stand clear of the fence: nothing to hop over it from
    cv.set(x1 - 4, Y + 1, z1 - 3, 'water_cauldron[level=3]')
    cv.set(x1 - 5, Y + 1, z1 - 3, 'water_cauldron[level=3]')
    cv.set(x0 + 3, Y + 1, z0 + 3, 'tribalpower:offering_table')
    cv.sign(x0 + 7, Y + 1, z0 - 1, 'oak_sign[rotation=8]', 'THE PADDOCK', 'Sheep of nine colours', 'and the spirit herd')


def garden(cv, reserved):
    """The Pad-keepers' garden west of their shop: gysahl, wheat and carrots, a coop, a scarecrow."""
    x0, x1, z0, z1 = GARDEN
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if (x, z) not in cv.surface:
                continue
            reserved.add((x, z))
            edge = x in (x0, x1) or z in (z0, z1)
            if edge:
                cv.set(x, Y + 1, z, 'spruce_fence')
                continue
            row = (z - z0) % 4
            if row == 0:
                cv.set(x, Y, z, 'water')
                continue
            cv.set(x, Y, z, 'farmland[moisture=7]')
            crop = {1: 'chocobosreborn:gysahl_green[age=4]', 2: 'wheat[age=7]', 3: 'carrots[age=7]'}[row]
            if x > x0 + 9:
                crop = {1: 'pamhc2crops:pamtomatocrop[age=7]', 2: 'pamhc2crops:pamstrawberrycrop[age=7]',
                        3: 'pamhc2crops:pamlettucecrop[age=7]'}[row]
            cv.set(x, Y + 1, z, crop)
    cv.set(x0 + 8, Y + 1, z1, 'spruce_fence_gate[facing=south,open=false,in_wall=false]')
    # scarecrow
    sx, sz = x0 + 7, z0 + 3
    cv.set(sx, Y, sz, 'coarse_dirt')
    cv.fill(sx, Y + 1, sz, sx, Y + 2, sz, 'spruce_fence')
    cv.set(sx, Y + 3, sz, 'carved_pumpkin[facing=east]')
    cv.set(sx - 1, Y + 2, sz, 'spruce_fence')
    cv.set(sx + 1, Y + 2, sz, 'spruce_fence')
    # the farmer's composter and a coop for the hens
    cv.set(x1 + 1, Y + 1, z1 - 1, 'composter[level=3]')
    cv.set(x1 + 1, Y + 1, z0 + 1, 'hay_block')


def signpost(cv):
    """A post south of the pad that points the way; and the town bell where folk gather in the afternoon."""
    x, z = 0, 10
    cv.fill(x, Y + 1, z, x, Y + 3, z, 'stripped_dark_oak_log')
    cv.set(x, Y + 4, z, 'lantern')
    cv.sign(x - 1, Y + 2, z, 'dark_oak_wall_sign[facing=west]', 'MARKET WEST', 'Pad-keepers', 'Saddle & Seed', 'Paddock')
    cv.sign(x + 1, Y + 2, z, 'dark_oak_wall_sign[facing=east]', 'MARKET EAST', 'Grit-singers', 'Drumheart Curios',
            'Drum Circle')
    cv.sign(x, Y + 2, z + 1, 'dark_oak_wall_sign[facing=south]', 'SOUTH ROAD', "Esther's Roost", 'Whiskerwind',
            'Leaf Archive')
    cv.sign(x, Y + 3, z + 1, 'dark_oak_wall_sign[facing=south]', 'NORTH', 'The Cut Loom', 'Purring Hearth',
            "Stitchers' Chapel")
    # meeting bell on the plaza rim
    bx, bz = -12, 12
    cv.fill(bx - 1, Y + 1, bz, bx - 1, Y + 3, bz, 'stripped_spruce_log')
    cv.fill(bx + 1, Y + 1, bz, bx + 1, Y + 3, bz, 'stripped_spruce_log')
    cv.set(bx - 1, Y + 4, bz, 'spruce_slab[type=bottom]')
    cv.set(bx, Y + 4, bz, 'spruce_slab[type=bottom]')
    cv.set(bx + 1, Y + 4, bz, 'spruce_slab[type=bottom]')
    cv.set(bx, Y + 3, bz, 'bell[attachment=double_wall,facing=east]')


# ---------------------------------------------------------------------------------------------------------------------
# Loom's End was raised by everyone who reached the edge: the nine tribes lead, and every craft of the sky left its
# mark. Each piece below names the mods whose work it shows.

RELICS = ['rootheart', 'grindcore', 'thornseed', 'edgestep', 'drumpulse', 'cogloop', 'hivecall', 'sealmark',
          'loomthread', 'lintwisp', 'knotcharm', 'firstcut_shard', 'overweaver_shuttle']


def loom_cogwork(cv):
    """Create: the Loom was a machine; its great cogs still hang on the uprights."""
    z0 = LOOM_Z
    for side in (-1, 1):
        x = 17 * side
        cv.set(x, Y + 15, z0, 'create:large_cogwheel[axis=x]')
        cv.set(x, Y + 18, z0 - 1, 'create:cogwheel[axis=x]')
        cv.fill(x, Y + 19, z0 - 1, x, Y + 26, z0 - 1, 'create:shaft[axis=y]')
    cv.fill(-13, Y + 7, z0, 13, Y + 7, z0, 'create:shaft[axis=x]')


def artificers_yard(cv, reserved):
    """Pattern-weavers' yard, where every machine-craft of the sky keeps a bench: Create, Create Crafts & Additions,
    Create Enchantment Industry, Mekanism, Powah, Applied Energistics, Modular Routers, Pipez, Packaged Auto,
    Functional Storage and Sophisticated Storage, under Powah panels."""
    x0, x1, z0, z1 = 64, 80, -36, -22
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            reserved.add((x, z))
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            cv.set(x, Y, z, 'ae2:sky_stone_small_brick' if (x + z) % 5 else 'ae2:smooth_sky_stone_block')
            cv.fill(x, Y + 1, z, x, Y + 5, z, 'air')
    # casing pillars, a copper-tile roof with quartz-glass skylights, Powah panels along the south eave
    for x in range(x0, x1 + 1, 4):
        for z in (z0, z1):
            cv.fill(x, Y + 1, z, x, Y + 5, z, 'create:andesite_casing')
    for z in range(z0, z1 + 1, 7):
        for x in (x0, x1):
            cv.fill(x, Y + 1, z, x, Y + 5, z, 'create:andesite_casing')
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            cv.set(x, Y + 6, z, 'ae2:quartz_glass' if (x - x0) % 4 == 2 and z0 < z < z1 else 'create:copper_tiles')
    for x in range(x0, x1 + 1, 2):
        cv.set(x, Y + 7, z1, 'powah:solar_panel_basic')
    # the back wall: machines at the bench, drawers and barrels above, a pipe run under the roof
    cv.fill(x0, Y + 1, z0, x1, Y + 5, z0, 'create:brass_casing')
    bench = ['mekanism:metallurgic_infuser[facing=south]', 'mekanism:enrichment_chamber[facing=south,active=false]',
             'mekanism:crusher[facing=south,active=false]', 'mekanism:basic_energy_cube[facing=south]',
             'powah:energy_cell_basic', 'powah:furnator_basic[facing=south]', 'ae2:inscriber[facing=south,spin=0]',
             'ae2:charger[facing=south,spin=0]', 'ae2:drive[facing=south,spin=0]',
             'createaddition:alternator[facing=south]', 'createaddition:electric_motor[facing=south]',
             'modularrouters:modular_router[facing=south,active=false]', 'packagedauto:packager',
             'create_enchantment_industry:printer[facing=south]', 'mekanism:basic_fluid_tank[active=false]']
    for i, b in enumerate(bench):
        cv.set(x0 + 1 + i, Y + 1, z0 + 1, b)
        cv.set(x0 + 1 + i, Y + 2, z0 + 1, 'functionalstorage:oak_4[facing=south,subfacing=down]' if i % 2
               else 'sophisticatedstorage:barrel[facing=south,flat_top=false]')
    cv.fill(x0 + 1, Y + 4, z0 + 1, x1 - 1, Y + 4, z0 + 1, 'pipez:universal_pipe')
    # west bay: Create's own machines
    cv.set(x0 + 1, Y + 1, z0 + 4, 'create:encased_fan[facing=up]')
    cv.fill(x0 + 1, Y + 1, z0 + 6, x0 + 1, Y + 2, z0 + 6, 'create:fluid_tank')
    cv.set(x0 + 1, Y + 1, z0 + 8, 'create:blaze_burner')
    cv.set(x0 + 1, Y + 3, z0 + 8, 'create:deployer[facing=down,axis_along_first=false]')
    cv.set(x0 + 1, Y + 1, z0 + 10, 'createaddition:tesla_coil[facing=up,powered=false]')
    cv.set(x0 + 2, Y + 5, z0 + 5, 'create:large_cogwheel[axis=z]')
    cv.fill(x0 + 2, Y + 5, z0 + 6, x0 + 2, Y + 5, z1 - 1, 'create:shaft[axis=z]')
    cv.set(x0 + 2, Y + 1, z1 - 1, 'create:hand_crank[facing=up]')
    # work tables down the middle
    for i, b in enumerate(['crafting_table', 'silentgear:gear_smithing_table', 'ae2:sky_stone_chest',
                           'irons_spellbooks:arcane_anvil[facing=east]', 'smithing_table', 'create:brass_block']):
        cv.set(x0 + 5 + i * 2, Y + 1, z0 + 7, b)
    # east wall: a dormant Mekanism teleporter arch, and the yard's sign
    for y in range(Y + 1, Y + 6):
        for z in range(z0 + 4, z0 + 8):
            edge = y in (Y + 1, Y + 5) or z in (z0 + 4, z0 + 7)
            cv.set(x1, y, z, 'mekanism:teleporter_frame' if edge else 'air')
    cv.sign(x0 + 8, Y + 1, z1 + 1, 'dark_oak_sign[rotation=0]', "ARTIFICERS' YARD", 'Every craft of the sky', 'keeps a bench here',
            'Pattern-weavers')
    for x in range(x0 + 2, x1, 4):
        cv.set(x, Y + 5, z0 + 7, 'ae2:quartz_fixture[facing=down,odd=false]')
    # lane from the market street
    for x in range(70, 73):
        for z in range(z1 + 1, -4):
            if (x, z) in cv.surface:
                reserved.add((x, z))
                pave(cv, x, z)


WINDMILL = (124, 0, 7)


def windward_mill(cv, reserved):
    """An islet off the east rim with a Create windmill, reached by a Macaw's rope bridge from Market Street."""
    cx, cz, r = WINDMILL
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            dd = math.hypot(x - cx, z - cz) + noise(x, z, 3, 7) * 1.2
            if dd > r:
                continue
            depth = int((r - dd) * 2.2) + 2
            cv.fill(x, Y - depth, z, x, Y - 1, z, 'stone' if hash2(x, z, 81) < .7 else 'tuff')
            cv.set(x, Y, z, 'grass_block')
            if hash2(x, z, 82) < .1:
                cv.set(x, Y - depth - 1, z, 'hanging_roots')
    # the mill tower: march stone, a frostpine cap, the bearing on the east face with four canvas arms
    cv.fill(cx - 2, Y + 1, cz - 2, cx + 2, Y + 9, cz + 2, 'tribalpower:march_stone_bricks')
    cv.fill(cx - 1, Y + 1, cz - 1, cx + 1, Y + 8, cz + 1, 'air')
    cv.set(cx - 2, Y + 1, cz, 'tribalpower:frostpine_door[facing=west,half=lower,hinge=left]')
    cv.set(cx - 2, Y + 2, cz, 'tribalpower:frostpine_door[facing=west,half=upper,hinge=left]')
    for y in (Y + 4, Y + 7):
        for x, z in ((cx - 2, cz + 1), (cx + 2, cz - 1), (cx, cz - 2), (cx, cz + 2)):
            cv.set(x, y, z, 'tribalpower:lit_blue_quartz_glass')
    for r2 in range(4):
        cv.fill(cx - 3 + r2, Y + 10 + r2, cz - 3 + r2, cx + 3 - r2, Y + 10 + r2, cz + 3 - r2, 'tribalpower:frostpine_planks')
    cv.set(cx, Y + 14, cz, 'supplementaries:wind_vane')
    hub = (cx + 3, Y + 8, cz)
    cv.set(cx + 2, Y + 8, cz, 'create:windmill_bearing[facing=east]')
    cv.set(*hub, 'create:shaft[axis=x]')
    for i in range(1, 7):
        for w in (-1, 0, 1):
            cv.set(hub[0], hub[1] + i, cz + w, 'create:white_sail[facing=east]')
            if i <= 5:      # the lower arm stops a block short of the others
                cv.set(hub[0], hub[1] - i, cz + w, 'create:white_sail[facing=east]')
            cv.set(hub[0], hub[1] + w, cz + i, 'create:white_sail[facing=east]')
            cv.set(hub[0], hub[1] + w, cz - i, 'create:white_sail[facing=east]')
    # millstones and sacks inside
    cv.set(cx, Y + 1, cz, 'create:millstone')
    cv.set(cx + 1, Y + 1, cz + 1, 'supplementaries:sack')
    cv.set(cx - 1, Y + 1, cz + 1, 'farmersdelight:rice_bale')
    cv.sign(cx - 4, Y + 1, cz + 2, 'dark_oak_sign[rotation=4]', 'THE WINDWARD MILL', 'The wind off the', 'edge still turns', 'the sails')
    # the rope bridge from the rim
    rim_x = max(x for (x, z) in cv.surface if z == 0)
    for x in range(rim_x - 1, cx - r + 2):
        cv.set(x, Y, 0, 'mcwbridges:rope_oak_bridge[facing=east,connection=base]')
        cv.fill(x, Y + 1, 0, x, Y + 3, 0, 'air')
    for z in (-1, 1):
        cv.set(rim_x - 1, Y + 1, z, 'oak_fence')
        cv.set(rim_x - 1, Y + 2, z, 'lantern')
    return {(x, 0) for x in range(rim_x - 3, rim_x + 1)}


def apiary(cv, reserved):
    """Colony-keepers' apiary: Productive Bees hives in a meadow south of their gate booth."""
    x0, x1, z0, z1 = 20, 32, 64, 76
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if (x, z) not in cv.surface:
                continue
            reserved.add((x, z))
            edge = x in (x0, x1) or z in (z0, z1)
            if edge:
                cv.set(x, Y + 1, z, 'tribalpower:bellcap_fence')
            elif hash2(x, z, 91) < .55:
                cv.set(x, Y + 1, z, FLOWERS[int(hash2(x, z, 92) * len(FLOWERS))])
    cv.set(x0, Y + 1, 74, 'tribalpower:bellcap_fence_gate[facing=east,open=false,in_wall=false]')
    for x, z in ((23, 67), (29, 67), (23, 73), (29, 73)):
        cv.set(x, Y + 1, z, 'tribalpower:bellcap_log')
        cv.set(x, Y + 2, z, 'productivebees:advanced_oak_beehive[expanded=up,facing=south,honey_level=5]')
        cv.set(x, Y + 3, z, 'productivebees:expansion_box_oak[expanded=up,facing=south]')
    cv.set(26, Y + 1, 70, 'productivebees:centrifuge')
    cv.set(26, Y + 1, 71, 'beehive[facing=south,honey_level=5]')
    cv.sign(26, Y + 1, z0 - 1, 'dark_oak_sign[rotation=8]', "COLONY-KEEPERS'", 'APIARY', 'Mind the bees')


def old_grove(cv, reserved):
    """The Old Grove, where the Rootbinders let the hedge-mages keep their circles: a Nature's Aura ancient tree and
    altar, an Ars Nouveau archwood with its brazier, an Occultism chalk circle, an Iron's Spellbooks brazier."""
    cx, cz, r = -66, -56, 7
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            if math.hypot(x - cx, z - cz) <= r + .4 and (x, z) in cv.surface:
                reserved.add((x, z))
                cv.set(x, Y, z, 'moss_block' if hash2(x, z, 95) < .6 else 'podzol')
    tree(cv, cx - 3, cz - 2, 'ancient', 7)
    cv.set(cx - 1, Y + 1, cz - 4, 'naturesaura:nature_altar')
    for dx, dz in ((-5, 1), (-4, 3), (-1, 1), (-6, -2)):
        if cv.air(cx + dx, Y + 1, cz + dz):
            cv.set(cx + dx, Y + 1, cz + dz, 'naturesaura:aura_bloom')
    tree(cv, cx + 4, cz - 4, 'archwood', 6)
    cv.set(cx + 2, Y + 1, cz - 1, 'ars_nouveau:ritual_brazier')
    cv.set(cx + 4, Y + 1, cz + 1, 'ars_nouveau:arcane_pedestal[facing=up]')
    # the chalk circle: a golden bowl on an otherstone pedestal ringed with white glyphs and four large candles
    ox, oz = cx + 1, cz + 3
    cv.set(ox, Y + 1, oz, 'occultism:otherstone_pedestal')
    cv.set(ox, Y + 2, oz, 'occultism:golden_sacrificial_bowl')
    k = 0
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if max(abs(dx), abs(dz)) == 2 and cv.air(ox + dx, Y + 1, oz + dz):
                cv.set(ox + dx, Y + 1, oz + dz, f'occultism:chalk_glyph_white[facing=north,sign={k % 14}]')
                k += 3
    for dx, dz in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        if cv.air(ox + dx, Y + 1, oz + dz):
            cv.set(ox + dx, Y + 1, oz + dz, 'occultism:large_candle_purple')
    cv.set(cx - 4, Y + 1, cz + 4, 'irons_spellbooks:brazier[hanging=false,lit=true]')
    cv.sign(cx + 6, Y + 1, cz + 1, 'dark_oak_sign[rotation=12]', 'THE OLD GROVE', 'Rootbinders tend it', 'Leave the circle', 'as you found it')


def dress_interiors(cv):
    """Every craft furnishes the town: Farmer's Delight and Handcrafted in the Hearth, relics and Voidloom in the
    Chapel, Iron's Spellbooks and Create's brass shelves in the Archive, a Pattern-weavers clock on the Lookout."""
    # the Hearth kitchen (Local frame of purring_hearth)
    H = Local(cv, 'S', -60, -30)
    H.set(1, 1, 6, 'farmersdelight:stove[facing={right},lit=true]')
    H.set(1, 2, 6, 'farmersdelight:cooking_pot[facing={right},support=tray]')
    H.set(1, 1, 7, 'handcrafted:oven[facing={right},lit=true]')
    H.set(1, 1, 8, 'farmersdelight:cabbage_crate')
    H.set(1, 4, 6, 'handcrafted:kitchen_hood[facing={right}]')
    H.set(1, 2, 8, 'farmersdelight:cutting_board[facing={right}]')     # on the crate: the bar keeps its slab
    for u, v in ((10, 2), (10, 6)):
        H.set(u, 1, v, 'handcrafted:spruce_table')
        H.set(u - 1, 1, v, 'handcrafted:spruce_chair[facing={right}]')
        H.set(u + 1, 1, v, 'handcrafted:spruce_chair[facing={left}]')
        H.set(u, 1, v + 1, 'handcrafted:spruce_chair[facing={front}]')
    H.set(13, 1, 1, 'sophisticatedbackpacks:backpack[facing={back}]')
    for i, item in enumerate(['farmersdelight:beef_stew', 'pamhc2foodcore:applepieitem', 'farmersdelight:apple_pie',
                              'chocobosreborn:gysahl_green']):
        H.frame(1 + i, 3, 1, 'back', item)
    # the Chapel: thirteen Woven Relics on the walls, the Voidloom by the altar, Driftwrecks plinths with idols
    C = Local(cv, 'S', 36, -30)
    for i, relic in enumerate(RELICS):
        u, v, facing = (1, 1 + i * 2, 'right') if i < 7 else (9, 2 + (i - 7) * 2, 'left')
        C.frame(u, 6, v, facing, f'guardians:relic_{relic}')
    C.set(1, 1, 16, 'voidloom:loomframe')
    C.set(9, 1, 16, 'voidloom:tension_barrel')
    for u in (1, 9):
        C.set(u, 1, 13, 'driftwrecks:trophy_plinth')
        C.set(u, 2, 13, 'driftwrecks:thread_idol')
    for u in (3, 7):
        C.set(u, 1, 12, 'occultism:large_candle_white')
    C.frame(5, 2, 16, 'front', 'voidloom:void_yarn')     # under the tapestry, not inside it
    # the Lookout becomes the Pattern-weavers' clock tower: a clock face on each side, a vane on top
    lx, lz = LOOKOUT
    for dx, dz, f in ((3, 0, 'east'), (-3, 0, 'west'), (0, 3, 'south'), (0, -3, 'north')):
        cv.set(lx + dx, Y + 22, lz + dz, f'supplementaries:clock_block[facing={f},two_faced=false]')
    # a crown: corner pillars and a blue hip roof over the platform, the vane on its peak
    for dx in (-4, 4):
        for dz in (-4, 4):
            cv.fill(lx + dx, Y + 28, lz + dz, lx + dx, Y + 31, lz + dz, 'tribalpower:chiseled_march_stone_bricks')
    cv.set(lx, Y + 28, lz, 'tribalpower:shard_lamp[lit=true]')
    for k in range(4):
        r = 5 - k
        y = Y + 32 + k
        for x in range(lx - r, lx + r + 1):
            for z in range(lz - r, lz + r + 1):
                if max(abs(x - lx), abs(z - lz)) != r:
                    continue
                if abs(x - lx) == r and abs(z - lz) == r:
                    cv.set(x, y, z, 'blue_terracotta')
                elif z - lz == -r:
                    cv.set(x, y, z, 'mcwroofs:blue_terracotta_roof[facing=south,half=bottom,shape=straight]')
                elif z - lz == r:
                    cv.set(x, y, z, 'mcwroofs:blue_terracotta_roof[facing=north,half=bottom,shape=straight]')
                elif x - lx == -r:
                    cv.set(x, y, z, 'mcwroofs:blue_terracotta_roof[facing=east,half=bottom,shape=straight]')
                else:
                    cv.set(x, y, z, 'mcwroofs:blue_terracotta_roof[facing=west,half=bottom,shape=straight]')
    cv.fill(lx - 1, Y + 36, lz - 1, lx + 1, Y + 36, lz + 1, 'blue_terracotta')
    cv.set(lx, Y + 37, lz, 'supplementaries:wind_vane')
    cv.set(lx - 1, Y + 1, lz + 1, 'cartography_table')
    cv.set(lx - 1, Y + 11, lz + 1, 'comforts:hammock_cyan[facing=south,part=foot]')
    cv.set(lx - 1, Y + 11, lz + 2, 'comforts:hammock_cyan[facing=south,part=head]')
    cv.set(lx - 1, Y + 21, lz + 1, 'handcrafted:spruce_desk[facing=south]')
    cv.set(lx - 1, Y + 22, lz + 1, 'supplementaries:globe[facing=south]')
    # the Archive: Iron's Spellbooks at work among the shelves
    ax, az = ARCHIVE[0], ARCHIVE[1]
    cv.set(ax + 2, Y + 1, az + 3, 'irons_spellbooks:inscription_table[facing=north]')
    cv.set(ax + 2, Y + 1, az - 3, 'irons_spellbooks:scroll_forge[facing=south]')
    cv.set(ax - 2, Y + 1, az + 2, 'irons_spellbooks:book_stack[facing=east]')
    cv.set(ax + 1, Y + 1, az - 1, 'mysticalagriculture:essence_vessel')
    # Roost wares: the spirit herd's tack beside the chocobo steward
    R = Local(cv, 'E', -5, 78)
    for (u, dy, v, facing), item in zip([(1, 2, 2, 'right'), (1, 2, 3, 'right'), (1, 2, 4, 'right'),
                                          (9, 2, 2, 'left'), (9, 2, 3, 'left'), (9, 2, 4, 'left')],
                                         ['shamanicmounts:shamanic_saddle', 'shamanicmounts:saddle_bags',
                                          'shamanicmounts:herd_book', 'chocobosreborn:gysahl_green',
                                          'shamanicmounts:diamond_apple', 'minecraft:golden_carrot']):
        R.frame(u, dy, v, facing, item)
    R.set(9, 1, 0, 'sophisticatedbackpacks:backpack[facing={front}]')


def street_dress(cv):
    """Supplementaries planters along Market Street, Amendments hanging pots, Botany Pots on the fountain rim."""
    for x in (-66, -86, -31, 31, 66, 86):
        for z in (-4, 4):
            if cv.air(x, Y + 1, z) and base_id(cv.get(x, Y, z) or 'air') != 'air':
                cv.set(x, Y + 1, z, 'supplementaries:planter[extended=false]')
                cv.set(x, Y + 2, z, FLOWERS[(x + z) % len(FLOWERS)])
    for dx in (-3, 3):
        cv.set(FOUNTAIN[0] + dx, Y + 2, FOUNTAIN[1] + 3, 'botanypots:terracotta_botany_pot')


HOME_STYLE = {   # the nine peoples' homes: wood, walls, footing, Macaw's roof, Handcrafted furniture wood, set piece
    'soil': dict(PALETTES['soil'], roof=('mcwroofs:thatch_roof', None, 'hay_block'), hc='spruce',
                 piece=['composter[level=5]', 'hay_block']),
    'stone': dict(PALETTES['stone'], roof=('mcwroofs:stone_bricks_roof', None, 'stone_bricks'), hc='dark_oak',
                  piece=['stonecutter[facing={right}]', 'exdeorum:stone_barrel']),
    'sprout': dict(tp_wood('willow'), wall='tribalpower:moss_agate_bricks', base='tribalpower:march_cobble',
                   roof=('mcwroofs:grass_roof', None, 'moss_block'), dye='green', hc='oak', tribe=2,
                   glass='tribalpower:green_quartz_glass_pane',
                   piece=['botanypots:terracotta_botany_pot', 'mysticalagriculture:inferium_block']),
    'claw': dict(log='dark_oak_log', wood='stripped_dark_oak_log', plank='dark_oak_planks', stair='dark_oak_stairs',
                 slab='dark_oak_slab', fence='dark_oak_fence', door='dark_oak_door', trapdoor='dark_oak_trapdoor',
                 wall='tribalpower:march_cobble', base='tribalpower:march_stone_bricks', dye='red', tribe=3,
                 roof=('mcwroofs:red_terracotta_roof', None, 'red_terracotta'), hc='dark_oak',
                 glass='tribalpower:red_quartz_glass_pane',
                 piece=['irons_spellbooks:armor_pile[facing={right}]', 'sophisticatedbackpacks:backpack[facing={right}]']),
    'spark': dict(PALETTES['spark'], roof=('mcwroofs:orange_terracotta_roof', None, 'orange_terracotta'), hc='spruce',
                  piece=['note_block', 'tribalpower:ember_bowl[lit=true]']),
    'clock': dict(log='tribalpower:march_log', wood='tribalpower:march_log', plank='tribalpower:march_planks',
                  stair='tribalpower:march_planks_stairs', slab='tribalpower:march_planks_slab',
                  fence='tribalpower:march_fence', door='tribalpower:march_door', trapdoor='tribalpower:march_trapdoor',
                  wall='tribalpower:polished_moonstone', base='tribalpower:moonstone_bricks', dye='blue', tribe=5,
                  roof=('mcwroofs:blue_terracotta_roof', None, 'blue_terracotta'), hc='oak',
                  glass='tribalpower:blue_quartz_glass_pane',
                  piece=['create:clockwork_bearing[facing=up]', 'supplementaries:hourglass[facing=up]']),
    'swarm': dict(PALETTES['swarm'], roof=('mcwroofs:yellow_terracotta_roof', None, 'yellow_terracotta'), hc='oak',
                  piece=['beehive[facing={right},honey_level=5]', 'honey_block']),
    'sigil': dict(PALETTES['sigil'], roof=('mcwroofs:purple_terracotta_roof', None, 'purple_terracotta'), hc='dark_oak',
                  piece=['lectern[facing={right}]', 'occultism:large_candle_purple']),
    'spindle': dict(log='spruce_log', wood='stripped_spruce_log', plank='spruce_planks', stair='spruce_stairs',
                    slab='spruce_slab', fence='spruce_fence', door='spruce_door', trapdoor='spruce_trapdoor',
                    wall='calcite', base='tribalpower:moonstone_bricks', dye='cyan', tribe=8,
                    roof=('mcwroofs:cyan_terracotta_roof', None, 'cyan_terracotta'), hc='spruce',
                    glass='tribalpower:cyan_quartz_glass_pane', piece=['loom[facing={right}]', 'voidloom:tension_barrel']),
}


def home(cv, reserved, face, fx, fz, tribe, chimney=True):
    """A tribe home, 7 wide and 8 deep: footing, timber frame, tribe glass, the tribe's roof, a banner by the door,
    Handcrafted furniture inside and a set piece from the people's craft."""
    st = HOME_STYLE[tribe]
    L = Local(cv, face, fx, fz)
    w, d, h = 7, 8, 4
    L.fill(0, 0, 0, w - 1, 0, d - 1, st['base'])
    L.fill(1, 0, 1, w - 2, 0, d - 2, st['plank'])
    L.fill(0, 1, 0, w - 1, h, d - 1, st['wall'])
    L.fill(0, 1, 0, w - 1, 1, d - 1, st['base'])
    for u in (0, w - 1):
        for v in (0, d - 1):
            L.fill(u, 1, v, u, h, v, st['log'])
    L.fill(0, h, 0, w - 1, h, 0, st['log'] + '[axis={au}]')
    L.fill(0, h, d - 1, w - 1, h, d - 1, st['log'] + '[axis={au}]')
    L.fill(1, 1, 1, w - 2, h, d - 2, 'air')
    # windows in the tribe's quartz glass; the door in the tribe's wood
    for u in (1, 5):
        L.set(u, 2, 0, st['glass'])
        L.set(u, 1, -1, 'supplementaries:planter[extended=false]')
        L.set(u, 2, -1, FLOWERS[(fx + fz + u) % len(FLOWERS)])
    for v in (2, 5):
        L.fill(0, 2, v, 0, 3, v, st['glass'])
        L.fill(w - 1, 2, v, w - 1, 3, v, st['glass'])
    L.set(3, 1, 0, st['door'] + '[facing={front},half=lower,hinge=left]')
    L.set(3, 2, 0, st['door'] + '[facing={front},half=upper,hinge=left]')
    L.set(2, 3, -1, f'tribalpower:tribe_banner[facing={{front}},tribe={st["tribe"]},wall=true]')
    L.set(4, 1, -1, st['fence'])
    L.set(4, 2, -1, 'lantern')
    L.fill(2, 0, -2, 4, 0, -1, st['base'])
    top = gable_roof(L, w, d, h + 1, st, v0=-1, v1=d)
    # inside: a Handcrafted table and chairs, a shelf, the hearth, the people's own piece
    hc = st['hc']
    L.set(3, 1, 4, f'handcrafted:{hc}_table')
    L.set(2, 1, 4, f'handcrafted:{hc}_chair[facing={{right}}]')
    L.set(4, 1, 4, f'handcrafted:{hc}_chair[facing={{left}}]')
    L.set(1, 2, 3, f'handcrafted:{hc}_shelf[facing={{right}},shape=single,type=1]')
    L.set(5, 1, 6, 'furnace[facing={front},lit=true]')
    L.set(1, 1, 6, st['piece'][0])
    L.set(1, 1, 5, st['piece'][1])
    L.set(5, 1, 1, 'crafting_table')
    L.set(5, 1, 3, f"{st['dye']}_bed[facing={{back}},part=foot]")
    L.set(5, 1, 4, f"{st['dye']}_bed[facing={{back}},part=head]")
    L.fill(3, h, 3, 3, top - 1, 3, 'chain')          # the lantern hangs from the ridge
    L.set(3, h - 1, 3, 'lantern[hanging=true]')
    if chimney:
        L.fill(w - 2, h + 1, d - 2, w - 2, h + 5, d - 2, 'bricks')
        L.set(w - 2, h + 6, d - 2, 'campfire[lit=true,signal_fire=false]')
    for u in range(-1, w + 1):
        for v in range(-2, d + 1):
            reserved.add(L.xz(u, v))
    return L


HOMES = [   # face, front x, front z, people
    ('E', -6, -52, 'spindle'), ('W', 6, -58, 'claw'), ('E', -6, -62, 'sigil'), ('W', 6, -68, 'claw'),
    ('E', -6, -72, 'spindle'), ('W', 6, -78, 'clock'),
    ('S', 52, -44, 'stone'), ('S', 62, -44, 'clock'), ('S', -42, -50, 'soil'), ('S', -32, -52, 'sigil'),
    ('N', -20, 59, 'soil'), ('N', -30, 59, 'sprout'), ('N', -40, 60, 'sprout'),   # porches clear of their lane
    ('N', 50, 58, 'clock'), ('N', 40, 58, 'swarm'), ('W', 70, 20, 'spark'), ('W', 70, 30, 'stone'),
]


def homes(cv, reserved):
    for face, fx, fz, tribe in HOMES:
        home(cv, reserved, face, fx, fz, tribe)
    # lanes to the new homes
    lane(cv, reserved, [(x, z) for x in range(-47, -3) for z in (55, 56, 57)])
    lane(cv, reserved, [(x, z) for x in range(34, 51) for z in (53, 54, 55)])
    lane(cv, reserved, [(x, z) for x in (66, 67, 68) for z in range(5, 37)])
    lane(cv, reserved, [(x, z) for x in range(47, 69) for z in (-42, -41, -40)])
    lane(cv, reserved, [(x, z) for x in (47, 48, 49) for z in range(-42, -26)])
    lane(cv, reserved, [(x, z) for x in range(-45, -22) for z in (-47, -46, -45)])      # on to the Cut Loom
    lane(cv, reserved, [(x, z) for x in range(-30, -27) for z in (-49, -48)])           # the porch at z -50


CLUTTER = [
    ['supplementaries:planter[extended=false]', 'FLOWER'],
    ['barrel[facing=up]'],
    ['farmersdelight:carrot_crate'], ['farmersdelight:cabbage_crate'], ['farmersdelight:onion_crate'],
    ['hay_block', 'hay_block'],
    ['oak_log[axis=x]', 'oak_log[axis=x]'],
    ['supplementaries:sack'],
    ['decorated_pot[facing=south]'],
    ['stripped_oak_log', 'potted_fern'],
    ['composter[level=4]'],
    ['flowering_azalea'], ['azalea'],
    ['rose_bush[half=lower]', 'rose_bush[half=upper]'], ['lilac[half=lower]', 'lilac[half=upper]'],
    ['peony[half=lower]', 'peony[half=upper]'],
    ['LAMP'],
    ['tribalpower:march_stone_bricks', 'tribalpower:spirit_lantern'],
    ['exdeorum:oak_barrel'],
    ['beehive[facing=south,honey_level=2]'],
]


def roadside(cv, reserved):
    """Life along every street and lane: planters, crates, barrels, hay, woodpiles, sacks, bushes, lamps."""
    placed = []
    for (x, z) in sorted(cv.paved):
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if (nx, nz) in cv.paved or (nx, nz) not in cv.surface or (nx, nz) in reserved:
                continue
            if base_id(cv.get(nx, Y, nz) or 'air') not in ('grass_block', 'moss_block') or not cv.air(nx, Y + 1, nz):
                continue
            if hash2(nx, nz, 101) > .22 or any(abs(nx - a) + abs(nz - b) < 4 for a, b in placed):
                continue
            pick = CLUTTER[int(hash2(nx, nz, 102) * len(CLUTTER))]
            if pick[0] == 'LAMP':
                lamp_post(cv, nx, nz)
            else:
                for i, b in enumerate(pick):
                    if not cv.air(nx, Y + 1 + i, nz):
                        break
                    cv.set(nx, Y + 1 + i, nz, FLOWERS[(nx * 7 + nz) % len(FLOWERS)] if b == 'FLOWER' else b)
            placed.append((nx, nz))
            reserved.add((nx, nz))


def plaza_dress(cv):
    """Benches and planters on the rim of the Knot, facing the pad."""
    for a in range(0, 360, 40):
        r = math.radians(a)
        x, z = round(math.cos(r) * 23), round(math.sin(r) * 23)
        if abs(x) <= 4 or abs(z) <= 4 or not cv.air(x, Y + 1, z):
            continue
        facing = ('west' if x > 0 else 'east') if abs(x) >= abs(z) else ('north' if z > 0 else 'south')
        side = {'west': (0, 1), 'east': (0, -1), 'north': (-1, 0), 'south': (1, 0)}[facing]
        if not cv.air(x + side[0], Y + 1, z + side[1]):
            continue
        cv.set(x, Y + 1, z, f'tribalpower:oak_tribal_bench[facing={facing},part=left]')
        cv.set(x + side[0], Y + 1, z + side[1], f'tribalpower:oak_tribal_bench[facing={facing},part=right]')
        px, pz = x - side[0], z - side[1]
        if cv.air(px, Y + 1, pz):
            cv.set(px, Y + 1, pz, 'supplementaries:planter[extended=false]')
            cv.set(px, Y + 2, pz, FLOWERS[a // 40 % len(FLOWERS)])


HOME_FOLK = ['Hazel', 'Oren', 'Sable', 'Tamsin', 'Bram', 'Ivy', 'Quill', 'Rook', 'Maren', 'Fenn', 'Lark', 'Juno',
             'Pell', 'Sorrel', 'Tobin', 'Wick', 'Yarrow']


def lane(cv, reserved, cells):
    for (x, z) in cells:
        if (x, z) in cv.surface:
            reserved.add((x, z))
            pave(cv, x, z)


def villager_nbt(profession):
    """A townsperson with a trade but nothing to sell: empty offers, and one point of experience so the job sticks."""
    return ('{VillagerData:{profession:"minecraft:%s",level:2,type:"minecraft:plains"},Xp:1,Offers:{Recipes:[]}}'
            % profession)


TOWNSFOLK = [   # name, profession (workstation in town), where they start the day
    ('Nori', 'farmer', -78, -4), ('Tavi', 'mason', 36, 2), ('Ember', 'cleric', 42, 2), ('Lumi', 'shepherd', 44, -27),
    ('Wren', 'librarian', -40, 48), ('Pim', 'fisherman', -22, 40), ('Juniper', 'cartographer', 60, 50),
    ('Moss', 'butcher', -52, -26),
]
CATS = [('Button', -52, -35), ('Nimbus', 40, -34), ('Soot', -16, -16), ('Tansy', -30, 36), ('Moth', 18, 18),
        ('Cinder', 40, 28), ('Wisp', -58, 0), ('Pounce', 58, -2)]


def near(cx, cz, i, spread, seed):
    """A deterministic spot around (cx, cz) for the i-th animal of a flock."""
    return (cx + int((hash2(i, seed, 7) - .5) * 2 * spread), cz + int((hash2(seed, i, 8) - .5) * 2 * spread))


WALK_THROUGH = ('air', 'short_grass', 'fern', 'pink_petals', 'woven_mat', *FLOWERS)     # and every carpet


def ground_spot(cv, x, z):
    """The nearest cell to (x, z), ring by ring, where a walker stands on solid ground with two clear blocks above."""
    def ok(x, z):
        g = cv.get(x, Y, z)
        return (x, z) in cv.surface and g is not None and is_full(g) and base_id(g) != 'farmland' and             all(base_id(cv.get(x, y, z) or 'air') in WALK_THROUGH or base_id(cv.get(x, y, z)).endswith('carpet')
                for y in (Y + 1, Y + 2))
    for r in range(6):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if max(abs(dx), abs(dz)) == r and ok(x + dx, z + dz):
                    return x + dx, z + dz
    raise ValueError(f'no open ground near {x}, {z}')

# Founder genomes captured from the Shamanic Mounts spawn eggs (tools/hub_loomsend_founders.json), so the herd looks
# like its line rather than a random void-biome roll.
FOUNDERS_FILE = Path(__file__).with_name('hub_loomsend_founders.json')
FOUNDER_NBT = json.loads(FOUNDERS_FILE.read_text(encoding='utf-8')) if FOUNDERS_FILE.exists() else {}


def loomsend():
    cv = Canvas()
    island(cv)
    reserved = set()
    knot(cv, reserved)
    cut_loom(cv, reserved)
    gate_path(cv, reserved)
    market(cv, reserved)
    whiskerwind_road(cv, reserved)
    purring_hearth(cv, reserved)
    chapel(cv, reserved)
    archive(cv, reserved)
    lookout(cv, reserved)
    drum_circle(cv, reserved)
    paddock(cv, reserved)
    garden(cv, reserved)
    artificers_yard(cv, reserved)
    apiary(cv, reserved)
    old_grove(cv, reserved)
    homes(cv, reserved)
    bridge_end = windward_mill(cv, reserved)
    loom_cogwork(cv)
    reserved |= springs(cv)
    signpost(cv)
    dress_interiors(cv)
    street_dress(cv)
    # lanes: market street to the Hearth and the Chapel, south road to the Archive, the Lookout and the Drum Circle
    lane(cv, reserved, [(x, z) for x in range(-50, -47) for z in range(-28, -4)])     # the Hearth
    lane(cv, reserved, [(x, z) for x in range(29, 32) for z in range(-28, -4)])       # the Chapel
    lane(cv, reserved, [(x, z) for x in range(29, 50) for z in range(-29, -26)])
    lane(cv, reserved, [(x, z) for x in range(-43, -3) for z in (47, 48, 49)])          # the Archive
    lane(cv, reserved, [(x, z) for x in range(4, 63) for z in (50, 51, 52)])            # the Lookout
    lane(cv, reserved, [(x, z) for x in range(4, 32) for z in (33, 34, 35)])            # the Drum Circle
    lane(cv, reserved, [(x, z) for x in range(4, 20) for z in (73, 74, 75)])            # the apiary, past the booth
    lane(cv, reserved, [(x, z) for x in (-77, -76, -75) for z in range(5, 14)])         # the paddock
    lane(cv, reserved, [(x, z) for x in (-79, -78, -77) for z in range(-7, -4)])        # the garden
    plaza_dress(cv)
    reserved.update((x, z) for _, _, x, z in TOWNSFOLK)      # the townsfolk's and cats' morning spots stay clear
    reserved.update((x, z) for _, x, z in CATS)
    roadside(cv, reserved)
    # buildings' own footprints stay clear of grass tufts
    for (x, y, z), b in list(cv.c.items()):
        if y == Y + 1 and base_id(b) != 'air':
            reserved.add((x, z))
    # trees: cherry by the plaza, willow and hearthoak from the March, oaks and azaleas in the quadrants
    # (each spot has a clear 3x3 of open ground; one that lost it to a building would silently never grow)
    trees = [(-36, -69, 'oak'), (-18, -58, 'cherry'), (18, -58, 'cherry'), (39, -72, 'azalea'), (-90, -30, 'apple'),
             (-39, 21, 'cherry'), (33, 18, 'cherry'), (78, 42, 'azalea'), (48, 75, 'oak'), (-39, 72, 'azalea'),
             (-75, 57, 'cherry'), (84, -24, 'birch'), (-60, -66, 'dark'), (74, -42, 'hearthoak'), (-14, 62, 'willow'),
             (66, 60, 'willow'), (-86, 40, 'birch'), (-94, 12, 'pear'), (94, -12, 'apple'), (-30, -70, 'cherry'),
             (30, -62, 'birch'), (-60, 70, 'willow'), (56, 66, 'cherry'), (-88, -33, 'oak'), (88, 30, 'oak'),
             (12, 84, 'cherry'), (-21, 77, 'azalea'), (-61, 21, 'hearthoak'), (58, 20, 'birch')]
    for x, z, kind in trees:
        if all((x + dx, z + dz) in cv.surface and (x + dx, z + dz) not in reserved
               for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
            tree(cv, x, z, kind)
            reserved.add((x, z))
            if kind == 'cherry':      # bees keep a nest in the cherries
                cv.set(x + 1, Y + 3, z, 'bee_nest[facing=east,honey_level=3]')
    # the Lantern Walk, kept: nine tribe lanterns along the south lawn
    for i, t in enumerate(TRIBES):
        x = -36 + i * 9
        z = 82
        if abs(x) <= 4 or (x, z) not in cv.surface or not cv.air(x, Y + 1, z):
            continue
        cv.set(x, Y + 1, z, f'{DYE[t]}_concrete')
        cv.set(x, Y + 2, z, 'tribalpower:lantern_cap')
        reserved.add((x, z))
    # the rim, with rain chimes on a few of its posts
    openings = {(x, z) for (x, z) in cv.surface if abs(x) <= 3 and abs(z) > 30} | bridge_end
    rim_wall(cv, reserved, openings)
    for (x, z) in sorted(edge_cells(cv.surface)):
        if (x, z) not in openings and hash2(x, z, 71) < .03 and base_id(cv.get(x, Y + 2, z) or 'air') == 'air':
            cv.set(x, Y + 2, z, 'tribalpower:rain_chime')
    meadow(cv, reserved)
    islets(cv)
    # benches by the fountain
    for x in (-20, -10):
        cv.set(x, Y + 1, 21, 'spruce_stairs[facing=' + ('west' if x < -15 else 'east') + ']')
    # arrival must be clear
    for dy in (1, 2, 3):
        assert cv.air(0, Y + dy, 5), cv.get(0, Y + dy, 5)
    # townsfolk: each has a trade and a workstation here, a bed upstairs at the Hearth, and the bell to meet at
    for name, job, x, z in TOWNSFOLK:
        cv.resident(x, Y + 1, z, name, nbt=villager_nbt(job))
    # a family in every home: nitwits keep no trade, so they wander, visit and sleep in their own bed
    for (face, fx, fz, tribe), name in zip(HOMES, HOME_FOLK):
        x, _, z = Local(cv, face, fx, fz).world(3, 1, -3)
        cv.resident(x, Y + 1, z, name, nbt=villager_nbt('nitwit'))
    for name, x, z in CATS:
        cv.resident(x, Y + 1, z, name, 'minecraft:cat')
    # the tribes about their roles: Drumheart drummers on the Circle's stage, a Loom-stitcher at the chapel loom,
    # hunters in the grove and at the Cut, a Colony-keeper by the hives, a Pattern-weaver in the yard
    dx, dz = DRUM
    for name, tribe, role, x, y, z in (('Drumheart Tam', 4, 'DRUMMER', dx - 2, Y + 2, dz - 2),
                                       ('Drumheart Oda', 4, 'DRUMMER', dx + 2, Y + 2, dz - 2),
                                       ('Loom-stitcher Wynn', 8, 'WEAVER', 41, Y + 1, -36),
                                       ('Rootbinder Ash', 2, 'HUNTER', -60, Y + 1, -50),
                                       ('Edge-walker Kest', 3, 'HUNTER', 0, Y + 1, -60),
                                       ('Colony-keeper Bee', 6, 'WEAVER', 17, Y + 1, 62),
                                       ('Pattern-weaver Cog', 5, 'WEAVER', 72, Y + 1, -18)):
        cv.resident(x, y, z, name, 'tribalpower:tribal_kin', nbt='{Tribe:%d,Role:"%s"}' % (tribe, role))
    # the paddock: sheep in the nine tribe colours, cows, pigs, a horse, a donkey, and the spirit herd
    x0, x1, z0, z1 = PADDOCK
    pcx, pcz = (x0 + x1) // 2, (z0 + z1) // 2
    for i, colour in enumerate((12, 8, 13, 14, 1, 11, 4, 10, 9)):
        x, z = near(pcx, pcz, i, 6, 11)
        cv.resident(x, Y + 1, z, f'Fleece {i + 1}', 'minecraft:sheep', nbt='{Color:%db}' % colour, show_name=False)
    for i, kind in enumerate(('cow', 'cow', 'cow', 'pig', 'pig', 'horse', 'donkey', 'llama')):
        x, z = near(pcx, pcz, i, 6, 12)
        cv.resident(x, Y + 1, z, f'Stock {i + 1}', 'minecraft:' + kind, show_name=False)
    for i, name in enumerate(('Fred', 'Fluffy', 'Spot', 'Biscuit', 'Noodle')):   # whatever line the herd rolls
        x, z = near(pcx, pcz, i, 5, 13)
        cv.resident(x, Y + 1, z, name, 'shamanicmounts:mount', tags=['ncs_hub_herd'])
    # the garden and the lanes: hens, rabbits; parrots about the eaves; fish and an axolotl in the fountain
    gx0, gx1, gz0, gz1 = GARDEN
    for i in range(6):
        x, z = near((gx0 + gx1) // 2, gz1 + 3, i, 5, 14)
        cv.resident(x, Y + 1, z, f'Hen {i + 1}', 'minecraft:chicken', show_name=False)
    for i, (x, z) in enumerate(((-30, 80), (60, 30), (-12, -66), (78, 52), (-88, 20), (20, -60))):
        cv.resident(x, Y + 1, z, f'Hopper {i + 1}', 'minecraft:rabbit', show_name=False)
    for i, (x, z, v) in enumerate(((-44, -26, 0), (-66, -10, 2), (33, 20, 3), (60, -20, 1), (-40, 44, 4))):
        cv.resident(x, Y + 2, z, f'Pip-squeak {i + 1}', 'minecraft:parrot', nbt='{Variant:%d}' % v, show_name=False)
    fx, fz = FOUNTAIN
    for i, (x, z) in enumerate(((fx - 1, fz), (fx + 1, fz + 1), (fx, fz - 1))):
        cv.resident(x, Y, z, f'Minnow {i + 1}', 'minecraft:tropical_fish', nbt='{FromBucket:1b}', show_name=False)
    cv.resident(fx + 1, Y, fz - 1, 'Pip', 'minecraft:axolotl', nbt='{FromBucket:1b,Variant:0}', show_name=False)
    for i, (x, z) in enumerate(((24, 66), (28, 70), (30, 74), (22, 72), (-36, 22), (34, 20))):
        cv.resident(x, Y + 3, z, f'Bee {i + 1}', 'minecraft:bee', show_name=False)
    # town chocobos about Esther's Roost and the south road: yellow and green, TownBird so nobody tames them
    for name, plumage, x, z in (('Pollen', 0, -8, 82), ('Nutmeg', 0, -18, 64), ('Sprig', 1, 8, 58),
                                ('Barley', 0, 12, 40)):
        cv.resident(x, Y + 1, z, name, 'chocobosreborn:chocobo', tags=['ncs_hub_chocobo'],
                    nbt='{Plumage:%d,TownBird:1b}' % plumage)
    # Sunfeather, the Hall's golden chocobo: belongs to no one, wanders the town
    cv.resident(12, Y + 1, 24, 'Sunfeather', 'chocobosreborn:chocobo', tags=['ncs_hub_sunfeather'],
                nbt='{Plumage:5,TownBird:1b,Grade:3}')
    # walkers start on open ground: one whose spot a prop, a fence or a crop took moves to the nearest clear cell
    for r in cv.residents:
        if r['pos'][1] == Y + 1:
            x, z = ground_spot(cv, math.floor(r['pos'][0]), math.floor(r['pos'][2]))
            r['pos'] = [x + .5, Y + 1, z + .5]
    cv.connect()
    return cv


def write_posts(script, posts):
    """Write the keepers' posts, tribes and names into dock_stalls.js between its HUB_POSTS markers."""
    raw = script.read_bytes().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    text = raw.replace('\r\n', '\n')
    head, rest = text.split('const HUB_POSTS = ', 1)
    rest = rest[rest.index('\n// HUB_POSTS:END'):]
    rows = ',\n'.join(f"  {k}: [{', '.join(str(v) for v in pos)}, {STALL_TRIBE[k]}, '{STALL_NAMES[k]}']"
                      for k, pos in posts.items())
    script.write_bytes((head + 'const HUB_POSTS = {\n' + rows + ',\n}' + rest).replace('\n', nl).encode('utf-8'))


def pad_cells_v1():
    """Blocks the old Java ceremony builder placed, so the upgrade can clear what the new plan does not reuse."""
    cells = set()
    for x in range(-7, 8):
        for z in range(-7, 8):
            cells |= {(x, 62, z), (x, 63, z)}
    for x in (-7, 7):
        for z in (-7, 7):
            cells |= {(x, 64, z), (x, 65, z), (x, 66, z)}
    cells |= {(-1, 64, -2), (1, 64, -2), (-1, 64, -1), (1, 64, -1)}
    for x, z in ((-5, 0), (5, 0), (-4, 4), (4, 4)):
        cells |= {(x, 64, z), (x, 65, z)}
    cells |= {(-2, 64, 1), (2, 64, 1), (0, 64, -6)}
    return cells


def plan(v1_town):
    """The v2 plan: stale v1 cells turned to air first, then the new town, then signs, frames and residents."""
    cv = loomsend()
    old = set()
    for box in v1_town['boxes']:
        a, b = box['from'], box['to']
        for x in range(a[0], b[0] + 1):
            for y in range(a[1], b[1] + 1):
                for z in range(a[2], b[2] + 1):
                    if abs(x) <= 7 and abs(z) <= 7 and y >= 62:
                        continue          # v1 never wrote inside the ceremony square
                    old.add((x, y, z))
    old |= pad_cells_v1()
    stale = {p: 'minecraft:air' for p in old if p not in cv.c and p not in cv.keep}
    boxes = cv.boxes(stale) + cv.boxes(cv.c)
    for b in boxes:
        f, t = b['from'], b['to']
        assert -160 <= f[0] and t[0] <= 160 and -160 <= f[2] and t[2] <= 160 and f[1] >= 0 and t[1] <= 128, b
    return cv, dict(name="Loom's End", revision=2, boxes=boxes, keep=sorted(list(p) for p in cv.keep),
                    signs=cv.signs, frames=cv.frames, residents=cv.residents, posts=cv.posts)
