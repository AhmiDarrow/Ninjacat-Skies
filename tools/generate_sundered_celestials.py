"""The Sundered sky's two suns and five moons, painted to sit in the HD panoramas (sundered_day/night).

Two opposing suns (drawn additively, black is nothing):
  sundered_sun_amber.png  the Hearth: the great gold sun, rising in the east
  sundered_sun_azure.png  the Lantern: a smaller blue-white sun, rising in the west against it

Five moons in vanilla's phase layout (4 x 2 frames, frame 0 full, 4 new, 1-3 lit on the left, 5-7 on the right),
drawn with ordinary alpha so a dark limb hides the stars. Nearest first:
  sundered_moon_skein.png   the Skein: huge and near, wound in lilac and cream bands like a ball of yarn
  sundered_moon_rime.png    the Rime: an ice moon inside a thin tilted ring
  sundered_moon_hollow.png  the Hollow: void-black, a violet fire around its rim
  sundered_moon_cinder.png  the Cinder: small, crimson rock under grey ash
  sundered_moon_glint.png   the Glint: far and tiny, a white-gold spark with a halo

Every surface is an equirectangular map wrapped onto a sphere, lit at the frame's phase angle with a regolith
(Lommel-Seeliger) law, relief from the height map, and a halo that follows how much of the face is lit.
"""
import math
import pathlib

import numpy as np
from PIL import Image

SKY = pathlib.Path(__file__).resolve().parents[1] / "mods/ninjacatskies/src/main/resources/assets/ninjacatskies/textures/sky"


