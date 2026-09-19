"""Driftwrecks pixel-art toolkit: 32x32 canvas, hue-shifted ramps, lit shapes, tinted outline.

Style target (family STYLE_TARGET): native 32 px, hard alpha (0/255 only), 1 px outline tinted toward the item's own
hue from ink #111a22, light from the top-left, flat fills in 4-5 tone ramps (cool shadows, warm highlights), at most a
1-2 px specular. Used by generate_driftwrecks_art.py and its driftwrecks_art_* modules.
"""
from __future__ import annotations

import colorsys
import math
from pathlib import Path

from PIL import Image, ImageDraw

from art_tribe_glyphs import TRIBE_COLORS, draw_glyph

N = 32
INK = (0x11, 0x1a, 0x22)


# ------------------------------------------------------------------ colour

def hexc(h):
    return ((h >> 16) & 255, (h >> 8) & 255, h & 255)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _hue_toward(h, target, amount):
    d = ((target - h + 0.5) % 1.0) - 0.5
    return (h + max(-amount, min(amount, d))) % 1.0


def tone(c, v=1.0, s=0.0, hue=0.0):
    """Scale value by v, add s to saturation, rotate hue toward cool (hue<0) or warm (hue>0) by |hue| turns."""
    h, sa, va = colorsys.rgb_to_hsv(*(x / 255 for x in c[:3]))
    if hue < 0:
        h = _hue_toward(h, 0.64, -hue)   # toward blue-violet
    elif hue > 0:
        h = _hue_toward(h, 0.12, hue)    # toward warm yellow
    sa = max(0.0, min(1.0, sa + s))
    va = max(0.0, min(1.0, va * v))
    r, g, b = colorsys.hsv_to_rgb(h, sa, va)
    return (int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5))


class Ramp(tuple):
    """Five tones: deep, dark, base, light, hi (index 0..4)."""
    deep = property(lambda s: s[0])
    dark = property(lambda s: s[1])
    base = property(lambda s: s[2])
    light = property(lambda s: s[3])
    hi = property(lambda s: s[4])


def ramp(c, spread=1.0):
    c = tuple(c[:3])
    return Ramp((tone(c, 1 - 0.46 * spread, 0.10, -0.05), tone(c, 1 - 0.24 * spread, 0.06, -0.025), c,
                 tone(mix(c, (255, 255, 255), 0.18 * spread), 1.12, -0.06, 0.02),
                 tone(mix(c, (255, 250, 230), 0.45 * spread), 1.2, -0.14, 0.035)))


# the Driftwrecks materials
TEAL = ramp(hexc(0x3a9e98))        # tether thread
LOOM = ramp(hexc(0x62d1c9))        # bright thread / glow
GOLD = ramp(hexc(0xd2a54a))        # gold seam, brass
COPPER = ramp(hexc(0xc08a4e))
WOOD = ramp(hexc(0x7a5238))
DRIFT = ramp(hexc(0x5e4a3c))       # grey-brown driftwood
BONE = ramp(hexc(0xd8ccaa))
PAPER = ramp(hexc(0xe6dcc0))
SLATE = ramp(hexc(0x55667a))
IRON = ramp(hexc(0x7d8894))
RIFT = ramp(hexc(0x7a4bb0))
CLAY = ramp(hexc(0xa8643e))
LEAF = ramp(hexc(0x5a9a4a))
RED = ramp(hexc(0xb0443a))
WAX = ramp(hexc(0xe0b24a))


def tribe_ramp(tribe):
    return ramp(TRIBE_COLORS[tribe])


# ------------------------------------------------------------------ canvas

