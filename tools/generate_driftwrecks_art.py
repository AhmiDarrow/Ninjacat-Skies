#!/usr/bin/env python3
"""Driftwrecks pixel art: every item and block texture at native 32x32, the Drift Needle's 32 frames, 54 Keepsakes
+ the Heart of the Weave, nine Tribe Banners, and the Steward echo entity skin.

    python tools/generate_driftwrecks_art.py [--sheets DIR]

Style: the family STYLE_TARGET (32 px, hard alpha, 1 px outline tinted toward the item's hue from ink #111a22,
top-left light, 4-5 tone hue-shifted ramps; teal tether thread + gold seam as the Driftwrecks mark). Tribe/Strand
glyphs and colours come from tools/art_tribe_glyphs.py (the canonical Tribal Power glyphs).

Modules:
  driftwrecks_art_lib         canvas, ramps, lit shapes, outline
  driftwrecks_art_items       thread goods, lures, key, paper goods, salvage, Drift Needle frames
  driftwrecks_art_keepsakes1  keepsakes: soil, stone, sprout, claw
  driftwrecks_art_keepsakes2  keepsakes: spark, clock, swarm, sigil, spindle; Heart of the Weave; glyph tag
  driftwrecks_art_blocks      blocks (UV notes in its docstring) and Tribe Banners
Filenames and ids are unchanged; models reference the same textures.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from driftwrecks_content import C, CORES, STRANDS, TRIBES  # noqa: E402
import driftwrecks_art_blocks as blocks_mod  # noqa: E402
import driftwrecks_art_items as items_mod  # noqa: E402
from driftwrecks_art_keepsakes2 import heart_keepsake, keepsake  # noqa: E402

TEX = ROOT / "mods/driftwrecks/src/main/resources/assets/driftwrecks/textures"
TEAL, TEAL_LT, GOLD = (0x3D, 0x7A, 0x7A), (0x5C, 0xD8, 0xC8), (0xD4, 0xA8, 0x4B)
INK = (0x2A, 0x2F, 0x4F)


def items():
    I = TEX / "item"
    for name, fn in items_mod.ITEMS.items():
        fn().save(I / f"{name}.png")
    # the needle: 32 frames, frame 16 points straight up (target ahead), clockwise
    for i in range(32):
        items_mod.drift_needle(i).save(I / f"drift_needle_{i:02d}.png")
    seen = {}
    for s in STRANDS:
        for c in CORES:
            g = keepsake(s, c)
            h = hashlib.md5(g.im.tobytes()).hexdigest()
            assert h not in seen, f"keepsake_{s}_{c} duplicates {seen.get(h)}"
            seen[h] = f"keepsake_{s}_{c}"
            g.save(I / f"keepsake_{s}_{c}.png")
    heart_keepsake().save(I / "keepsake_heartwreck.png")


def blocks():
    B = TEX / "block"
    for name, fn in blocks_mod.BLOCKS.items():
        fn().save(B / f"{name}.png")
    for s in STRANDS:
        blocks_mod.tribe_banner(s).save(B / f"tribe_banner_{s}.png")


def entity():
    """Steward echo skin (64x32 vanilla-cat UV) is painted by tools/generate_steward_echo.py."""
    E = TEX / "entity"
    E.mkdir(parents=True, exist_ok=True)
    from generate_steward_echo import steward_echo
    steward_echo().save(E / "steward_echo.png")


def sheets(out: Path):
    """One render sheet per Strand (six Keepsakes, x3, with names) and one of all 54, for approval."""
    out.mkdir(parents=True, exist_ok=True)
    for s in STRANDS:
        W, H = 6 * 150, 190
        sheet = Image.new("RGB", (W, H), (0xED, 0xE3, 0xCC))
        d = ImageDraw.Draw(sheet)
        d.text((10, 6), f"{TRIBES[s]} ({s}) keepsakes", fill=INK)
        for i, c in enumerate(CORES):
            im = Image.open(TEX / "item" / f"keepsake_{s}_{c}.png").resize((96, 96), Image.NEAREST)
            sheet.paste(im, (i * 150 + 27, 26), im)
            name = C[s][c][0]
            d.text((i * 150 + 8, 130), c, fill=TEAL)
            for j, line in enumerate([name[k:k + 22] for k in range(0, len(name), 22)]):
                d.text((i * 150 + 8, 146 + j * 12), line, fill=INK)
        sheet.save(out / f"keepsakes_{s}.png")
    all_ = Image.new("RGB", (6 * 72 + 20, 9 * 72 + 20), (0x80, 0x80, 0x80))
    for r, s in enumerate(STRANDS):
        for c, core in enumerate(CORES):
            im = Image.open(TEX / "item" / f"keepsake_{s}_{core}.png").resize((64, 64), Image.NEAREST)
            all_.paste(im, (10 + c * 72, 10 + r * 72), im)
    all_.save(out / "keepsakes_all.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets", default="")
    a = ap.parse_args()
    items()
    blocks()
    entity()
    if a.sheets:
        sheets(Path(a.sheets))
    print("Driftwrecks art written to", TEX.relative_to(ROOT))


if __name__ == "__main__":
    main()
