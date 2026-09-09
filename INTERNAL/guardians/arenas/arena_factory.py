"""Snapped Guardian arenas — one unique stage per boss, built block-by-block (Minecraft scale: 1 unit = 1 block),
rendered with the boss standing in it and player silhouettes for scale. Concept art for the arena builders;
ARENAS.md carries the block specs and mechanics.
usage: NCS_ART_ROOT=<work dir> blender --background --python arena_factory.py -- <boss|all> [samples]
Floor top of every arena is z=0 where the boss stands.
"""
import bpy, math, sys, random, os
ART = os.environ.get('NCS_ART_ROOT', os.path.expanduser('~'))
sys.path.insert(0, ART); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boss_lib2 as L, boss_factory as BF
from voxel import Voxels
from mathutils import Vector

OUT = os.path.join(ART, 'renders', 'arenas'); os.makedirs(OUT, exist_ok=True)
TEAL = (0.12, 0.95, 0.82); GOLD = (1.0, 0.72, 0.18)
rad = math.radians

# ---------------------------------------------------------------- materials (block palette)
def blk(name, rgb, dark=None, rough=0.95, scale=3.0, bump=0.35, sheen=0.0):
    dark = dark or tuple(c*0.5 for c in rgb)
    m = L.surface(name, base=rgb, dark=dark, crack_str=0, rough=rough, bump=bump, noise_scale=scale, sheen=sheen)
    p = [n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]; p.inputs["Specular IOR Level"].default_value = 0.12
    return m
def glow(name, rgb, s=2.0): return L.glow(name, rgb, s)

PAL = dict(
    dirt=((0.40, 0.27, 0.15), 0.95), rooted=((0.36, 0.25, 0.15), 0.95), mud=((0.25, 0.21, 0.19), 0.95), moss=((0.32, 0.50, 0.22), 0.95), grass=((0.33, 0.56, 0.22), 0.95),
    stone=((0.52, 0.52, 0.52), 0.95), cobble=((0.45, 0.45, 0.45), 0.95), deepslate=((0.27, 0.27, 0.30), 0.95), blackstone=((0.13, 0.12, 0.14), 0.9), tuff=((0.42, 0.44, 0.40), 0.95),
    gravel=((0.56, 0.53, 0.51), 0.95), basalt=((0.22, 0.22, 0.24), 0.9), obsidian=((0.17, 0.11, 0.24), 0.3), endstone=((0.86, 0.86, 0.62), 0.95), purpur=((0.55, 0.40, 0.70), 0.9),
    oak=((0.62, 0.46, 0.26), 0.9), darkoak=((0.30, 0.20, 0.10), 0.9), spruce=((0.45, 0.32, 0.18), 0.9), planks=((0.66, 0.50, 0.28), 0.9), log=((0.36, 0.25, 0.13), 0.9),
    copper=((0.74, 0.46, 0.30), 0.55), oxcopper=((0.30, 0.60, 0.52), 0.6), brass=((0.78, 0.58, 0.24), 0.45), iron=((0.62, 0.62, 0.64), 0.5), gold=((0.92, 0.72, 0.22), 0.4),
    wax=((0.86, 0.66, 0.30), 0.75), comb=((0.66, 0.45, 0.16), 0.75), darkwax=((0.38, 0.25, 0.08), 0.8), hedge=((0.17, 0.38, 0.14), 0.95), leaves=((0.22, 0.46, 0.18), 0.95),
    wool=((0.78, 0.76, 0.80), 1.0), rope=((0.58, 0.44, 0.26), 0.95), amethyst=((0.55, 0.40, 0.80), 0.5), prismarine=((0.35, 0.65, 0.60), 0.7), sand=((0.85, 0.80, 0.60), 0.95),
    glass=((0.7, 0.9, 0.9), 0.1), snow=((0.95, 0.95, 0.97), 0.9), redwool=((0.65, 0.22, 0.22), 1.0),
)
GLOWS = dict(lava=((1.0, 0.40, 0.05), 3.2), honey=((1.0, 0.62, 0.10), 2.2), teal=(TEAL, 1.6), gold=(GOLD, 1.6), seam=(GOLD, 3.0), void=(TEAL, 1.0),
             amber=((1.0, 0.72, 0.28), 1.4), violet=((0.6, 0.35, 0.95), 1.4), white=((0.9, 0.95, 1.0), 1.2), ember=((1.0, 0.55, 0.15), 2.0), soul=((0.3, 0.9, 0.9), 1.6))

CUR = None
def Vx():
    """new voxel canvas; also the export target for curves/threads and the pad/totem/gate metadata"""
    global CUR; CUR = Voxels(); CUR.meta = dict(pads=[], totem=None, gate=None); return CUR

# curve/thread materials that should become blocks in the exported arena data
MATKEY = {'rootwood': 'log', 'vine': 'leaves', 'totemthread': None, 'gateglow': None, 'warp': 'teal', 'sagthread': 'teal', 'skyseam': 'gold', 'pipe': 'copper'}

def palette(V, *keys):
    keys = tuple(dict.fromkeys(keys + ('deepslate', 'blackstone', 'gold', 'teal', 'log', 'leaves', 'copper')))   # totem/gate/spawn pads always need these
    for k in keys:
        if k in PAL: rgb, rough = PAL[k]; V.mat(k, blk(k, rgb, rough=rough, sheen=0.3 if k in ('wool', 'hedge', 'leaves') else 0.0))
        else: rgb, s = GLOWS[k]; V.mat(k, glow(k, rgb, s))

# ---------------------------------------------------------------- props (non-voxel)
def cube(center, size, mat, rot=(0, 0, 0)):
    o = L.cube(center, (size[0]*2, size[1]*2, size[2]*2), rot=rot); o.data.materials.append(mat); return o
