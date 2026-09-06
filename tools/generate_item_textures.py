#!/usr/bin/env python3
"""Hand-authored 16x16 pixel textures for Ninjacat Skies mods.

Palette from docs/STYLEGUIDE.md. Patterns are explicit pixel maps — not generative.
"""
from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image

# RGBA
P = {
    ".": (0, 0, 0, 0),
    "I": (42, 47, 79, 255),   # indigo
    "i": (58, 64, 110, 255),  # indigo light
    "T": (61, 122, 122, 255), # teal
    "t": (90, 150, 148, 255), # teal light
    "G": (212, 168, 75, 255), # gold
    "g": (230, 196, 120, 255),# gold light
    "A": (138, 133, 128, 255),# ash
    "a": (168, 162, 155, 255),# ash light
    "C": (232, 224, 213, 255),# cream
    "K": (28, 28, 36, 255),   # near-black outline
    "W": (245, 240, 232, 255),# paper
    "B": (70, 52, 40, 255),   # wood brown
    "b": (110, 82, 58, 255),  # wood light
    "S": (90, 90, 98, 255),   # steel
    "s": (140, 140, 150, 255),
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


def item_model(modid: str, name: str) -> None:
    path = ROOT / "mods" / mod_folder(modid) / "src/main/resources/assets" / modid / "models/item" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{\n  "parent": "minecraft:item/generated",\n'
        f'  "textures": {{\n    "layer0": "{modid}:item/{name}"\n  }}\n}}\n',
        encoding="utf-8",
    )


def block_model(modid: str, name: str) -> None:
    base = ROOT / "mods" / mod_folder(modid) / "src/main/resources/assets" / modid
    (base / "models/block").mkdir(parents=True, exist_ok=True)
    (base / "models/item").mkdir(parents=True, exist_ok=True)
    (base / "blockstates").mkdir(parents=True, exist_ok=True)
    (base / "models/block" / f"{name}.json").write_text(
        '{\n  "parent": "minecraft:block/cube_all",\n'
        f'  "textures": {{\n    "all": "{modid}:block/{name}"\n  }}\n}}\n',
        encoding="utf-8",
    )
    (base / "models/item" / f"{name}.json").write_text(
        f'{{\n  "parent": "{modid}:block/{name}"\n}}\n',
        encoding="utf-8",
    )
    (base / "blockstates" / f"{name}.json").write_text(
        '{\n  "variants": {\n'
        f'    "": {{ "model": "{modid}:block/{name}" }}\n  }}\n}}\n',
        encoding="utf-8",
    )


def mod_folder(modid: str) -> str:
    return {
        "ninjacatskies": "ninjacatskies",
        "voidloom": "voidloom",
        "clowderhall": "clowderhall",
        "ninjacatlib": "ninjacat-lib",
    }[modid]


def tex_item(modid: str, name: str, rows: list[str]) -> None:
    path = ROOT / "mods" / mod_folder(modid) / "src/main/resources/assets" / modid / "textures/item" / f"{name}.png"
    save(path, rows)
    item_model(modid, name)


def tex_block(modid: str, name: str, rows: list[str]) -> None:
    path = ROOT / "mods" / mod_folder(modid) / "src/main/resources/assets" / modid / "textures/block" / f"{name}.png"
    save(path, rows)
    block_model(modid, name)


# --- ninjacatskies ---
tex_item("ninjacatskies", "whisker_codex", [
    "................",
    "....KKKKKKKK....",
    "...KWWWWWWWWK...",
    "...KWIIIIIIWK...",
    "...KWIGGGGIWK...",
    "...KWIIIIIIWK...",
    "...KWITTTTIWK...",
    "...KWIIIIIIWK...",
    "...KWIGGGGIWK...",
    "...KWIIIIIIWK...",
    "...KWWWWWWWWK...",
    "....KKKKKKKK....",
    "......K..K......",
    "......K..K......",
    ".......KK.......",
    "................",
])

tex_item("ninjacatskies", "frayed_thread", [
    "................",
    "................",
    "....G...........",
    "...GgG.T........",
    "....G.TtT.......",
    ".....T..T.......",
    "......T.tT......",
    ".......T..T.....",
    "........TtT.....",
    ".........T.G....",
    "..........GgG...",
    "...........G....",
    "................",
    "................",
    "................",
    "................",
])

# Twisted twin of frayed_thread — Clock/Swarm/Spark braid glue
tex_item("ninjacatskies", "braid_cord", [
    "................",
    "................",
    "...G...T........",
    "...GgT.tT.......",
    "....GTtT.G......",
    ".....TtGgG......",
    "......TG.T......",
    ".....GtT.tT.....",
    "....GgG.TtT.....",
    ".....T..T.G.....",
    "......TtTgG.....",
    ".......T.G......",
    "................",
    "................",
    "................",
    "................",
])

tex_item("ninjacatskies", "codex_page", [
    "................",
    "..KKKKKKKKKKK...",
    "..KWWWWWWWWWK...",
    "..KWIIIIIIIWK...",
    "..KWWWWWWWWWK...",
    "..KWTTTTTTTWK...",
    "..KWWWWWWWWWK...",
    "..KWIIIIIIIWK...",
    "..KWWWWWWWWWK...",
    "..KWGGGGGGGWK...",
    "..KWWWWWWWWWK...",
    "..KKKKKKKKKKK...",
    "................",
    "................",
    "................",
    "................",
])

TOKEN = [
    "................",
    "......KKKK......",
    "....KKIIIIKK....",
    "...KIIiiiiIIK...",
    "...KIiGGGGiIK...",
    "..KIiG....GiIK..",
    "..KIiG.TT.GiIK..",
    "..KIiG.Tt.GiIK..",
    "..KIiG.TT.GiIK..",
    "..KIiG....GiIK..",
    "...KIiGGGGiIK...",
    "...KIIiiiiIIK...",
    "....KKIIIIKK....",
    "......KKKK......",
    "................",
    "................",
]
for strand in ("soil", "stone", "sprout", "claw", "spark", "clock", "swarm", "sigil", "spindle"):
    tex_item("ninjacatskies", f"strand_token_{strand}", TOKEN)

tex_item("ninjacatskies", "spindle_loom_fragment", [
    "................",
    "......KKKK......",
    "....KKGGGGKK....",
    "...KGgTTTTGgK...",
    "...KGTiiiiTGK...",
    "..KGTIiGGiITGK..",
    "..KGTiG..GiTGK..",
    "..KGTiGttGiTGK..",
    "..KGTiGttGiTGK..",
    "..KGTiG..GiTGK..",
    "..KGTIiGGiITGK..",
    "...KGTiiiiTGK...",
    "...KGgTTTTGgK...",
    "....KKGGGGKK....",
    "......KKKK......",
    "................",
])

# --- voidloom ---
tex_item("voidloom", "void_yarn", [
    "................",
    "................",
    "......IiI.......",
    ".....ITTtI......",
    "....ITt..tI.....",
    "...IT......TI...",
    "...I.T....T.I...",
    "...I..TtTt..I...",
    "...I..tTTt..I...",
    "...I.T....T.I...",
    "...IT......TI...",
    "....It..tTI.....",
    ".....ITTtI......",
    "......IiI.......",
    "................",
    "................",
])

tex_item("voidloom", "binding_knot", [
    "................",
    "................",
    "......KK........",
    ".....KGGK.......",
    "....KGg..GK.....",
    "...KG..TT..GK...",
    "...KG.TiiT.GK...",
    "....KGiiiiGK....",
    "....KGiiiiGK....",
    "...KG.TiiT.GK...",
    "...KG..TT..GK...",
    "....KGg..GK.....",
    ".....KGGK.......",
    "......KK........",
    "................",
    "................",
])

MESH = [
    "................",
    ".KKKKKKKKKKKKKK.",
    ".K............K.",
    ".K.AAAAAAAAAA.K.",
    ".K.A........A.K.",
    ".K.A.AAAAAA.A.K.",
    ".K.A.A....A.A.K.",
    ".K.A.A.TT.A.A.K.",
    ".K.A.A.Tt.A.A.K.",
    ".K.A.A....A.A.K.",
    ".K.A.AAAAAA.A.K.",
    ".K.A........A.K.",
    ".K.AAAAAAAAAA.K.",
    ".K............K.",
    ".KKKKKKKKKKKKKK.",
    "................",
]
tex_item("voidloom", "thread_mesh_string", MESH)
tex_item("voidloom", "thread_mesh_flint", [r.replace("T", "A").replace("t", "a") for r in MESH])
tex_item("voidloom", "thread_mesh_iron", [r.replace("T", "S").replace("t", "s") for r in MESH])

tex_item("voidloom", "spindle_hammer", [
    "................",
    ".........sss....",
    "........sSSs....",
    ".......sSSSs....",
    "......sSSS......",
    ".....sSSK.......",
    "....bBK.........",
    "...bBK..........",
    "..bBK...........",
    ".bBK............",
    ".BK.............",
    "bB..............",
    "................",
    "................",
    "................",
    "................",
])

tex_item("voidloom", "spindle_crook", [
    "................",
    "......bbb.......",
    ".....bBBb.......",
    "....bB..Bb......",
    "....bB...B......",
    ".........Bb.....",
    "..........Bb....",
    "...........Bb...",
    "............Bb..",
    ".............Bb.",
    "..............Bb",
    "..............Bb",
    ".............Bb.",
    "............Bb..",
    "................",
    "................",
])

tex_block("voidloom", "loomframe", [
    "BBBBBBBBBBBBBBBB",
    "BiiiiiiiiiiiiiiB",
    "BiIIIIIIIIIIIIiB",
    "BiI..........IiB",
    "BiI.TTTTTTTT.IiB",
    "BiI.T......T.IiB",
    "BiI.T.GGGG.T.IiB",
    "BiI.T.G..G.T.IiB",
    "BiI.T.G..G.T.IiB",
    "BiI.T.GGGG.T.IiB",
    "BiI.T......T.IiB",
    "BiI.TTTTTTTT.IiB",
    "BiI..........IiB",
    "BiIIIIIIIIIIIIiB",
    "BiiiiiiiiiiiiiiB",
    "BBBBBBBBBBBBBBBB",
])

tex_block("voidloom", "tension_barrel", [
    "....BBBBBBBB....",
    "...BbbbbbbbbB...",
    "..BbIIIIIIIIbB..",
    "..BbI......IbB..",
    "..BbI.TTTT.IbB..",
    "..BbI.TggT.IbB..",
    "..BbI.TgGT.IbB..",
    "..BbI.TTTT.IbB..",
    "..BbI......IbB..",
    "..BbIIIIIIIIbB..",
    "..BbbbbbbbbbbB..",
    "..BbBBBBBBBBbB..",
    "..Bb........bB..",
    "..BbbbbbbbbbbB..",
    "...BBBBBBBBBB...",
    "................",
])

# --- clowderhall ---
tex_item("clowderhall", "island_charter", [
    "................",
    "..KKKKKKKKKKK...",
    "..KCCggggggCK...",
    "..KCgWWWWWWgCK..",
    "..KCgWIIIIWgCK..",
    "..KCgWITTIWgCK..",
    "..KCgWI..TWgCK..",
    "..KCgWIGGGWgCK..",
    "..KCgWIIIIWgCK..",
    "..KCgWWWWWWgCK..",
    "..KCCggggggCK...",
    "..KKKKKKKKKKK...",
    "......KK........",
    "......KK........",
    "................",
    "................",
])

tex_item("clowderhall", "hub_key", [
    "................",
    "................",
    "........GGG.....",
    ".......GgggG....",
    ".......Gg.gG....",
    ".......GgggG....",
    ".........G......",
    ".........G......",
    ".........G.G....",
    ".........G......",
    ".........G.G....",
    ".........G......",
    "................",
    "................",
    "................",
    "................",
])

tex_item("clowderhall", "strand_banner_pattern", [
    "................",
    ".CCCCCCCCCCCCCC.",
    ".CIIIIIIIIIIIIC.",
    ".CI..........IC.",
    ".CI.TTTTTTTT.IC.",
    ".CI.T......T.IC.",
    ".CI.T.GGGG.T.IC.",
    ".CI.T.GiiG.T.IC.",
    ".CI.T.GGGG.T.IC.",
    ".CI.T......T.IC.",
    ".CI.TTTTTTTT.IC.",
    ".CI..........IC.",
    ".CIIIIIIIIIIIIC.",
    ".CCCCCCCCCCCCCC.",
    "................",
    "................",
])

print("done")
