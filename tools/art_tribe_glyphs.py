"""Canonical tribe glyphs and colours for every Ninjacat Skies art generator.

Copied from tribal-power tools/art/tribes.py (glyph bitmaps live in its tools/art/glyphs.py); keep in sync.
Do not change the glyph shapes here: one canonical glyph per tribe is used everywhere a tribe or Strand is shown
(Tribal marks/banners, Core strand tokens/notches, Driftwrecks banners/keepsakes).

Strand ids in Ninjacat Skies (Core, Driftwrecks, Clowder Hall) are the tribe ids, so STRAND_TO_TRIBE is identity.

    from art_tribe_glyphs import TRIBES, GLYPHS, TRIBE_COLORS, draw_glyph
    draw_glyph(img, 'claw', x, y, (225, 217, 189))              # 9x9 glyph, top-left at (x, y)
    draw_glyph(img, 'claw', x, y, colour, scale=2, shadow=deep) # 18x18 with a 1 px drop shadow

API
    TRIBES            ordered list of the nine tribe ids
    TRIBE_NAMES       tribe id -> people name ("Edge-walkers")
    TRIBE_COLORS      tribe id -> (r, g, b) accent colour
    GLYPH_SIZE        9 (every glyph is GLYPH_SIZE x GLYPH_SIZE cells)
    GLYPH_NAMES       tribe id -> glyph name ("boot")
    GLYPHS            tribe id -> list[str] pixel map ('#' = ink, '.' = empty)
    GLYPHS_BY_NAME    glyph name -> list[str]
    STRAND_TO_TRIBE   strand id -> tribe id
    glyph_pixels(tribe, scale=1) -> list of (x, y) offsets that are ink
    draw_glyph(img, tribe, x, y, color, scale=1, shadow=None)  paints onto a PIL RGBA Image (or ImageDraw) in place
"""
from __future__ import annotations

TRIBES = ["soil", "stone", "sprout", "claw", "spark", "clock", "swarm", "sigil", "spindle"]
TRIBE_NAMES = {"soil": "Pad-keepers", "stone": "Grit-singers", "sprout": "Rootbinders", "claw": "Edge-walkers",
               "spark": "Drumhearts", "clock": "Pattern-weavers", "swarm": "Colony-keepers", "sigil": "Seal-carvers",
               "spindle": "Loom-stitchers"}
TRIBE_COLORS = {
    "soil": (0x8b, 0x5a, 0x2b), "stone": (0x7d, 0x87, 0x91), "sprout": (0x4f, 0x9a, 0x5a),
    "claw": (0xb8, 0x51, 0x2f), "spark": (0xe0, 0xa3, 0x2d), "clock": (0x4a, 0x7f, 0xb5),
    "swarm": (0xd7, 0xb2, 0x3c), "sigil": (0x8a, 0x5f, 0xc7), "spindle": (0x62, 0xd1, 0xc9),
}
GLYPH_NAMES = {"soil": "hearth", "stone": "mesh", "sprout": "root", "claw": "boot", "spark": "drum",
               "clock": "cog", "swarm": "comb", "sigil": "seal", "spindle": "spindle"}
STRAND_TO_TRIBE = {t: t for t in TRIBES}
GLYPH_SIZE = 9

GLYPHS_BY_NAME = {
    # hearth: a low bowl of banked embers with one small flame licking up from the coals
    "hearth": ["....#....", "...#.#...", "..#...#..", "..#.#.#..", "#..#.#..#",
               "#########", ".#######.", "..#####..", "...###..."],
    # mesh: a knotted net of diagonal cords (the Grit-singers' ore mesh)
    "mesh": ["#...#...#", ".#.#.#.#.", "..#...#..", ".#.#.#.#.", "#...#...#",
             ".#.#.#.#.", "..#...#..", ".#.#.#.#.", "#...#...#"],
    # root: a sprout above spreading roots
    "root": ["....#....", "...##....", "..#.#.#..", "....##...", "....#....",
             "#########", ".#..#..#.", "#...#...#", "#..#.#..#"],
    # boot: a walking boot with a spur
    "boot": ["...###...", "...#.#...", "...#.#...", "...#.#...", "...#.##..",
             "..##..#..", ".#....#..", "#......#.", "#########"],
    # drum: a standing drum with a strike line
    "drum": ["....#....", ".#######.", "#.......#", "#########", "#.#...#.#",
             "#..#.#..#", "#...#...#", "#########", ".#######."],
    # cog: a gear with a hollow hub
    "cog": ["..#.#.#..", ".#######.", "##.....##", ".#..#..#.", "##.###.##",
            ".#..#..#.", "##.....##", ".#######.", "..#.#.#.."],
    # comb: three hexagonal cells
    "comb": ["..#...#..", ".#.#.#.#.", "#...#...#", "#...#...#", ".#.#.#.#.",
             "..#...#..", ".#.#.#.#.", "#...#...#", ".#.#.#.#."],
    # seal: a ring around a dotted centre
    "seal": ["..#####..", ".#.....#.", "#..###..#", "#.#...#.#", "#.#.#.#.#",
             "#.#...#.#", "#..###..#", ".#.....#.", "..#####.."],
    # spindle: a shaft through a diamond bobbin with crossing thread
    "spindle": ["#...#...#", ".#..#..#.", "..#.#.#..", "...###...", "..#####..",
                "...###...", "..#.#.#..", ".#..#..#.", "#...#...#"],
}
GLYPHS = {t: GLYPHS_BY_NAME[GLYPH_NAMES[t]] for t in TRIBES}


def glyph_pixels(tribe, scale=1):
    """(x, y) offsets of every ink pixel of the tribe's glyph at the given integer scale."""
    out = []
    for j, row in enumerate(GLYPHS[STRAND_TO_TRIBE.get(tribe, tribe)]):
        for i, ch in enumerate(row):
            if ch == "#":
                out.extend((i * scale + a, j * scale + b) for b in range(scale) for a in range(scale))
    return out


def _painter(img):
    """Return put(x, y, rgba) for a PIL Image or an ImageDraw.Draw."""
    if hasattr(img, "point") and hasattr(img, "rectangle"):   # ImageDraw.Draw
        return lambda x, y, c: img.point((x, y), fill=c)
    w, h = img.size
    px = img.load()

    def put(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            px[x, y] = c
    return put


def _rgba(c):
    c = tuple(c)
    return c if len(c) == 4 else c + (255,)


def draw_glyph(img, tribe, x, y, color, scale=1, shadow=None):
    """Paint the tribe's canonical glyph with its top-left at (x, y); each cell is `scale` px.

    `img` is a PIL RGBA Image (or an ImageDraw.Draw). `shadow`, if given, is painted 1 px down-right first."""
    put = _painter(img)
    pts = glyph_pixels(tribe, scale)
    if shadow is not None:
        s = _rgba(shadow)
        for dx, dy in pts:
            put(x + dx + 1, y + dy + 1, s)
    c = _rgba(color)
    for dx, dy in pts:
        put(x + dx, y + dy, c)
