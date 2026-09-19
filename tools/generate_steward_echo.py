#!/usr/bin/env python3
"""Steward Echo skin (driftwrecks textures/entity/steward_echo.png, 64x32, vanilla cat box-UV layout).

    python tools/generate_steward_echo.py [--check]

A cat spun from teal loom thread: wound-thread bands along every box, lighter on top faces, darker underneath,
bone eyes and a brass nose on the face. EchoRenderer draws it translucent with the vanilla cat model.
tools/generate_driftwrecks_art.py calls steward_echo() for its entity pass.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core_pixel import *  # noqa: E402,F403

DEST = ROOT / "mods/driftwrecks/src/main/resources/assets/driftwrecks/textures/entity/steward_echo.png"
# vanilla OcelotModel boxes: name -> (u, v, w, h, d)
BOXES = {
    "head": (0, 0, 5, 4, 5), "ear_l": (0, 10, 1, 1, 2), "ear_r": (6, 10, 1, 1, 2), "nose": (0, 24, 3, 2, 1),
    "body": (20, 0, 4, 16, 6), "tail1": (0, 15, 1, 8, 1), "tail2": (4, 15, 1, 8, 1),
    "leg_back": (8, 13, 2, 6, 2), "leg_front": (40, 0, 2, 10, 2),
}


def faces(u, v, w, h, d):
    """Box-UV face rectangles (x0, y0, x1, y1) inclusive: top, bottom, then the four sides."""
    return {
        "top": (u + d, v, u + d + w - 1, v + d - 1), "bottom": (u + d + w, v, u + d + 2 * w - 1, v + d - 1),
        "sides": [(u, v + d, u + d - 1, v + d + h - 1), (u + d, v + d, u + d + w - 1, v + d + h - 1),
                  (u + d + w, v + d, u + 2 * d + w - 1, v + d + h - 1), (u + 2 * d + w, v + d, u + 2 * d + 2 * w - 1, v + d + h - 1)],
        "front": (u + d, v + d, u + d + w - 1, v + d + h - 1),
    }


def steward_echo():
    im = blank(64, 32); d = draw(im); t = ramp(LOOM)
    for name, box in BOXES.items():
        f = faces(*box)
        x0, y0, x1, y1 = f["top"]; d.rectangle(f["top"], fill=t[3])
        for x in range(x0, x1 + 1, 2):
            d.point((x, y0), fill=t[4])
        d.rectangle(f["bottom"], fill=t[1])
        for sx0, sy0, sx1, sy1 in f["sides"]:
            for y in range(sy0, sy1 + 1):  # wound thread: two-row bands, a darker turn every third band
                band = (y - sy0) // 2
                c = t[2] if band % 3 else t[1]
                d.line((sx0, y, sx1, y), fill=c)
                if (y - sy0) % 2 == 0 and band % 3:
                    d.line((sx0, y, sx1, y), fill=t[3] if (y - sy0) % 4 == 0 else t[2])
            d.point((sx0, sy1), fill=t[0]); d.point((sx1, sy1), fill=t[0])
    # face: head front is 5x4 at (5, 5)
    fx, fy, _, _ = faces(*BOXES["head"])["front"]
    d.rectangle((fx, fy, fx + 4, fy + 3), fill=t[2])
    d.point((fx + 1, fy + 1), fill=BONE_LIGHT); d.point((fx + 3, fy + 1), fill=BONE_LIGHT)
    d.point((fx + 2, fy + 3), fill=t[0])
    nx, ny, _, _ = faces(*BOXES["nose"])["front"]
    d.rectangle((nx, ny, nx + 2, ny + 1), fill=t[2]); d.point((nx + 1, ny), fill=BRASS_LIGHT); d.point((nx + 1, ny + 1), fill=BRASS)
    # a single brass stitch down the spine (body top) marks the Steward's thread
    bx0, by0, bx1, by1 = faces(*BOXES["body"])["top"]
    for y in range(by0, by1 + 1, 2):
        d.point(((bx0 + bx1) // 2, y), fill=BRASS)
    return im


def main():
    im = steward_echo()
    if "--check" in sys.argv:
        if Image.open(DEST).convert("RGBA").tobytes() != im.tobytes():
            sys.exit("steward_echo drift")
        return
    save(im, DEST)


if __name__ == "__main__":
    main()
