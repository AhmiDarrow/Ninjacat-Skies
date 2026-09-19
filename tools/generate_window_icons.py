#!/usr/bin/env python3
"""Game-window icons (FancyMenu): pack/overrides/config/fancymenu/assets/window_icon_{16,32}.png.

    python tools/generate_window_icons.py [--check]

A clear mark that reads in a taskbar at 16px: a black ninjacat head (hood slit, teal eyes) against a night-sky
tile with a copper rim. Both sizes are drawn natively (the 16px one is a hand pixel map, never a downscale).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core_pixel import *  # noqa: E402,F403

DEST = ROOT / "pack/overrides/config/fancymenu/assets"
PAL = {
    "K": INK, "c": COPPER_LIGHT, "C": COPPER_DARK, "o": COPPER,
    "n": (0x34, 0x4c, 0x84), "m": (0x28, 0x3a, 0x6a), "S": BONE_LIGHT, "s": BONE_SHADE,
    "B": (0x12, 0x14, 0x22), "b": (0x3a, 0x40, 0x68), "e": COPPER_DARK,
    "I": (0x2e, 0x34, 0x58), "T": LOOM, "t": LOOM_PALE, "M": BRASS_LIGHT,
}
ICON16 = [
    "KKKKKKKKKKKKKKKK",
    "KcccccccccccccCK",
    "KcnnnnnnnnnSnnCK",
    "KcnBnnnnnnnnBnCK",
    "KcnBBnnSnnnBBnCK",
    "KcnBeBBBBBBeBnCK",
    "KcBBBBBBBBBBBBCK",
    "KcBIIIIIIIIIIBCK",
    "KcBITtIIIITtIBCK",
    "KcBIIIIIIIIIIBCK",
    "KcmBBBBBBBBBBmCK",
    "KcmmBBBBBBBBmmCK",
    "KcmmmBBBBBBmmmCK",
    "KcmmmmmmmmmmmmCK",
    "KcCCCCCCCCCCCCCK",
    "KKKKKKKKKKKKKKKK",
]


def icon32():
    im = blank(); d = draw(im); P = {k: rgba(v) for k, v in PAL.items()}
    d.rectangle((0, 0, 31, 31), fill=P["K"])
    d.rectangle((1, 1, 30, 30), fill=P["o"])
    d.line((1, 1, 30, 1), fill=P["c"]); d.line((1, 1, 1, 30), fill=P["c"])
    d.line((2, 30, 30, 30), fill=P["C"]); d.line((30, 2, 30, 30), fill=P["C"])
    d.rectangle((3, 3, 28, 28), fill=P["K"])
    d.rectangle((4, 4, 27, 17), fill=P["n"]); d.rectangle((4, 18, 27, 27), fill=P["m"])   # sky, two flat bands
    for (x, y) in ((5, 5), (22, 5), (26, 12), (9, 5)):
        d.point((x, y), fill=P["S"])
    d.point((26, 7), fill=P["s"])
    d.ellipse((13, 4, 18, 9), fill=P["M"]); d.ellipse((15, 4, 19, 8), fill=P["n"])        # crescent moon
    # cat head: ears + round skull + cheeks
    d.polygon(((6, 6), (13, 12), (7, 15)), fill=P["B"]); d.polygon(((25, 6), (18, 12), (24, 15)), fill=P["B"])
    d.polygon(((8, 9), (11, 12), (8, 13)), fill=P["e"]); d.polygon(((23, 9), (20, 12), (23, 13)), fill=P["e"])
    d.ellipse((6, 10, 25, 28), fill=P["B"])
    d.arc((6, 10, 25, 28), 190, 250, fill=P["b"])                                            # rim light top-left
    # hood slit with glowing eyes
    d.rectangle((7, 16, 24, 20), fill=P["I"]); d.line((7, 16, 24, 16), fill=P["b"])
    for x in (10, 18):
        d.rectangle((x, 17, x + 3, 19), fill=P["T"]); d.point((x, 17), fill=P["t"]); d.point((x + 1, 17), fill=P["t"])
        d.point((x + 3, 19), fill=rgba(LOOM_DEEP))
    d.point((15, 23), fill=P["b"]); d.point((16, 23), fill=P["b"])                           # nose glint
    d.line((5, 27, 26, 27), fill=P["m"])
    return im


def build():
    return {"window_icon_16.png": from_rows(ICON16, PAL), "window_icon_32.png": icon32()}


def main():
    check = "--check" in sys.argv; drift = []
    for name, im in build().items():
        assert im.size in ((16, 16), (32, 32)) and all(len(r) == 16 for r in ICON16)
        p = DEST / name
        if check:
            if Image.open(p).convert("RGBA").tobytes() != im.tobytes():
                drift.append(name)
        else:
            save(im, p)
    if drift:
        sys.exit("window icon drift: " + ", ".join(drift))


if __name__ == "__main__":
    main()
