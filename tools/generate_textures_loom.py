#!/usr/bin/env python3
"""Hand-authored 16x16 textures for the Loom Tension layer (Tension Post, nine tribe tokens, Voidloom scraps).

Explicit pixel maps in the STYLEGUIDE palette — companion to generate_item_textures.py, which still owns
the rest. Run from anywhere: paths resolve from the repo root.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

P = {
    ".": (0, 0, 0, 0),
    "I": (42, 47, 79, 255),    # indigo
    "i": (58, 64, 110, 255),   # indigo light
    "T": (61, 122, 122, 255),  # teal
    "t": (90, 150, 148, 255),  # teal light
    "G": (212, 168, 75, 255),  # gold
    "g": (230, 196, 120, 255), # gold light / honey
    "A": (138, 133, 128, 255), # ash
    "a": (168, 162, 155, 255), # ash light
    "C": (232, 224, 213, 255), # cream
    "K": (28, 28, 36, 255),    # outline
    "B": (70, 52, 40, 255),    # wood brown
    "b": (110, 82, 58, 255),   # wood light
    "S": (90, 90, 98, 255),    # steel
    "s": (140, 140, 150, 255), # steel light
    "V": (107, 142, 58, 255),  # soil green
    "v": (140, 172, 90, 255),
    "N": (90, 175, 90, 255),   # sprout green
    "n": (130, 205, 130, 255),
    "O": (200, 122, 58, 255),  # copper (Clock)
    "o": (226, 158, 96, 255),
    "P": (138, 95, 184, 255),  # violet (Sigil)
    "p": (176, 140, 214, 255),
}

ROOT = Path(__file__).resolve().parents[1]


def save(path: Path, rows: list[str]) -> None:
    assert len(rows) == 16 and all(len(r) == 16 for r in rows), path
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            px[x, y] = P[ch]
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print("wrote", path.relative_to(ROOT))


def asset(modid: str, folder: str) -> Path:
    mod_folder = {"ninjacatskies": "ninjacatskies", "voidloom": "voidloom"}[modid]
    return ROOT / "mods" / mod_folder / "src/main/resources/assets" / modid / folder


def item_model(modid: str, name: str) -> None:
    path = asset(modid, "models/item") / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{\n  "parent": "minecraft:item/generated",\n'
        f'  "textures": {{\n    "layer0": "{modid}:item/{name}"\n  }}\n}}\n',
        encoding="utf-8",
    )


# --- Strand tokens: same coin, tribe ring color + a glyph each ---------------------------------

def token(ring: str, ring_light: str, glyph: list[str]) -> list[str]:
    """glyph: 6 rows of 6 chars placed at (5,5)."""
    rows = [
        "................",
        "......KKKK......",
        "....KKIIIIKK....",
        "...KIIiiiiIIK...",
        "...KIiRRRRiIK...",
        "..KIiR....RiIK..",
        "..KIiR....RiIK..",
        "..KIiR....RiIK..",
        "..KIiR....RiIK..",
        "..KIiR....RiIK..",
        "...KIiRRRRiIK...",
        "...KIIiiiiIIK...",
        "....KKIIIIKK....",
        "......KKKK......",
        "................",
        "................",
    ]
    rows = [r.replace("R", ring) for r in rows]
    # highlight top-left of ring
    rows[4] = rows[4][:6] + ring_light + rows[4][7:]
    rows[5] = rows[5][:5] + ring_light + rows[5][6:]
    out = []
    for y, r in enumerate(rows):
        if 5 <= y <= 9:
            g = glyph[y - 5]
            r = r[:6] + g[1:5] + r[10:]
        out.append(r)
    return out


TOKENS = {
    # ring, light, 5x6 glyph rows (only cols 1..4 are used)
    "soil": ("V", "v", [
        "......",
        "..VV..",
        ".vVVv.",
        ".BBBB.",
        ".bBBb.",
    ]),
    "stone": ("A", "a", [
        "......",
        ".a..a.",
        "..A...",
        ".a.aA.",
        "......",
    ]),
    "sprout": ("N", "n", [
        "...n..",
        "..nN..",
        ".nNN..",
        "..N...",
        "..N...",
    ]),
    "claw": ("S", "s", [
        ".s.s..",
        ".S.S.s",
        ".S.S.S",
        "..S.S.",
        "......",
    ]),
    "spark": ("G", "g", [
        "...gG.",
        "..gG..",
        ".GGGG.",
        "...G..",
        "..G...",
    ]),
    "clock": ("O", "o", [
        "..o...",
        ".oOOo.",
        ".O..O.",
        ".oOOo.",
        "..o...",
    ]),
    "swarm": ("g", "C", [
        "..gg..",
        ".gGGg.",
        ".GggG.",
        ".gGGg.",
        "..gg..",
    ]),
    "sigil": ("P", "p", [
        ".p..p.",
        "..PP..",
        "..P...",
        "..PP..",
        ".P..P.",
    ]),
    "spindle": ("T", "t", [
        ".tTTt.",
        ".T..T.",
        ".T.tT.",
        ".TTT..",
        "......",
    ]),
}

for name, (ring, light, glyph) in TOKENS.items():
    save(asset("ninjacatskies", "textures/item") / f"strand_token_{name}.png", token(ring, light, glyph))
    item_model("ninjacatskies", f"strand_token_{name}")

# --- Tension Post block ------------------------------------------------------------------------

save(asset("ninjacatskies", "textures/block") / "tension_post.png", [
    "BBBBBBBBBBBBBBBB",
    "BbbbbbbbbbbbbbbB",
    "BbIIIIIIIIIIIIbB",
    "BbIiiiiiiiiiiIbB",
    "BbIiTTTTTTTTiIbB",
    "BbIiiiiiiiiiiIbB",
    "BbIiiiiiiiiiiIbB",
    "BbIiTTTTTTTTiIbB",
    "BbIiiiiiiiiiiIbB",
    "BbIiiiiiiiiiiIbB",
    "BbIiTTTTTTTTiIbB",
    "BbIiiiiiiiiiiIbB",
    "BbIiiiiiiiiiiIbB",
    "BbIIIIIIIIIIIIbB",
    "BbbbbbbbbbbbbbbB",
    "BBBBBBBBBBBBBBBB",
])
save(asset("ninjacatskies", "textures/block") / "tension_post_top.png", [
    "BBBBBBBBBBBBBBBB",
    "BbbbbbbbbbbbbbbB",
    "BbBBBBBBBBBBBBbB",
    "BbBbbbbbbbbbbBbB",
    "BbBbIIIIIIIIbBbB",
    "BbBbIiiiiiiIbBbB",
    "BbBbIiTTTTiIbBbB",
    "BbBbIiTGGTiIbBbB",
    "BbBbIiTGGTiIbBbB",
    "BbBbIiTTTTiIbBbB",
    "BbBbIiiiiiiIbBbB",
    "BbBbIIIIIIIIbBbB",
    "BbBbbbbbbbbbbBbB",
    "BbBBBBBBBBBBBBbB",
    "BbbbbbbbbbbbbbbB",
    "BBBBBBBBBBBBBBBB",
])

# Notches: 4x4 used (uv 0..4) — outline + fill + one highlight pixel. Rest of the 16x16 is the fill.
NOTCH_COLORS = {
    "soil": ("V", "v"), "stone": ("A", "a"), "sprout": ("N", "n"), "claw": ("S", "s"), "spark": ("G", "g"),
    "clock": ("O", "o"), "swarm": ("g", "C"), "sigil": ("P", "p"), "spindle": ("T", "t"), "rewoven": ("C", "g"),
}
for name, (fill, light) in NOTCH_COLORS.items():
    rows = ["K" + fill * 14 + "K"] * 16
    rows[0] = "K" * 16
    rows[15] = "K" * 16
    rows[1] = "K" + light + fill * 13 + "K"
    # 4x4 region top-left is what the model samples
    rows[1] = "K" + light + light + fill + rows[1][4:]
    rows[2] = "K" + light + fill + fill + rows[2][4:]
    rows[3] = "K" + fill + fill + "K" + rows[3][4:]
    save(asset("ninjacatskies", "textures/block") / f"notch_{name}.png", rows)

# --- Voidloom scraps --------------------------------------------------------------------------

save(asset("voidloom", "textures/item") / "loom_lint.png", [
    "................",
    "................",
    "......t.t.......",
    ".....tCtCt......",
    "....tCaCaCt.....",
    ".....CaCaC......",
    "....tCaCaCt.....",
    ".....CaCaC......",
    "....tCaCaCt.....",
    ".....tCtCt......",
    "......t.t.......",
    "................",
    "................",
    "................",
    "................",
    "................",
])
item_model("voidloom", "loom_lint")

save(asset("voidloom", "textures/item") / "strand_filament.png", [
    "................",
    "..............G.",
    ".............Gg.",
    "............GgT.",
    "...........Ggt..",
    "..........GgT...",
    ".........Ggt....",
    "........GgT.....",
    ".......Ggt......",
    "......GgT.......",
    ".....Ggt........",
    "....GgT.........",
    "...Ggt..........",
    "..GT............",
    ".G..............",
    "................",
])
item_model("voidloom", "strand_filament")

print("done")
