#!/usr/bin/env python3
"""Pixel-quantise baked Guardian / Remnant textures so the bosses sit with the 32px item and block art.

    python tools/pixel_quantise_boss.py                     # every shipped Guardian and Remnant texture
    python tools/pixel_quantise_boss.py --only thornmother  # one model (Guardian id or Remnant strand)
    python tools/pixel_quantise_boss.py --force             # re-run on textures that are already quantised

Called by INTERNAL/guardians/bosses/pipeline/export_boss.py (and so remnant_export.py, which reuses its export())
straight after the .ncgb is written, as `python tools/pixel_quantise_boss.py --force --pair <png> <emit png> <ncgb>`
in a subprocess (Blender's bundled Python has no Pillow); also runnable on the shipped PNGs as a post-process.

Per model (<id>.png albedo + <id>_emit.png emissive, both sampled through the textured part's 0..1 UVs):
  1. Rasterise the textured part's UV triangles from the .ncgb to find the texels the mesh actually samples, and
     flood the colour of those texels outward so downsampling never pulls in the black bake background.
  2. Measure texel density (texels per block along a face) from 3D area vs UV area and pick the power-of-two
     downsample that lands closest to 24 px per block (the 16-32 px range of the item/block art).
  3. Box-downsample, then quantise to a small palette (albedo 20 colours, emissive 8 + black) found by k-means in
     OKLab. The palette is hue-shifted like the hand art (shadows cooler, highlights warmer), chroma is capped so
     nothing goes neon, the darkest tone is pulled onto the style ink (#111a22), and centres close to a Living
     Lattice colour snap onto it. No dithering; a 3x3 majority pass removes the Cycles sampling speckle.
  4. Scale back up with nearest-neighbour to the original size, so UVs, dimensions and the renderer are untouched.
Meshes (.ncgb) are never modified.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
GUARDIANS = ROOT / "mods/guardians/src/main/resources/assets/guardians"
DRIFT = ROOT / "mods/driftwrecks/src/main/resources/assets/driftwrecks"

SMOOTH_RADIUS = 1.2            # texels (on the downsampled grid) of pre-quantise smoothing
TARGET_DENSITY = 24.0          # texels per block along a face
ALBEDO_COLOURS = 20
EMIT_COLOURS = 8
HUE_SHIFT_DEG = 7.0            # ramp ends rotate at most this far toward blue (shadow) / amber (highlight)
MAX_CHROMA = 0.13              # OKLab chroma cap (muted jewel tones, no neon)
INK = (0x11, 0x1A, 0x22)
STYLE = [  # Living Lattice palette (tribal-power/tools/art/lattice.py) + the Core ink
    INK, (0x3E, 0x28, 0x1F), (0x5A, 0x3B, 0x2E), (0x7A, 0x51, 0x38), (0x2A, 0x36, 0x3F), (0x3A, 0x4A, 0x55),
    (0x55, 0x66, 0x72), (0x74, 0x86, 0x92), (0x8A, 0x5E, 0x30), (0xC0, 0x8A, 0x4E), (0xE3, 0xB1, 0x71),
    (0x9A, 0x74, 0x2E), (0xD2, 0xA5, 0x4A), (0xF1, 0xD0, 0x82), (0x2F, 0x8A, 0x86), (0x62, 0xD1, 0xC9),
    (0xB0, 0xA5, 0x88), (0xE1, 0xD9, 0xBD), (0x1C, 0x1E, 0x22), (0x2A, 0x2C, 0x30), (0x45, 0x47, 0x4C),
]
MARKER = "ncs-pixel-quantised"


# ------------------------------------------------------------------ colour space
def _lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _unlin(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255.0


def to_oklab(rgb):
    r, g, b = [_lin(rgb[..., i].astype(np.float64)) for i in range(3)]
    l = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return np.stack([0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
                     1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                     0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s], -1)


def from_oklab(lab):
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = np.stack([4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
                    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                    -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s], -1)
    return np.round(_unlin(rgb)).astype(np.uint8)


# ------------------------------------------------------------------ ncgb
def read_textured_tris(ncgb: Path):
    """[(xyz(3,3), uv(3,2))] for every triangle of the textured part(s)."""
    b = ncgb.read_bytes(); o = 8
    assert b[:4] == b"NCGB", ncgb

    def u32():
        nonlocal o; v = struct.unpack_from("<I", b, o)[0]; o += 4; return v

    def s():
        nonlocal o; n = struct.unpack_from("<H", b, o)[0]; o += 2 + n
    for _ in range(u32()):
        s(); o += 4
    tris = []
    for _ in range(u32()):
        s(); textured = b[o]; o += 1; nv = u32()
        raw = np.frombuffer(b, dtype=np.uint8, count=nv * 62, offset=o).reshape(nv, 62); o += nv * 62
        f = raw[:, :32].copy().view("<f4")
        nt = u32(); idx = np.frombuffer(b, dtype="<u4", count=nt * 3, offset=o).reshape(nt, 3); o += nt * 12
        if textured:
            tris.append((f[:, 0:3][idx], f[:, 6:8][idx]))
    if not tris:
        return None, None
    return np.concatenate([t[0] for t in tris]), np.concatenate([t[1] for t in tris])


def uv_mask_and_density(ncgb: Path, size):
    xyz, uv = read_textured_tris(ncgb)
    w, h = size
    if xyz is None:
        return None, None
    a3 = 0.5 * np.linalg.norm(np.cross(xyz[:, 1] - xyz[:, 0], xyz[:, 2] - xyz[:, 0]), axis=1).sum()
    e1, e2 = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
    a2 = 0.5 * np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]).sum()
    density = w * np.sqrt(a2 / a3) if a3 > 0 else None
    mask = Image.new("L", size, 0); d = ImageDraw.Draw(mask)
    for t in uv:
        d.polygon([(float(p[0]) * w, float(p[1]) * h) for p in t], fill=255, outline=255)
    return np.array(mask) > 0, density


# ------------------------------------------------------------------ image steps
def flood(img, mask, rings=64):
    """Push covered colours outward into uncovered texels (nearest covered neighbour, 4-connected rings)."""
    img = img.astype(np.float64).copy(); m = mask.copy()
    for _ in range(rings):
        if m.all():
            break
        acc = np.zeros_like(img); cnt = np.zeros(m.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sm = np.roll(m, (dy, dx), (0, 1)); si = np.roll(img, (dy, dx), (0, 1))
            acc[sm] += si[sm]; cnt[sm] += 1
        grow = (~m) & (cnt > 0)
        if not grow.any():
            break
        img[grow] = acc[grow] / cnt[grow][:, None]; m |= grow
    return img


def box_down(img, f):
    h, w = img.shape[:2]
    return img.reshape(h // f, f, w // f, f, -1).mean(axis=(1, 3))


def kmeans(x, k, iters=24):
    """Deterministic k-means (farthest-point init on lightness-sorted data)."""
    order = np.argsort(x[:, 0]); x = x[order]
    k = min(k, len(np.unique(np.round(x, 3), axis=0)))
    cent = [x[len(x) // 2]]
    dist = np.linalg.norm(x - cent[0], axis=1)
    for _ in range(1, k):
        cent.append(x[int(np.argmax(dist))]); dist = np.minimum(dist, np.linalg.norm(x - cent[-1], axis=1))
    cent = np.array(cent)
    for _ in range(iters):
        lab = np.argmin(((x[:, None, :] - cent[None]) ** 2).sum(-1), axis=1)
        new = np.array([x[lab == i].mean(0) if (lab == i).any() else cent[i] for i in range(k)])
        if np.allclose(new, cent, atol=1e-5):
            break
        cent = new
    return cent


def style_palette(cent, emissive=False):
    """Hue-shift the k-means centres into ramps: shadows cooler, highlights warmer; cap chroma; snap to style."""
    out = cent.copy()
    L = out[:, 0]; lo, hi = L.min(), L.max(); mid = (lo + hi) / 2
    a, b = out[:, 1], out[:, 2]
    C = np.hypot(a, b); H = np.arctan2(b, a)
    t = (L - mid) / max(hi - lo, 1e-6) * 2          # -1 darkest .. +1 lightest
    cool, warm = np.radians(255.0), np.radians(75.0)  # OKLab hue of blue-ish / amber
    tgt = np.where(t < 0, cool, warm)
    dh = np.angle(np.exp(1j * (tgt - H)))
    r = np.radians(HUE_SHIFT_DEG)
    H = H + np.clip(dh, -r, r) * np.clip(np.abs(t), 0, 1)
    C = np.minimum(C * (1 - np.where(t < 0, 0.3, 0.1) * np.abs(t)), 0.22 if emissive else MAX_CHROMA)
    out[:, 1], out[:, 2] = C * np.cos(H), C * np.sin(H)
    style = to_oklab(np.array(STYLE, dtype=np.float64))
    for i in range(len(out)):
        d = np.linalg.norm(style - out[i], axis=1); j = int(np.argmin(d))
        if d[j] < 0.02:
            out[i] = style[j]
    if not emissive:  # darkest tone sits on the style ink
        i = int(np.argmin(out[:, 0]))
        if out[i, 0] < 0.3:
            out[i] = to_oklab(np.array([INK], dtype=np.float64))[0]
    return out


def majority(idx, mask):
    """3x3 mode filter on palette indices (only replaces isolated texels: < 2 same neighbours)."""
    h, w = idx.shape; pad = np.pad(idx, 1, mode="edge")
    nb = np.stack([pad[1 + dy:h + 1 + dy, 1 + dx:w + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if (dy, dx) != (0, 0)])
    same = (nb == idx[None]).sum(0)
    out = idx.copy()
    ys, xs = np.nonzero((same < 2) & mask)
    for y, x in zip(ys, xs):
        vals, counts = np.unique(nb[:, y, x], return_counts=True); out[y, x] = vals[np.argmax(counts)]
    return out


def quantise(rgb, mask, f, colours, emissive=False):
    h, w = rgb.shape[:2]
    if emissive:  # glow lines are 1-2 texels wide: keep the brightest texel of each cell instead of averaging
        h2, w2 = h // f, w // f
        cells = rgb.reshape(h2, f, w2, f, 3).transpose(0, 2, 1, 3, 4).reshape(h2, w2, f * f, 3).astype(np.float64)
        pick = cells.sum(-1).argmax(-1)
        small = np.take_along_axis(cells, pick[..., None, None], 2)[:, :, 0]
    else:  # average each cell, then soften the Cycles sampling grain so quantising yields flat patches
        small = box_down(flood(rgb, mask, rings=2 * f + 4), f)
        small = np.array(Image.fromarray(np.round(small).astype(np.uint8), "RGB")
                         .filter(ImageFilter.GaussianBlur(SMOOTH_RADIUS)), dtype=np.float64)
    smask = box_down(mask[..., None].astype(np.float64), f)[..., 0] > 0.25
    lab = to_oklab(small)
    flat = lab[smask] if smask.any() else lab.reshape(-1, 3)
    if emissive:
        lit = flat[flat[:, 0] > 0.12]
        k = kmeans(lit[:: max(1, len(lit) // 20000)], colours) if len(lit) else np.zeros((1, 3))
        raw = np.vstack([np.zeros((1, 3)), k])
        cent = np.vstack([np.zeros((1, 3)), style_palette(k, emissive=True)])
    else:
        raw = kmeans(flat[:: max(1, len(flat) // 20000)], colours); cent = style_palette(raw)
    idx = np.argmin(((lab[..., None, :] - raw[None, None]) ** 2).sum(-1), axis=-1)
    if emissive:
        idx[lab[..., 0] <= 0.12] = 0
    if not emissive:
        for _ in range(2):
            idx = majority(idx, smask)
    pal = from_oklab(cent)
    if emissive:
        pal[0] = 0
    out = pal[idx]
    # keep a 2-texel bleed ring round every UV island (seam safety); everything the mesh never samples goes flat
    ring = smask.copy()
    for _ in range(2):
        ring = ring | np.roll(ring, 1, 0) | np.roll(ring, -1, 0) | np.roll(ring, 1, 1) | np.roll(ring, -1, 1)
    out[~ring] = 0 if emissive else INK
    return np.repeat(np.repeat(out, f, 0), f, 1)[:h, :w], len(pal)


def already_done(path: Path):
    with Image.open(path) as im:
        return im.info.get("Comment") == MARKER or im.info.get(MARKER) == "1"


def save(arr, path: Path):
    from PIL import PngImagePlugin
    info = PngImagePlugin.PngInfo(); info.add_text(MARKER, "1")
    Image.fromarray(arr.astype(np.uint8), "RGB").save(path, pnginfo=info, optimize=True)


def quantise_pair(albedo: Path, emit: Path | None, ncgb: Path, force=False, log=print):
    """Quantise <id>.png (+ <id>_emit.png) in place. Returns the chosen downsample factor."""
    albedo, ncgb = Path(albedo), Path(ncgb)
    if not force and already_done(albedo):
        log(f"skip {albedo.name} (already quantised)"); return None
    rgb = np.array(Image.open(albedo).convert("RGB"))
    h, w = rgb.shape[:2]
    mask, density = uv_mask_and_density(ncgb, (w, h))
    if mask is None:
        mask = rgb.max(-1) > 0; density = None
    f = 1
    if density:
        opts = [c for c in (1, 2, 4, 8, 16) if w % c == 0 and h % c == 0]
        f = min(opts, key=lambda c: abs(np.log(density / c / TARGET_DENSITY)))
    out, n = quantise(rgb, mask, f, ALBEDO_COLOURS)
    save(out, albedo)
    msg = f"{albedo.name}: {density or 0:.0f} px/block -> /{f} = {(density or 0) / f:.0f} px/block, {n} colours"
    if emit and Path(emit).exists():
        e = np.array(Image.open(emit).convert("RGB"))
        eo, en = quantise(e, mask, f, EMIT_COLOURS, emissive=True)
        save(eo, Path(emit)); msg += f"; emit {en} colours"
    log(msg)
    return f


def shipped():
    for p in sorted((GUARDIANS / "guardian").glob("*.ncgb")):
        yield p.stem, GUARDIANS / "textures/guardian" / f"{p.stem}.png", GUARDIANS / "textures/guardian" / f"{p.stem}_emit.png", p
    for p in sorted((DRIFT / "remnant").glob("*.ncgb")):
        yield p.stem, DRIFT / "textures/remnant" / f"{p.stem}.png", DRIFT / "textures/remnant" / f"{p.stem}_emit.png", p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="comma-separated ids")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--pair", nargs=3, metavar=("ALBEDO", "EMIT", "NCGB"),
                    help="quantise one freshly baked texture pair (what the Blender exporters call)")
    a = ap.parse_args()
    if a.pair:
        quantise_pair(Path(a.pair[0]), Path(a.pair[1]), Path(a.pair[2]), force=a.force)
        return
    only = set(a.only.split(",")) if a.only else None
    for name, alb, emit, ncgb in shipped():
        if only and name not in only:
            continue
        if alb.exists():
            quantise_pair(alb, emit, ncgb, force=a.force)


if __name__ == "__main__":
    main()