class Px:
    def __init__(self, size=N):
        self.n = size
        self.im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.px = self.im.load()
        self.d = ImageDraw.Draw(self.im)

    # -- raw pixels
    def p(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.n and 0 <= y < self.n:
            self.px[x, y] = tuple(c[:3]) + (255,)

    def clear(self, x, y):
        if 0 <= x < self.n and 0 <= y < self.n:
            self.px[x, y] = (0, 0, 0, 0)

    def get(self, x, y):
        if 0 <= x < self.n and 0 <= y < self.n:
            return self.px[x, y]
        return (0, 0, 0, 0)

    def on(self, x, y):
        return self.get(x, y)[3] > 0

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.p(x, y, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = y0 + (y1 - y0) * i / n
            for a in range(w):
                for b in range(w):
                    self.p(math.floor(x + 0.5) + a, math.floor(y + 0.5) + b, c)

    def poly(self, pts, c):
        self.d.polygon([tuple(p) for p in pts], fill=tuple(c[:3]) + (255,))

    def pts(self, cells, c):
        for x, y in cells:
            self.p(x, y, c)

    # -- lit shapes: a set of cells shaded by a ramp with top-left light
    def fill(self, cells, R, rim=True, spec=None):
        cells = set(cells)
        if not isinstance(R, Ramp):
            self.pts(cells, R)
            return cells
        for (x, y) in cells:
            c = R.base
            if rim:
                if (x, y + 1) not in cells or (x + 1, y) not in cells:
                    c = R.dark
                if (x - 1, y) not in cells or (x, y - 1) not in cells:
                    c = R.light
            self.p(x, y, c)
        if spec:
            for s in spec:
                self.p(*s, R.hi)
        return cells

    def box(self, x0, y0, x1, y1, R, rim=True):
        return self.fill(rect_cells(x0, y0, x1, y1), R, rim)

    def ball(self, cx, cy, rx, ry=None, R=None, spec=True, bands=(0.55, 0.05, -0.55)):
        """Ellipse shaded in flat bands by its normal against a top-left light."""
        ry = rx if ry is None else ry
        cells = ellipse_cells(cx, cy, rx, ry)
        for (x, y) in cells:
            nx, ny = (x + 0.5 - cx) / max(rx, 0.5), (y + 0.5 - cy) / max(ry, 0.5)
            l = -(nx + ny) * 0.72
            c = R.light if l > bands[0] else R.base if l > bands[1] else R.dark if l > bands[2] else R.deep
            self.p(x, y, c)
        if spec:
            self.p(int(cx - rx * 0.45), int(cy - ry * 0.5), R.hi)
        return cells

    def cyl(self, x0, y0, x1, y1, R):
        """Vertical cylinder: banded columns, light at the left third."""
        w = x1 - x0 + 1
        for x in range(x0, x1 + 1):
            t = (x - x0) / max(1, w - 1)
            c = R.light if t < 0.3 else R.base if t < 0.65 else R.dark if t < 0.9 else R.deep
            for y in range(y0, y1 + 1):
                self.p(x, y, c)
        return rect_cells(x0, y0, x1, y1)

    def rod(self, x0, y0, x1, y1, R, w=2):
        """A diagonal/straight stick w px wide with a light upper edge and dark lower edge."""
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            for k in range(w):
                c = R.light if k == 0 else R.dark if k == w - 1 else R.base
                if abs(x1 - x0) > abs(y1 - y0):
                    self.p(x, y + k, c)
                else:
                    self.p(x + k, y, c)

    def solid(self, cells, R, axis="x", spec=None, edge=True):
        """Shade any silhouette as a rounded solid: tone by position across each run (left/top light,
        right/bottom dark), plus a lighter top-left edge and darker bottom-right edge. axis='y' shades along
        columns (for horizontal forms)."""
        cells = set(cells)
        for (x, y) in cells:
            if axis == "x":
                a = 0
                while (x - a - 1, y) in cells:
                    a += 1
                b = 0
                while (x + b + 1, y) in cells:
                    b += 1
            else:
                a = 0
                while (x, y - a - 1) in cells:
                    a += 1
                b = 0
                while (x, y + b + 1) in cells:
                    b += 1
            w = a + b + 1
            t = a / max(1, w - 1)
            i = 3 if t < 0.28 else 2 if t < 0.68 else 1 if (t < 0.93 or w < 4) else 0
            if edge:
                if (x, y - 1) not in cells or (x - 1, y) not in cells and axis == "y":
                    i = min(4 if w >= 5 and t < 0.28 else 3, i + 1)
                if (x, y + 1) not in cells and i > 0:
                    i -= 1
            self.p(x, y, R[i])
        for s in spec or ():
            self.p(*s, R.hi)
        return cells

    def glyph(self, tribe, x, y, c, scale=1, shadow=None):
        draw_glyph(self.im, tribe, x, y, c, scale=scale, shadow=shadow)

    # -- outline + finish
    def outline(self, ink=INK, tint=0.3, diagonal=False):
        """1 px outline on every transparent cell touching the art, tinted toward the neighbour's hue."""
        src = self.im.copy().load()
        nb = ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (-1, -1), (1, -1), (-1, 1)) if diagonal else ())
        todo = []
        for y in range(self.n):
            for x in range(self.n):
                if src[x, y][3]:
                    continue
                cols = [src[x + dx, y + dy] for dx, dy in nb
                        if 0 <= x + dx < self.n and 0 <= y + dy < self.n and src[x + dx, y + dy][3]]
                if cols:
                    avg = tuple(sum(c[i] for c in cols) // len(cols) for i in range(3))
                    todo.append((x, y, mix(ink, tone(avg, 0.55, 0.15, -0.04), tint)))
        for x, y, c in todo:
            self.p(x, y, c)
        return self

    def harden(self):
        """Force hard alpha (0 or 255)."""
        for y in range(self.n):
            for x in range(self.n):
                r, g, b, a = self.px[x, y]
                self.px[x, y] = (r, g, b, 255) if a >= 128 else (0, 0, 0, 0)
        return self

    def save(self, path: Path):
        self.harden()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.im.save(path)


# ------------------------------------------------------------------ cell sets

def rect_cells(x0, y0, x1, y1):
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def ellipse_cells(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry
    out = set()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                out.add((x, y))
    return out


def ring_cells(cx, cy, r_out, r_in):
    return ellipse_cells(cx, cy, r_out) - ellipse_cells(cx, cy, r_in)


def poly_cells(pts):
    im = Image.new("L", (N, N), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
    px = im.load()
    return {(x, y) for y in range(N) for x in range(N) if px[x, y]}


def line_cells(x0, y0, x1, y1, w=1):
    out = set()
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = math.floor(x0 + (x1 - x0) * i / n + 0.5)
        y = math.floor(y0 + (y1 - y0) * i / n + 0.5)
        for a in range(w):
            for b in range(w):
                out.add((x + a, y + b))
    return out
