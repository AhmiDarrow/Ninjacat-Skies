#!/usr/bin/env python3
"""Procedural 32→64 paw logo for FancyMenu / UI pack. Palette from STYLEGUIDE."""
from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image

P = {
    ".": (0, 0, 0, 0),
    "I": (42, 47, 79, 255),
    "i": (58, 64, 110, 255),
    "T": (61, 122, 122, 255),
    "t": (90, 150, 148, 255),
    "G": (212, 168, 75, 255),
    "g": (230, 196, 120, 255),
    "C": (232, 224, 213, 255),
    "K": (28, 28, 36, 255),
    "D": (32, 36, 58, 255),
}

# 32x32: void-indigo disc, four separate teal toes, cream/gold palm
ROWS = [
    "................................",
    ".........KKKKKKKKKKKK...........",
    ".......KKIIIIIIIIIIIIKK.........",
    "......KIiiiiiiiiiiiiiiIK........",
    ".....KIiiiiiiiiiiiiiiiiIK.......",
    "....KIiiiiiiiiiiiiiiiiiiK.......",
    "....KIii.KKK.KK.KK.KKK.iiK......",
    "...KIii.KTTtKTTKTTKTTtK.iIK.....",
    "...KIii.KTttKttKttKTttK.iIK.....",
    "...KIii.KTTtKTTKTTKTTtK.iIK.....",
    "...KIii..KKK.KK.KK.KKK..iIK.....",
    "...KIiiii..............iiIK.....",
    "...KIiiiii............iiiIK.....",
    "...KIiiiii..........iiiiIK......",
    "...KIiiiii...KKKKKK..iiiIK......",
    "...KIiiii..KKTTTTTTKK.iiIK......",
    "...KIiiii.KTTttttttTTK.iiK......",
    "...KIiiii.KTtCCCCCCtTK.iiK......",
    "...KIiiii.KTtCgGGGgCtTK.iK......",
    "...KIiiii.KTtCGTTTGCtTK.iK......",
    "...KIiiii.KTtCGTDDTGCtTKiK......",
    "...KIiiii.KTtCGTTTGCtTK.iK......",
    "...KIiiii.KTtCgGGGgCtTK.iK......",
    "...KIiiii.KTtCCCCCCtTK.iiK......",
    "...KIiiii.KTTttttttTTK.iiK......",
    "...KIiiii..KKTTTTTTKK.iiIK......",
    "...KIiiiii...KKKKKK..iiiIK......",
    "....KIiiiii.........iiiiK.......",
    "....KIiiiiiiiiiiiiiiiiiK........",
    ".....KKIIIIIIIIIIIIIIKK.........",
    ".......KKKKKKKKKKKKKK...........",
    "................................",
]


def save(path: Path, rows: list[str], scale: int = 2) -> None:
    assert len(rows) == 32 and all(len(r) == 32 for r in rows), [
        (i, len(r), r) for i, r in enumerate(rows) if len(r) != 32
    ]
    unknown = {ch for row in rows for ch in row if ch not in P}
    assert not unknown, unknown
    img = Image.new("RGBA", (32, 32))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            px[x, y] = P[ch]
    if scale != 1:
        img = img.resize((32 * scale, 32 * scale), Image.NEAREST)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print("wrote", path, img.size)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    save(root / "pack/overrides/config/fancymenu/assets/ninjacat_logo.png", ROWS, 2)
    save(
        root
        / "pack/overrides/resourcepacks/ninjacat-skies-ui/assets/ninjacat_skies_ui/textures/gui/ninjacat_logo.png",
        ROWS,
        2,
    )


if __name__ == "__main__":
    main()