def fbm(rng, w, h, octaves=6, base=4, falloff=0.55):
    out = np.zeros((h, w))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        cw, ch = base * 2 ** o, max(2, base * 2 ** o // 2)
        grid = rng.random((ch, cw))
        grid = np.concatenate([grid, grid[:, :1]], axis=1)
        img = Image.fromarray((grid * 255).astype(np.uint8)).resize((w + w // cw, h), Image.BICUBIC)
        out += amp * (np.asarray(img, float)[:, :w] / 255)
        total += amp
        amp *= falloff
    out /= total
    return (out - out.min()) / (np.ptp(out) + 1e-9)


def craters(rng, w, h, count, rmin, rmax):
    height = np.zeros((h, w))
    ys, xs = np.mgrid[0:h, 0:w]
    for _ in range(count):
        r = rmin * (rmax / rmin) ** (rng.random() ** 2.2)
        cx, cy = rng.random() * w, h * (0.12 + 0.76 * rng.random())
        dx = (xs - cx + w / 2) % w - w / 2
        d = np.hypot(dx, ys - cy) / r
        height += (np.where(d < 1, -(1 - d ** 2) * 0.8, 0) + np.exp(-((d - 1.0) / 0.18) ** 2) * 0.35) * min(1.0, r / rmax * 2)
    return height


def surface(kind, seed):
    rng = np.random.default_rng(seed)
    w, h = 1024, 512
    base = fbm(rng, w, h, 7, 4)
    glow = np.zeros((h, w, 3))
    lat = np.linspace(-1, 1, h)[:, None] * np.ones((1, w))
    lon = np.linspace(0, 2 * np.pi, w, endpoint=False)[None, :] * np.ones((h, 1))
    if kind == "skein":
        # wound thread: bands along a tilted axis, each band a bundle of fine strands, crossing layers
        warp = fbm(rng, w, h, 4, 3, 0.5) * 0.35
        a = lat * 0.85 + np.sin(lon) * 0.35 + warp
        b = lat * -0.55 + np.cos(lon * 1 + 1.3) * 0.55 + warp * 0.8
        strands_a = 0.5 + 0.5 * np.sin(a * 130)
        strands_b = 0.5 + 0.5 * np.sin(b * 118)
        layer = fbm(rng, w, h, 3, 2, 0.5) > 0.5
        strands = np.where(layer, strands_a, strands_b)
        band = np.where(layer, np.sin(a * 5), np.sin(b * 6))
        lilac, cream, rose = np.array([0.72, 0.62, 0.86]), np.array([0.94, 0.90, 0.82]), np.array([0.86, 0.60, 0.70])
        mix = (band[..., None] + 1) / 2
        colour = lilac * (1 - mix) + np.where(layer[..., None], cream, rose) * mix
        colour = colour * (0.80 + 0.20 * strands[..., None])
        height = strands * 0.35 + base * 0.2
    elif kind == "rime":
        cracks = 1 - np.abs(fbm(rng, w, h, 5, 9, 0.5) * 2 - 1)
        lines = np.clip((cracks - 0.94) / 0.06, 0, 1)
        colour = np.array([0.80, 0.90, 0.98]) * (0.82 + 0.18 * base[..., None]) - lines[..., None] * np.array([0.30, 0.18, 0.05])
        height = base * 0.3 + craters(rng, w, h, 60, 3, 22) * 0.5
    elif kind == "hollow":
        swirl = fbm(rng, w, h, 5, 5, 0.55)
        colour = np.array([0.07, 0.05, 0.10]) + np.array([0.10, 0.06, 0.16]) * swirl[..., None] ** 2
        height = base * 0.3
    elif kind == "cinder":
        ash = np.clip((fbm(rng, w, h, 5, 4, 0.55) - 0.40) * 3.0, 0, 1)[..., None]
        colour = (np.array([0.66, 0.16, 0.14]) * (1 - ash) + np.array([0.46, 0.44, 0.46]) * ash) * (0.75 + 0.35 * base[..., None])
        height = base * 0.4 + craters(rng, w, h, 300, 2, 30)
    else:   # glint
        colour = np.array([1.0, 0.95, 0.80]) * (0.85 + 0.15 * base[..., None])
        height = base * 0.15
    return np.clip(colour, 0, 1), height, glow


def moon_frame(tex, px, phase, halo_tint, earthshine, disc=0.72, halo_gain=1.0, rim=None, ring=None):
    colour, height, glow = tex
    hh, ww = height.shape
    ss = px * 2
    c = (np.arange(ss) + 0.5) / ss * 2 - 1
    X0, Y0 = np.meshgrid(c, -c)
    X, Y = X0 / disc, Y0 / disc
    r2 = X ** 2 + Y ** 2
    inside = r2 <= 1
    Z = np.sqrt(np.clip(1 - r2, 0, 1))
    lon = np.arctan2(X, Z)
    lat = np.arcsin(np.clip(Y, -1, 1))
    u = ((lon / (2 * np.pi) + 0.5) * ww).astype(int) % ww
    v = np.clip(((0.5 - lat / np.pi) * hh).astype(int), 0, hh - 1)
    gy, gx = np.gradient(height)
    nx, ny, nz = X - 1.1 * gx[v, u], Y + 1.1 * gy[v, u], Z
    n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2) + 1e-9
    theta = math.radians(phase * 45)
    lx, lz = -math.sin(theta), math.cos(theta)
    mu0 = np.clip((nx * lx + nz * lz) / n, 0, 1)
    mu = np.clip(nz / n, 0.05, 1)
    smooth = np.clip((X * lx + Z * lz) * 6 + 0.5, 0, 1)
    light = np.clip(2 * mu0 / (mu0 + mu + 1e-6) * smooth * 0.80, 0, 1.2)
    rgb = colour[v, u] * (light * (0.94 + 0.06 * Z) + earthshine)[..., None] + glow[v, u]
    lit_share = (1 + math.cos(theta)) / 2
    rr = np.sqrt(r2)
    halo = np.exp(-np.clip(rr - 1, 0, None) / 0.10) * (0.10 + 0.45 * lit_share) * halo_gain
    if rim is not None:   # a fire around the limb that burns whatever the phase
        ring_glow = np.exp(-np.abs(rr - 1) / 0.035) * rim[1]
        rgb = rgb + ring_glow[..., None] * np.array(rim[0]) * inside[..., None]
        halo = np.maximum(halo, np.exp(-np.clip(rr - 1, 0, None) / 0.05) * rim[1] * 0.8)
        halo_tint = rim[0]
    alpha = np.where(inside, 1.0, np.clip(halo * 0.55, 0, 1))
    rgb = np.where(inside[..., None], rgb, np.array(halo_tint) * np.clip(0.6 + 0.4 * lit_share, 0, 1))
    if ring is not None:   # a thin tilted ring: in front below the equator line, hidden by the disc above it
        tilt, inner, outer, tint = ring
        ct, st = math.cos(tilt), math.sin(tilt)
        xr, yr = X0 * ct + Y0 * st, -X0 * st + Y0 * ct
        e = np.hypot(xr, yr / 0.22)
        band = (e > inner) & (e < outer)
        grain = 0.85 + 0.15 * np.sin(e * 55)
        front = yr < 0
        show = band & (front | ~inside)
        ra = 0.85 * grain * (0.45 + 0.55 * lit_share)
        rgb = np.where(show[..., None], np.array(tint) * (0.55 + 0.45 * grain[..., None]), rgb)
        alpha = np.where(show, np.maximum(alpha, ra), alpha)
    img = np.concatenate([np.clip(rgb, 0, 1), alpha[..., None]], axis=-1)
    img = img.reshape(px, 2, px, 2, 4).mean(axis=(1, 3))
    return Image.fromarray((img * 255).round().astype(np.uint8), "RGBA")


def atlas(name, kind, seed, px, halo, earthshine, **extra):
    tex = surface(kind, seed)
    sheet = Image.new("RGBA", (px * 4, px * 2), (0, 0, 0, 0))
    for phase in range(8):
        sheet.paste(moon_frame(tex, px, phase, halo, earthshine, **extra), ((phase % 4) * px, (phase // 4) * px))
    sheet.save(SKY / f"sundered_moon_{name}.png")


def sun(name, px, disc, core_tint, limb_tint, corona_tint, corona_width, bloom_gain, rays=0):
    c = (np.arange(px) + 0.5) / px * 2 - 1
    X, Y = np.meshgrid(c, c)
    r = np.hypot(X, Y)
    mu = np.sqrt(np.clip(1 - (r / disc) ** 2, 0, 1))[..., None]
    core = np.array(core_tint) * (0.78 + 0.22 * mu) + (np.array(limb_tint) - np.array(core_tint)) * (1 - mu) ** 2
    edge = np.clip((disc - r) * px / 3 + 0.5, 0, 1)[..., None]
    out = np.clip(r - disc, 0, None)
    corona = np.exp(-out / corona_width)[..., None] * np.array(corona_tint) * 0.75
    if rays:   # a few soft spikes, for the small hard sun
        ang = np.arctan2(Y, X)
        spikes = (np.abs(np.cos(ang * rays / 2)) ** 40)[..., None] * np.exp(-out / 0.25)[..., None] * np.array(corona_tint) * 0.35
        corona = corona + spikes
    bloom = np.exp(-out / 0.22)[..., None] * np.array(corona_tint) * bloom_gain
    fade = np.clip((1 - r) / 0.12, 0, 1)[..., None]
    rgb = (core * edge + (corona + bloom) * (1 - edge)) * fade
    img = np.concatenate([np.clip(rgb, 0, 1), np.ones((px, px, 1))], axis=-1)
    Image.fromarray((img * 255).round().astype(np.uint8), "RGBA").save(SKY / f"sundered_sun_{name}.png")


def main():
    sun("amber", 512, 0.30, (1.0, 0.95, 0.82), (1.0, 0.70, 0.36), (1.0, 0.72, 0.36), 0.06, 0.20)
    sun("azure", 512, 0.22, (0.94, 0.98, 1.0), (0.62, 0.80, 1.0), (0.55, 0.78, 1.0), 0.035, 0.12, rays=6)
    atlas("skein", "skein", 7001, 256, (0.82, 0.74, 0.95), 0.08)
    atlas("rime", "rime", 7103, 256, (0.70, 0.85, 1.0), 0.07, disc=0.46,
          ring=(math.radians(-18), 0.62, 0.93, (0.78, 0.86, 0.96)))
    atlas("hollow", "hollow", 7207, 192, (0.55, 0.30, 0.95), 0.10, rim=((0.62, 0.30, 1.0), 0.9))
    atlas("cinder", "cinder", 7309, 128, (0.95, 0.40, 0.32), 0.06)
    atlas("glint", "glint", 7411, 64, (1.0, 0.92, 0.70), 0.08, disc=0.40, halo_gain=1.8)
    for p in SKY.glob("sundered_*_*.png"):
        (SKY / (p.name + ".mcmeta")).write_text('{"texture": {"blur": true, "clamp": true}}', encoding="utf-8")
    print("sundered suns and moons written")


if __name__ == "__main__":
    main()