def curve(pts, radius, mat, kind='NURBS'):
    if CUR is not None:                                                   # voxelize for the exported block plan
        key = MATKEY.get(mat.name.split('.')[0], None)
        if key is None:
            for k in ('cathedral', 'strandcol'):
                if mat.name.startswith(k): key = 'gold' if 'gold' in mat.name.lower() else 'teal'
        if key and key in CUR.mats:
            P = [Vector(p) for p in pts]
            if kind == 'NURBS' and len(P) >= 3:                           # sample the smooth curve as a quadratic bezier-ish through the points
                Q = []
                for i in range(40):
                    t = i/39; a = P[0]*(1-t)**2 + P[1]*2*t*(1-t) + P[2]*t*t if len(P) == 3 else P[min(len(P)-1, int(t*(len(P)-1)))]
                    Q.append(a)
                P = Q
            for a, b in zip(P, P[1:]):
                n = int((b-a).length)+1
                for i in range(n+1):
                    q = a + (b-a)*(i/n); CUR.set(q.x, q.y, q.z, key)
    cu = bpy.data.curves.new('c', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = radius; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new(kind); sp.points.add(len(pts)-1)
    for i, p in enumerate(pts): sp.points[i].co = (*p, 1)
    sp.use_endpoint_u = True; o = bpy.data.objects.new('c', cu); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o
def thread(a, b, mat, r=0.08): return curve([a, b], r, mat, 'POLY')

def players(V, spots, z=0):
    for (x, y) in spots:
        V.disc(x, y, 1.5, z-1, z, 'teal'); BF.player_figure((x+0.5, y+0.5, z)); V.meta['pads'].append((x, y, z))

def totem(V, x, y, z=0):
    V.meta['totem'] = (x, y, z)
    V.column(x, y, z, z+1, 'deepslate'); V.set(x, y, z+1, 'gold')
    thread((x+0.5, y+0.5, z+2), (x+0.5, y+0.5, z+7), glow("totemthread", TEAL, 2.0), 0.06)

def gate(V, x, y, z=0, axis='x', h=5, w=4):
    """the return gate: two pillars + lintel, a teal sheet between"""
    V.meta['gate'] = (x, y, z, axis, h, w)
    for s in (-w//2, w//2):
        if axis == 'x': V.column(x+s, y, z, z+h, 'blackstone')
        else: V.column(x, y+s, z, z+h, 'blackstone')
    for s in range(-w//2, w//2+1):
        V.set(x+s if axis == 'x' else x, y if axis == 'x' else y+s, z+h, 'blackstone')
    sheet = cube((x+0.5, y+0.5, z+h/2+0.5), ((w-1)/2, 0.06, (h-1)/2) if axis == 'x' else (0.06, (w-1)/2, (h-1)/2), glow("gateglow", TEAL, 1.4))

def stars(n=300, seed=9):
    rnd = random.Random(seed); m = glow("star", (0.85, 0.9, 1.0), 6.0)
    for i in range(n):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(200, 300); z = rnd.uniform(-40, 180)
        bpy.ops.mesh.primitive_ico_sphere_add(radius=rnd.uniform(0.15, 0.45), location=(d*math.cos(a), d*math.sin(a), z), subdivisions=1); bpy.context.object.data.materials.append(m)

def void_ground(colour=(0.015, 0.018, 0.035)):
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o.dimensions.x > 150: bpy.data.objects.remove(o)
    w = bpy.data.worlds['World']; w.node_tree.nodes["Background"].inputs[0].default_value = (*colour, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.7

def accent(loc, rgb, energy=3000, size=6):
    bpy.ops.object.light_add(type='POINT', location=loc); l = bpy.context.object; l.data.energy = energy; l.data.color = rgb; l.data.shadow_soft_size = size; return l

def rocks(V, key, n, rmin, rmax, seed, z=0, smin=1, smax=3):
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(rmin, rmax); s = rnd.randint(smin, smax)
        x, y = int(r*math.cos(a)), int(r*math.sin(a))
        V.box(x, y, z, x+s, y+s, z+rnd.randint(1, s), key)

# ---------------------------------------------------------------- the 13 arenas
def beddown():
    """THE BURROW BOWL — a sunken earthen bowl; the boss buries the pit in soil layers you dig channels through."""
    V = Vx(); palette(V, 'dirt', 'rooted', 'mud', 'moss', 'grass', 'log', 'teal', 'gold'); rnd = random.Random(3)
    V.disc(0, 0, 11, -2, 0, 'mud', jitter=1.0, rnd=rnd)                                     # pit floor
    for (ri, ro, z, key) in ((10, 16, 2, 'rooted'), (15, 22, 4, 'dirt'), (21, 27, 6, 'moss'), (26, 31, 8, 'grass')):
        V.disc(0, 0, ro, -2, z-1, 'dirt', rin=ri, jitter=1.2, rnd=rnd); V.disc(0, 0, ro, z-1, z, key, rin=ri, jitter=1.2, rnd=random.Random(rnd.random()))   # four stepped tiers
    V.disc(0, 0, 32, -6, -2, 'dirt', jitter=1.5, rnd=rnd); V.disc(0, 0, 24, -9, -6, 'rooted', jitter=2)  # island underside
    # teal root-seams glowing in the pit floor and up the first tier
    for k in range(7):
        a = 2*math.pi*k/7; V.line(2*math.cos(a), 2*math.sin(a), 15*math.cos(a), 15*math.sin(a), -1, 0, 'teal')
    # root arches from tier 3 over the pit, and soil slabs stacked on the rim (the burial layers)
    root = blk("rootwood", (0.32, 0.21, 0.10), scale=1.5)
    for k in range(6):
        a = 2*math.pi*k/6 + 0.3; p1 = (23*math.cos(a-0.28), 23*math.sin(a-0.28)); p2 = (23*math.cos(a+0.28), 23*math.sin(a+0.28))
        curve([(p1[0], p1[1], 5), ((p1[0]+p2[0])/2*0.8, (p1[1]+p2[1])/2*0.8, 16), (p2[0], p2[1], 5)], 0.9, root)
        curve([(p1[0]*1.1, p1[1]*1.1, 6), (p1[0]*0.6, p1[1]*0.6, 1), (p1[0]*0.3, p1[1]*0.3, -1)], 0.45, root)     # roots crawling down into the pit
        x, y = int(28*math.cos(a)), int(28*math.sin(a)); V.box(x-2, y-2, 8, x+2, y+2, 11, 'dirt'); V.box(x-1, y-1, 11, x+1, y+1, 12, 'mud')
    rocks(V, 'mud', 18, 3, 10, 5, z=0); rocks(V, 'moss', 14, 22, 30, 6, z=8)
    for k in range(10):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(24, 30); V.column(int(r*math.cos(a)), int(r*math.sin(a)), 8, 9+rnd.randint(1, 3), 'log')  # dead stumps on the rim
    players(V, [(18, 4), (-16, 9), (-6, -17), (14, -12)], z=4); totem(V, 0, -21, 4); gate(V, 0, 32, 8, 'x')
    V.build(); accent((0, 0, 6), TEAL, 2500, 8)
    return dict(cam=(50, -62, 24), target=(0, 0, 3), lens=36)

def grindmaw():
    """THE MILLPIT — a stone quarry: a rotating grindstone ring in the floor, four sieve chutes pouring grit into the pit."""
    V = Vx(); palette(V, 'stone', 'cobble', 'deepslate', 'gravel', 'brass', 'iron', 'teal', 'gold', 'tuff'); rnd = random.Random(5)
    V.disc(0, 0, 32, -4, 0, 'deepslate', jitter=1.0, rnd=rnd); V.disc(0, 0, 26, -8, -4, 'stone', jitter=2, rnd=rnd)
    V.disc(0, 0, 32, 0, 5, 'stone', rin=29, jitter=0.8, rnd=rnd); V.disc(0, 0, 33, 5, 7, 'cobble', rin=28)      # quarry wall + rim
    V.disc(0, 0, 21, 0, 1, 'stone', rin=14)                                                                       # the grindstone ring (rotates)
    for k in range(16):
        a = 2*math.pi*k/16; V.line(14.5*math.cos(a), 14.5*math.sin(a), 20.5*math.cos(a), 20.5*math.sin(a), 1, 2, 'brass')   # tooth ridges
    V.disc(0, 0, 9, -1, 0, 'gravel', jitter=1.5, rnd=rnd)                                                        # grit pit floor (the boss's grit)
    for k in range(4):                                                                                            # four sieve chutes
        a = math.pi/2*k; x, y = int(27*math.cos(a)), int(27*math.sin(a))
        V.box(x-3, y-3, 5, x+3, y+3, 12, 'stone'); V.box(x-2, y-2, 12, x+2, y+2, 13, 'brass'); V.box(x-1, y-1, 7, x+1, y+1, 12, 'gravel')
        for i in range(8):                                                                                       # sloping chute + spilled grit
            t = i/8; cx, cy = int(x*(1-t*0.75)), int(y*(1-t*0.75)); V.box(cx-1, cy-1, int(7-t*7), cx+2, cy+2, int(8-t*7), 'iron')
        V.disc(x*0.28, y*0.28, 3.5, 0, 1, 'gravel'); V.disc(x*0.28, y*0.28, 2, 1, 2, 'gravel')
    for k in range(8):
        a = 2*math.pi*k/8 + 0.2; x, y = int(30*math.cos(a)), int(30*math.sin(a)); V.column(x, y, 7, 10, 'iron'); V.set(x, y, 10, 'gold')  # lantern posts
    rocks(V, 'cobble', 24, 22, 29, 8, z=0); rocks(V, 'gravel', 20, 9, 14, 9, z=0, smax=2)
    players(V, [(24, 5), (-22, 8), (-8, -23), (16, -18)]); totem(V, -24, -20); gate(V, 0, 34, 7, 'x')
    V.build(); accent((0, 0, 5), TEAL, 2000, 6); accent((-25, -20, 6), GOLD, 800, 3)
    return dict(cam=(52, -64, 42), target=(0, 0, 3), lens=36)

def thornmother():
    """THE OVERGROWTH TERRACE — stepped garden terraces; growth spreads each phase, four composter stations must be kept clear."""
    V = Vx(); palette(V, 'grass', 'dirt', 'hedge', 'leaves', 'log', 'planks', 'cobble', 'moss', 'teal', 'gold'); rnd = random.Random(7)
    for i, (r, z) in enumerate(((36, 0), (28, 3), (20, 6), (12, 9))):
        V.disc(0, 0, r, z-3, z, 'dirt', jitter=1.0, rnd=rnd); V.disc(0, 0, r, z-1, z, 'grass' if i % 2 == 0 else 'moss', jitter=1.0, rnd=rnd)
        if i: V.disc(0, 0, r+1, z-3, z, 'cobble', rin=r, jitter=0)                                               # retaining walls
    V.disc(0, 0, 30, -8, -3, 'dirt', jitter=2, rnd=rnd)
    # hedges creeping down the steps (the spread), taller near the boss
    for i in range(140):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(8, 34); x, y = int(r*math.cos(a)), int(r*math.sin(a))
        z = 9 if r < 12 else 6 if r < 20 else 3 if r < 28 else 0; s = rnd.randint(1, 3); h = rnd.randint(1, 4 if r < 20 else 2)
        V.box(x, y, z, x+s, y+s, z+h, 'hedge' if rnd.random() < 0.75 else 'leaves')
    for k in range(4):                                                                                            # the four pruning stations
        a = math.pi/2*k + math.pi/4; x, y = int(24*math.cos(a)), int(24*math.sin(a))
        V.box(x-2, y-2, 3, x+3, y+3, 4, 'planks'); V.box(x, y, 4, x+1, y+1, 5, 'log'); V.set(x, y, 5, 'teal')
        V.disc(x, y, 4, 3, 4, 'grass')                                                                            # kept clear
    for k in range(8):                                                                                            # trellis posts + vine canopy
        a = 2*math.pi*k/8; x, y = int(32*math.cos(a)), int(32*math.sin(a)); V.column(x, y, 0, 15, 'log'); V.column(x+1, y, 0, 15, 'log')
        b = 2*math.pi*(k+1)/8; V.line(32*math.cos(a), 32*math.sin(a), 32*math.cos(b), 32*math.sin(b), 15, 16, 'log')
        for j in range(5):
            if math.sin((a+b)/2) > -0.2: V.line(32*math.cos(a)*(0.3+j*0.15), 32*math.sin(a)*(0.3+j*0.15), 32*math.cos(b)*(0.3+j*0.15), 32*math.sin(b)*(0.3+j*0.15), 15, 16, 'leaves')   # canopy open on the camera side
    vine = blk("vine", (0.2, 0.42, 0.16), scale=1.5)
    for k in range(20):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(10, 30); curve([(r*math.cos(a), r*math.sin(a), 15), (r*math.cos(a)+rnd.uniform(-2, 2), r*math.sin(a)+rnd.uniform(-2, 2), rnd.uniform(6, 12))], 0.2, vine, 'POLY')
    players(V, [(30, 4), (-28, 8), (-10, -29), (24, -18)]); totem(V, 0, -33); gate(V, 0, 38, 0, 'x')
    V.build(); accent((0, 0, 12), (0.5, 1.0, 0.6), 2000, 8)
    return dict(cam=(54, -68, 28), target=(0, 0, 5), lens=36)

def edgewalker():
    """THE SKY SHARDS — deepslate shards floating over the void, no rails, crumbling bridges; a vertical duel."""
    V = Vx(); palette(V, 'deepslate', 'blackstone', 'tuff', 'cobble', 'teal', 'gold'); rnd = random.Random(11)
    plats = [((0, 0), 0, 19), ((27, 7), 6, 8), ((-25, 11), 9, 7), ((9, -29), 4, 8), ((-15, -23), 12, 6), ((31, -17), 14, 5), ((-31, -6), 3, 6), ((3, 31), 11, 7), ((-9, 37), 18, 5), ((25, 29), 16, 5)]
    for (x, y), z, r in plats:
        V.disc(x, y, r, z-2, z, 'deepslate', jitter=1.5, rnd=rnd); V.disc(x, y, r-2, z-5, z-2, 'blackstone', jitter=1.5, rnd=rnd)
        V.disc(x, y, r-4, z-9, z-5, 'blackstone', jitter=1.0, rnd=rnd); V.disc(x, y, max(1, r-7), z-13, z-9, 'blackstone')   # rock keel
        rocks(V, 'tuff', 4, 0, r-2, int(x*7+y), z=z, smax=2)
        for i in range(-r, r):
            for j in range(-r, r):
                if V.get(x+i, y+j, z-1) == 'deepslate' and rnd.random() < 0.12: V.set(x+i, y+j, z-1, 'cobble')
    links = [(0, 1), (0, 3), (0, 6), (1, 5), (3, 4), (6, 4), (0, 7), (7, 8), (7, 9), (1, 9)]
    for i, (a, b) in enumerate(links):
        (ax, ay), az, _ = plats[a]; (bx, by), bz, _ = plats[b]; n = int(math.hypot(bx-ax, by-ay))
        for s in range(n):
            t = s/n
            if i % 3 == 2 and 0.35 < t < 0.7: continue                                                   # broken span
            if rnd.random() < 0.08: continue                                                             # missing planks
            z = az + (bz-az)*t; V.box(int(ax+(bx-ax)*t)-1, int(ay+(by-ay)*t)-1, int(z)-1, int(ax+(bx-ax)*t)+2, int(ay+(by-ay)*t)+2, int(z), 'deepslate')
    for k in range(4):                                                                                    # gold claw-marks on the main shard
        V.line(rnd.uniform(-8, 8), rnd.uniform(-8, 8), rnd.uniform(-8, 8), rnd.uniform(-8, 8), -1, 0, 'gold')
    players(V, [(9, 2), (-8, 6), (-2, -9), (6, -7)]); totem(V, -31, -6, 3); gate(V, -9, 37, 18, 'x')
    V.build(); accent((0, 0, 8), GOLD, 2500, 8); accent((-9, 37, 22), TEAL, 900, 4)
    return dict(cam=(58, -76, 30), target=(0, 2, 6), lens=34)

def drumheart():
    """THE FORGE DRUM — a brass platform over lava; eight piston hammers pulse on the beat and the lava channels rise with it."""
    V = Vx(); palette(V, 'brass', 'copper', 'oxcopper', 'iron', 'basalt', 'blackstone', 'lava', 'amber', 'teal', 'gold'); rnd = random.Random(13)
    V.disc(0, 0, 38, -5, -3, 'lava'); V.disc(0, 0, 40, -10, -5, 'basalt', jitter=2, rnd=rnd)                    # the lava pool in its crater
    V.disc(0, 0, 40, -5, 1, 'basalt', rin=37, jitter=1.0, rnd=rnd); V.disc(0, 0, 41, 1, 2, 'blackstone', rin=36)
    V.disc(0, 0, 23, -2, 0, 'brass'); V.disc(0, 0, 23, 0, 1, 'copper', rin=22)                                   # the drum platform + rim
    for k in range(12):
        a = 2*math.pi*k/12; x, y = int(21*math.cos(a)), int(21*math.sin(a)); V.box(x, y, -5, x+2, y+2, -2, 'iron')   # struts down to the pool
    for k in range(4):                                                                                              # lava channels (rise on the beat)
        a = math.pi/2*k + math.pi/4; V.line(4*math.cos(a), 4*math.sin(a), 19*math.cos(a), 19*math.sin(a), -1, 0, 'lava', width=2)
    for k in range(8):                                                                                              # eight piston hammers + beat pads
        a = 2*math.pi*k/8; x, y = int(17*math.cos(a)), int(17*math.sin(a))
        V.box(x-1, y-1, 0, x+2, y+2, 5, 'copper'); V.box(x-1, y-1, 5, x+2, y+2, 6, 'iron'); V.box(x, y, 6, x+1, y+1, 8, 'iron')
        V.disc(x*0.72, y*0.72, 2, -1, 0, 'amber')
    V.disc(0, 0, 28, -2, 0, 'iron', rin=24); V.disc(0, 0, 28, 0, 1, 'oxcopper', rin=27)                         # outer catwalk + rail
    for k in range(24):
        a = 2*math.pi*k/24; V.column(int(27*math.cos(a)), int(27*math.sin(a)), 1, 3, 'copper')
    for k in range(6):
        a = 2*math.pi*k/6 + 0.3; x, y = int(38*math.cos(a)), int(38*math.sin(a)); V.box(x-2, y-2, 2, x+2, y+2, 8, 'basalt'); V.set(x, y, 8, 'amber')  # crater chimneys
    for i in range(10):                                                                                             # bellows pipes from the wall to the drum
        a = 2*math.pi*i/10; curve([(37*math.cos(a), 37*math.sin(a), 1), (30*math.cos(a), 30*math.sin(a), 5), (24*math.cos(a), 24*math.sin(a), 1)], 0.5, blk("pipe", (0.7, 0.45, 0.3), rough=0.5))
    players(V, [(25, 4), (-24, 6), (-6, -25), (20, -16)]); totem(V, 0, -26); gate(V, 0, 41, 2, 'x')
    V.build(); accent((0, 0, -5), (1.0, 0.45, 0.1), 9000, 12); accent((0, 0, 6), (1.0, 0.7, 0.3), 1500, 6)
    return dict(cam=(54, -66, 40), target=(0, 0, 3), lens=36)

def cogwright():
    """THE ESCAPEMENT — a clockwork floor of concentric rotating rings; tiles light in the sequence you must remember."""
    V = Vx(); palette(V, 'brass', 'iron', 'copper', 'darkoak', 'blackstone', 'gold', 'teal', 'white'); rnd = random.Random(17)
    V.disc(0, 0, 35, -4, -1, 'blackstone', jitter=1.0, rnd=rnd)
    for i, (ri, ro) in enumerate(((4, 10), (11, 17), (18, 24), (25, 31))):                                       # four rotating rings
        V.disc(0, 0, ro, -1, 0, 'brass' if i % 2 else 'copper', rin=ri)
        V.disc(0, 0, ro, 0, 1, 'iron', rin=ro-1)                                                                 # lip between rings
        n = 8 + 4*i
        for k in range(n):
            a = 2*math.pi*k/n + i*0.2; x, y = int((ri+ro)/2*math.cos(a)), int((ri+ro)/2*math.sin(a))
            V.box(x-1, y-1, -1, x+1, y+1, 0, 'teal' if (k+i) % 5 == 0 else 'darkoak')                            # sequence tiles
    V.disc(0, 0, 4, -1, 1, 'iron')                                                                                  # centre hub
    for k in range(6):                                                                                              # gear towers on the rim
        a = 2*math.pi*k/6; x, y = int(33*math.cos(a)), int(33*math.sin(a))
        V.box(x-2, y-2, 0, x+2, y+2, 12, 'iron'); V.box(x-3, y-3, 12, x+3, y+3, 13, 'brass')
        g = L.ring((x+0.5, y+0.5, 15.5), 3.2, 0.7, V.mats['brass'], rot=(math.pi/2, 0, a))
        for j in range(10):
            b = 2*math.pi*j/10; cube((x+0.5+3.7*math.cos(b)*math.cos(a), y+0.5+3.7*math.cos(b)*math.sin(a), 15.5+3.7*math.sin(b)), (0.4, 0.4, 0.4), V.mats['brass'], rot=(0, 0, a))
    V.column(0, 38, 0, 16, 'iron'); V.box(-2, 36, 16, 3, 41, 18, 'brass'); L.sphere((0.5, 38.5, 2.5), 2.2, 16).data.materials.append(V.mats['brass'])  # the pendulum
    V.disc(0, 39, 5, -4, 0, 'blackstone')
    for k in range(12):
        a = 2*math.pi*k/12 + 0.26; V.column(int(31*math.cos(a)), int(31*math.sin(a)), 1, 4, 'copper'); V.set(int(31*math.cos(a)), int(31*math.sin(a)), 4, 'white')   # lamp posts
    players(V, [(27, 4), (-26, 7), (-8, -27), (20, -18)]); totem(V, -30, 0); gate(V, 0, 36, 0, 'x')
    V.build(); accent((0, 0, 8), TEAL, 2500, 8); accent((0, 38, 8), GOLD, 800, 4)
    return dict(cam=(56, -68, 30), target=(0, 0, 3), lens=36)

def hivemind():
    """THE COMB — a honeycomb arena; cells rise and fall, honey pools slow you, six drone cells open in the wall."""
    V = Vx(); palette(V, 'wax', 'comb', 'darkwax', 'honey', 'amber', 'teal', 'gold', 'oak'); rnd = random.Random(19)
    V.disc(0, 0, 34, -4, -1, 'darkwax', jitter=1.0, rnd=rnd)
    V.hexagon(0, 0, 36, -1, 4, 'darkwax')                                                                          # hexagonal outer wall...
    for x in range(-40, 41):
        for y in range(-40, 41):
            if abs(x+0.5) <= 33*0.866 and abs(y+0.5) <= 33 and abs(y+0.5)+abs(x+0.5)/math.sqrt(3) <= 33:
                for z in range(-1, 4): V.clear(x, y, z)                                                             # ...hollowed inside
    dx = 5.2; dy = dx*math.sqrt(3)/2
    for row in range(-8, 9):
        for col in range(-8, 9):
            x = col*dx + (dx/2 if row % 2 else 0); y = row*dy
            if math.hypot(x, y) > 31: continue
            h = rnd.choice((0, 0, 0, 1, 2, 3)); d = math.hypot(x, y)
            key = 'honey' if (rnd.random() < 0.18 and d > 9) else ('comb' if rnd.random() < 0.5 else 'wax')
            V.hexagon(x, y, 2.6, -1, h, key if key != 'honey' else 'wax');
            if key == 'honey': V.hexagon(x, y, 2.0, -1, max(h, 0)+1, 'honey')                                     # honey pool cell
            elif rnd.random() < 0.5: V.hexagon(x, y, 2.9, h-1, h, 'darkwax'); V.hexagon(x, y, 2.2, h-1, h, key)   # cell rims
    for k in range(6):                                                                                              # six drone cells in the wall
        a = 2*math.pi*k/6 + math.pi/6; x, y = 33*math.cos(a), 33*math.sin(a)
        V.hexagon(x, y, 3.5, 0, 6, 'comb'); V.hexagon(x, y, 2.3, 1, 5, 'amber')
    for k in range(9):                                                                                              # honey drips from roof struts
        a = 2*math.pi*k/9 + 0.1; x, y = int(22*math.cos(a)), int(22*math.sin(a)); V.column(x, y, 8, 12, 'oak'); V.column(x, y, 12-rnd.randint(1, 4), 12, 'honey')
        b = 2*math.pi*(k+1)/9 + 0.1; V.line(22*math.cos(a), 22*math.sin(a), 22*math.cos(b), 22*math.sin(b), 12, 13, 'oak')
    players(V, [(24, 4), (-22, 8), (-8, -23), (18, -16)]); totem(V, 0, -27); gate(V, 0, 36, 0, 'x')
    V.build(); accent((0, 0, 8), (1.0, 0.75, 0.3), 3000, 10)
    return dict(cam=(54, -66, 44), target=(0, 0, 3), lens=36)

def sealbreaker():
    """THE WARD CIRCLE — a stone sanctum; nine glyph pillars must be dispelled in the right order, wrong ones punish."""
    V = Vx(); palette(V, 'stone', 'deepslate', 'blackstone', 'gold', 'amethyst', 'teal', 'violet', 'soul', 'purpur'); rnd = random.Random(23)
    V.disc(0, 0, 33, -3, 0, 'stone'); V.disc(0, 0, 28, -7, -3, 'deepslate', jitter=2, rnd=rnd)
    for r in (8, 16, 24): V.disc(0, 0, r+0.6, -1, 0, 'gold', rin=r-0.6)                                          # inlaid circles
    for k in range(9):
        a = 2*math.pi*k/9 + math.pi/2; V.line(8*math.cos(a), 8*math.sin(a), 24*math.cos(a), 24*math.sin(a), -1, 0, 'gold')   # spokes
    V.disc(0, 0, 34, 0, 12, 'deepslate', rin=32); V.disc(0, 0, 35, 12, 14, 'blackstone', rin=31)                  # sanctum wall
    for k in range(18):
        a = 2*math.pi*k/18; x, y = int(33*math.cos(a)), int(33*math.sin(a)); V.box(x-1, y-1, 6, x+2, y+2, 9, 'purpur')   # wall windows
    for k in range(9):                                                                                              # nine glyph pillars
        a = 2*math.pi*k/9 + math.pi/2; x, y = int(24*math.cos(a)), int(24*math.sin(a))
        V.box(x-1, y-1, 0, x+2, y+2, 10, 'stone'); V.box(x-2, y-2, 10, x+3, y+3, 11, 'gold')
        V.box(x-1, y-1, 4, x+2, y+2, 7, 'teal' if k % 3 == 0 else 'violet')                                       # the glyph band
        V.column(x, y, 11, 14, 'amethyst'); V.set(x, y, 14, 'soul')
        b = 2*math.pi*(k+1)/9 + math.pi/2                                                                           # ward glass between pillars
        w = cube(((x+24*math.cos(b))/2+0.5, (y+24*math.sin(b))/2+0.5, 6), (8.0, 0.08, 3.0), glow("wardglass", (0.3, 0.9, 0.9), 0.5), rot=(0, 0, math.atan2(24*math.sin(b)-y, 24*math.cos(b)-x)))
    V.disc(0, 0, 6, 0, 1, 'deepslate'); V.disc(0, 0, 7, 0, 2, 'gold', rin=6)                                       # the dais
    players(V, [(20, 4), (-18, 8), (-6, -20), (15, -14)]); totem(V, 0, -20); gate(V, 0, 35, 0, 'x')
    V.build(); accent((0, 0, 8), (0.6, 0.4, 1.0), 2500, 8); accent((0, 0, 20), TEAL, 1500, 10)
    return dict(cam=(52, -64, 40), target=(0, 0, 4), lens=36)

def unwoven():
    """THE COLLAPSING LOOM — the floor is the warp: plank strips strung across a giant loom frame that unravel each phase."""
    V = Vx(); palette(V, 'darkoak', 'planks', 'spruce', 'iron', 'teal', 'gold', 'purpur'); rnd = random.Random(29)
    for sx in (-1, 1): V.box(sx*33-2, -2, -4, sx*33+2, 2, 28, 'darkoak'); V.box(sx*33-3, -3, 28, sx*33+3, 3, 30, 'spruce')   # uprights
    V.box(-33, -1, 28, 33, 1, 30, 'darkoak'); V.box(-33, -2, -4, 33, 2, -1, 'darkoak')                                       # beams
    V.box(-36, -24, -4, 36, 24, -3, 'spruce'); V.box(-36, -24, -6, 36, 24, -4, 'darkoak')                                    # the loom bed under the warp
    for k in range(23):                                                                                                     # 23 plank warp strips
        y = -22 + k*2
        if k in (3, 8, 14, 19):                                                                                              # unravelled: gaps with sagging thread
            for j in range(7): thread((-30+j*10, y+0.5, -1), (-30+j*10+rnd.uniform(-3, 3), y+0.5, -14), glow("sagthread", TEAL, 1.2), 0.08)
            continue
        V.box(-31, y, -1, 31, y+1, 0, 'planks')
    for k in range(31):                                                                                                     # vertical warp threads from the top beam
        x = -30 + k*2; thread((x+0.5, 0.5, 0), (x+0.5, 0.5, 28), glow("warp", GOLD if k % 3 == 0 else TEAL, 1.2), 0.07)
    V.box(-31, -1, 18, 31, 1, 19, 'iron'); V.box(-31, -1, 23, 31, 1, 24, 'iron')                                             # heddle bars (drop each phase)
    for sx in (-1, 1): V.box(sx*31, -23, 0, sx*31+1, 23, 1, 'iron')                                                          # shuttle rails
    for k in range(6): V.box(-26+k*10, -25, -3, -23+k*10, -22, 6, 'purpur')                                                  # bobbin pillars on the near edge
    players(V, [(14, 6), (-14, 8), (-6, -14), (12, -10)]); totem(V, 0, -20); gate(V, 0, 24, 0, 'x')
    V.build(); accent((0, 0, 10), TEAL, 2500, 8); accent((0, 0, 30), GOLD, 1200, 6)
    return dict(cam=(50, -66, 27), target=(0, 0, 6), lens=36)

def lintgolem():
    """THE DOCK DUSTBIN — a tiny laundry yard right on the Dock: washing lines, baskets, a rug to beat. Zero risk."""
    V = Vx(); palette(V, 'planks', 'oak', 'wool', 'rope', 'redwool', 'teal', 'gold', 'darkoak'); rnd = random.Random(31)
    V.box(-15, -15, -2, 15, 15, 0, 'planks'); V.box(-16, -16, -4, 16, 16, -2, 'darkoak')
    for sx in (-1, 1): V.column(sx*12, 0, 0, 7, 'oak')
    thread((-12.5, 0.5, 6.5), (12.5, 0.5, 6.5), V.mats['rope'], 0.08)
    cloth = blk("cloth", (0.72, 0.70, 0.75), rough=1.0, sheen=0.5)
    for k in range(7):
        x = -9 + k*3; c = cube((x+0.5, 0.5, 4.9), (1.1, 0.08, 1.5), cloth); c.rotation_euler = (rnd.uniform(-0.15, 0.15), 0, 0)
    for k in range(4):
        a = 2*math.pi*k/4 + 0.5; x, y = int(9*math.cos(a)), int(9*math.sin(a)); V.box(x-1, y-1, 0, x+2, y+2, 2, 'oak'); V.box(x, y, 1, x+1, y+1, 3, 'wool')
    V.box(-3, -9, 0, 3, -5, 1, 'redwool')
    for i in range(14):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(2, 12); V.set(int(r*math.cos(a)), int(r*math.sin(a)), 0, 'wool')
    V.box(-16, -16, 0, 16, -15, 1, 'oak'); V.box(-16, 15, 0, 16, 16, 1, 'oak')
    players(V, [(9, -3), (-9, 3)]); totem(V, 0, 10); gate(V, 0, 15, 0, 'x', h=4, w=2)
    V.build(); accent((0, 0, 6), (1.0, 0.9, 0.7), 900, 5)
    return dict(cam=(22, -28, 11), target=(0, 0, 2), lens=36)

def tangle():
    """THE KNOTGARDEN — a hedge maze of rope and vine knots; the boss strings paths shut behind you."""
    V = Vx(); palette(V, 'grass', 'dirt', 'hedge', 'leaves', 'rope', 'cobble', 'teal', 'gold', 'log'); rnd = random.Random(37)
    V.disc(0, 0, 31, -3, 0, 'dirt', jitter=1.0, rnd=rnd); V.disc(0, 0, 31, -1, 0, 'grass', jitter=1.0, rnd=rnd); V.disc(0, 0, 24, -7, -3, 'dirt', jitter=2, rnd=rnd)
    for r in (10, 16, 22, 28):
        n = int(r*1.2); gaps = set(rnd.sample(range(n), 3))
        for k in range(n):
            if k in gaps: continue
            a = 2*math.pi*k/n; b = 2*math.pi*(k+1)/n
            V.line(r*math.cos(a), r*math.sin(a), r*math.cos(b), r*math.sin(b), 0, 3, 'hedge', width=2)                       # continuous hedge walls
            if rnd.random() < 0.3: V.set(int(r*math.cos(a)), int(r*math.sin(a)), 3, 'leaves')
    for k in range(6):                                                                                            # radial hedge spurs joining rings
        a = 2*math.pi*k/6 + 0.9; r0 = rnd.choice((10, 16, 22)); V.line(r0*math.cos(a), r0*math.sin(a), (r0+6)*math.cos(a), (r0+6)*math.sin(a), 0, 3, 'hedge', width=2)
    for k in range(4):
        a = math.pi/2*k + 0.4; V.line(3*math.cos(a), 3*math.sin(a), 30*math.cos(a), 30*math.sin(a), -1, 0, 'cobble', width=2)
    for k in range(12):                                                                                             # rope knots strung across paths
        a = rnd.uniform(0, 6.28); r = rnd.uniform(8, 27); x, y = r*math.cos(a), r*math.sin(a)
        L.ring((x, y, 2.2), 1.3, 0.2, V.mats['rope'], rot=(rnd.uniform(0, 1.5), rnd.uniform(0, 1.5), 0))
        V.column(int(x), int(y), 0, 2, 'log')
    players(V, [(26, 5), (-24, 9), (-6, -26)]); totem(V, 0, -30); gate(V, 0, 33, 0, 'x')
    V.build(); accent((0, 0, 8), (0.9, 0.8, 0.5), 2000, 8)
    return dict(cam=(48, -58, 24), target=(0, 0, 3), lens=36)

def firstcut():
    """THE SEVERANCE — reality torn open: shards of islands floating in black void around the golden seam of the Cut; 150 blocks across."""
    V = Vx(); palette(V, 'obsidian', 'endstone', 'deepslate', 'blackstone', 'purpur', 'seam', 'void', 'teal', 'gold', 'grass', 'dirt'); rnd = random.Random(41)
    V.disc(0, 0, 42, -3, 0, 'obsidian', jitter=2.0, rnd=rnd); V.disc(0, 0, 36, -10, -3, 'blackstone', jitter=3, rnd=rnd)
    px, py = -75, -14                                                                                                # the Cut: a jagged seam across the floor and up into the sky
    for k in range(16):
        nx, ny = px+10+rnd.uniform(-2, 2), py+1.8+rnd.uniform(-4, 4); V.line(px, py, nx, ny, -1, 1, 'seam', width=2); px, py = nx, ny
    for k in range(6): thread((px*0.3+rnd.uniform(-6, 6), py*0.3+rnd.uniform(-4, 4), 20+k*4), (rnd.uniform(-8, 8), rnd.uniform(-4, 4), 70+k*6), glow("skyseam", GOLD, 3.0), 0.18)   # the seam continues up into the sky as a rift
    for k in range(20):                                                                                             # drifting world-shards
        a = 2*math.pi*k/20 + rnd.uniform(-0.2, 0.2); r = rnd.uniform(52, 78); z = int(rnd.uniform(-22, 48)); s = rnd.randint(5, 13)
        cx, cy = int(r*math.cos(a)), int(r*math.sin(a)); key = rnd.choice(('endstone', 'deepslate', 'obsidian', 'grass'))
        V.disc(cx, cy, s, z-2, z, key if key != 'grass' else 'dirt', jitter=1.5, rnd=rnd)
        if key == 'grass': V.disc(cx, cy, s, z-1, z, 'grass', jitter=1.5, rnd=rnd)
        V.disc(cx, cy, s*0.7, z-5, z-2, 'blackstone', jitter=1.5, rnd=rnd); V.disc(cx, cy, s*0.4, z-9, z-5, 'blackstone', jitter=1.0, rnd=rnd)
        if rnd.random() < 0.4: V.box(cx-1, cy-1, z, cx+1, cy+1, z+rnd.randint(2, 6), 'purpur')                    # a ruin on some shards
    for k in range(14):                                                                                             # void tears in the air
        cube((rnd.uniform(-48, 48), rnd.uniform(-48, 48), rnd.uniform(8, 44)), (0.12, rnd.uniform(1, 4), rnd.uniform(4, 14)), V.mats['void'], rot=(0, 0, rnd.uniform(0, 3)))
    players(V, [(30, 6), (-28, 10), (-10, -31), (24, -22)]); totem(V, 0, -36); gate(V, 0, 44, 0, 'x')
    V.build(); accent((0, 0, 20), GOLD, 12000, 16); accent((0, 0, 60), TEAL, 6000, 20); accent((-40, -40, 10), (0.6, 0.3, 1.0), 8000, 20)
    return dict(cam=(112, -142, 52), target=(0, 0, 14), lens=34)

def overweaver():
    """THE LOOM ABOVE — the restored Loom as a cathedral of thread: nine strand-bridges converge on the central weave where the boss IS the loom."""
    V = Vx(); palette(V, 'darkoak', 'planks', 'spruce', 'purpur', 'amethyst', 'gold', 'teal', 'oak'); rnd = random.Random(43)
    V.disc(0, 0, 36, -3, 0, 'purpur', jitter=0.8, rnd=rnd); V.disc(0, 0, 30, -8, -3, 'darkoak', jitter=2, rnd=rnd); V.disc(0, 0, 31, -1, 0, 'gold', rin=29.5)
    cols = [(0.5, 0.35, 0.2), TEAL, (0.3, 0.7, 0.3), GOLD, (1.0, 0.5, 0.15), (0.9, 0.75, 0.3), (1.0, 0.7, 0.2), (0.6, 0.45, 0.9), TEAL]
    for k in range(9):
        a = 2*math.pi*k/9 + math.pi/2; x, y = int(74*math.cos(a)), int(74*math.sin(a))
        V.disc(x, y, 11, -3, 0, 'planks', jitter=0.8, rnd=rnd); V.disc(x, y, 8, -7, -3, 'darkoak', jitter=1.5, rnd=rnd)     # nine strand platforms
        V.line(35*math.cos(a), 35*math.sin(a), 64*math.cos(a), 64*math.sin(a), -2, 0, 'planks', width=5)                        # bridges
        V.line(35*math.cos(a), 35*math.sin(a), 64*math.cos(a), 64*math.sin(a), 0, 1, 'oak', width=1)
        V.box(x-2, y-2, 0, x+2, y+2, 28, 'darkoak'); V.box(x-3, y-3, 28, x+3, y+3, 30, 'purpur'); V.set(x, y, 30, 'amethyst')   # pillars
        m = glow("strandcol%d" % k, cols[k], 1.6)
        cube((49.5*math.cos(a), 49.5*math.sin(a), 0.6), (14, 0.35, 0.05), m, rot=(0, 0, a))                                       # the strand's colour line on its bridge
        for j in range(3):
            dx, dy = (j-1)*2.0*math.cos(a+math.pi/2), (j-1)*2.0*math.sin(a+math.pi/2)
            thread((x+0.5+dx, y+0.5+dy, 30), (dx*0.4, dy*0.4, 64), glow("cathedral%d" % k, GOLD if j == 1 else TEAL, 1.4), 0.12)
        g = L.sphere((x*0.88, y*0.88, 5), 3.2, 12); g.scale = (0.8, 0.8, 1.6); g.data.materials.append(glow("shade", (0.4, 0.9, 0.85), 0.45))   # shade of that guardian
    L.sphere((0, 0, 64), 2.8, 8).data.materials.append(glow("keystone", GOLD, 3.0))
    players(V, [(20, 6), (-18, 10), (-8, -21), (16, -15)]); totem(V, 0, -27); gate(V, 0, 40, 0, 'x')
    V.build(); accent((0, 0, 20), GOLD, 10000, 16); accent((0, 0, 60), TEAL, 6000, 20)
    return dict(cam=(112, -142, 59), target=(0, 0, 18), lens=32)

ARENAS = dict(beddown=beddown, grindmaw=grindmaw, thornmother=thornmother, edgewalker=edgewalker, drumheart=drumheart, cogwright=cogwright,
              hivemind=hivemind, sealbreaker=sealbreaker, unwoven=unwoven, lintgolem=lintgolem, tangle=tangle, firstcut=firstcut, overweaver=overweaver)

def render(name, samples=48):
    b = BF.BOSSES[name]()                                   # resets the scene and builds the boss at the origin
    a = ARENAS[name]()
    ls = b.get('light', 1.0)
    cam, tgt = L.studio(target_z=a['target'][2], cam_loc=a['cam'], lens=a['lens'], fstop=8.0, teal=1600*ls, gold=1200*ls, fill=1600*ls, sun=5.0)
    tgt.location = a['target']; cam.data.dof.use_dof = False
    void_ground(); stars()
    sc = bpy.context.scene; sc.cycles.samples = samples; sc.render.resolution_x = 1280; sc.render.resolution_y = 760; sc.render.resolution_percentage = 100
    sc.render.filepath = f'{OUT}/{name}_arena.png'; bpy.ops.render.render(write_still=True); print("ARENA", name, "DONE")

import struct
def export(name, outdir):
    """block plan for the Java arena builder: .ncga = magic, keys, blocks (mc coords: x, y=z_up, z=-y), pads/totem/gate"""
    L.reset(); ARENAS[name](); V = CUR
    os.makedirs(outdir, exist_ok=True); keys = sorted(set(V.b.values())); ki = {k: i for i, k in enumerate(keys)}
    with open(os.path.join(outdir, f'{name}.ncga'), 'wb') as fh:
        fh.write(b'NCGA'); fh.write(struct.pack('<IH', 1, len(keys)))
        for k in keys: kb = k.encode(); fh.write(struct.pack('<H', len(kb))); fh.write(kb)
        fh.write(struct.pack('<I', len(V.b)))
        for (x, y, z), k in sorted(V.b.items()): fh.write(struct.pack('<3hB', x, z, -y, ki[k]))
        pads = V.meta['pads']; fh.write(struct.pack('<B', len(pads)))
        for (x, y, z) in pads: fh.write(struct.pack('<3h', int(x), int(z), int(-y)))
        tx, ty, tz = V.meta['totem'] or (0, 0, 0); fh.write(struct.pack('<3h', int(tx), int(tz), int(-ty)))
        gx, gy, gz, axis, h, w = V.meta['gate'] or (0, 0, 0, 'x', 5, 4); fh.write(struct.pack('<3hBBB', int(gx), int(gz), int(-gy), 1 if axis == 'x' else 0, h, w))
        r = max(max(abs(x), abs(y)) for (x, y, z) in V.b); fh.write(struct.pack('<h', r))
    print('ARENA DATA', name, len(V.b), 'blocks', len(keys), 'keys', 'r', r)

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
    which = list(ARENAS) if argv[0] == 'all' else argv[0].split(',')
    if len(argv) > 1 and argv[1] == 'export':
        for n in which: export(n, argv[2] if len(argv) > 2 else os.path.join(ART, 'export', 'arenas'))
    else:
        samples = int(argv[1]) if len(argv) > 1 else 48
        for n in which: render(n, samples)
