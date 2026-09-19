#!/usr/bin/env python3
"""Synthesised Driftwreck sounds — original, no samples. Same approach as tools/generate_sounds_loom.py.

    python tools/generate_sounds_driftwrecks.py && python tools/generate_driftwrecks_data.py

Writes assets/driftwrecks/sounds/<group>/<name>.ogg (numpy WAV -> ffmpeg Vorbis). The data generator then points
sounds.json at these files instead of the vanilla placeholders.
  driftwreck/arrive      long wood-and-rope creak, distant, as the piece is pulled in
  driftwreck/creak       one strain of old timber (loops quietly from half-life)
  driftwreck/crumble     a rim block letting go into the void
  driftwreck/warn_final  low groan under a thread pulled tight
  driftwreck/unravel     thread snap, then a rising shimmer as the blocks dissolve
  driftwreck/whisper     breathy, formant-shaped air for Haunted wrecks
  tether/lay             a soft thread tick per block laid
  tether/catch           the rope-tighten jerk of the thread catch
  rift/open              a reversed swell into a chime
  keepsake/found         a small warm chime
  atlas/page             paper flick and a tiny bell
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 44100
OUT = ROOT / "mods/driftwrecks/src/main/resources/assets/driftwrecks/sounds"
RNG = np.random.default_rng(1337)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.clip(t / max(attack, 1e-4), 0, 1) * np.exp(-t / max(decay, 1e-4))


def tone(freq, seconds, attack=0.005, decay=0.3, harmonics=((1, 1.0),)):
    n = int(seconds * SR); t = np.arange(n) / SR
    out = sum(a * np.sin(2 * np.pi * freq * m * t) for m, a in harmonics)
    return out * env(n, attack, decay)


def glide(f0, f1, seconds, attack=0.01, decay=1.0, harmonics=((1, 1.0),)):
    n = int(seconds * SR); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / seconds)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = sum(a * np.sin(ph * m) for m, a in harmonics)
    return out * env(n, attack, decay)


def noise(seconds, lowpass=1):
    x = RNG.standard_normal(int(seconds * SR))
    if lowpass > 1:
        x = np.convolve(x, np.ones(lowpass) / lowpass, mode="same")
    return x


def bandpass(x, center, width):
    """A cheap resonant band: FFT mask."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= np.exp(-((f - center) / width) ** 2)
    return np.fft.irfft(X, len(x))


def mix(*parts, offsets=None):
    offsets = offsets or [0] * len(parts)
    n = max(len(p) + o for p, o in zip(parts, offsets))
    out = np.zeros(n)
    for p, o in zip(parts, offsets):
        out[o:o + len(p)] += p
    return out


def normalize(x, peak=0.85):
    return x / (np.max(np.abs(x)) or 1.0) * peak


def tail(x, seconds=0.8, wet=0.3):
    """A short diffuse tail: a few decaying, lowpassed echoes (distance, not a room)."""
    out = np.concatenate([x, np.zeros(int(seconds * SR))])
    for k, d in enumerate((0.037, 0.061, 0.089, 0.131, 0.197)):
        o = int(d * SR)
        echo = np.convolve(x, np.ones(8) / 8, mode="same") * wet * (0.7 ** k)
        out[o:o + len(echo)] += echo
    return out


def creak(seconds, rate0=18, rate1=40, pitch=220):
    """Stick-slip friction: a train of tiny resonant clicks whose rate speeds up, like timber under load."""
    n = int(seconds * SR); out = np.zeros(n)
    t = 0.0
    while t < seconds:
        frac = t / seconds
        rate = rate0 + (rate1 - rate0) * frac
        i = int(t * SR)
        click = tone(pitch * (0.9 + 0.2 * RNG.random()), 0.03, 0.0005, 0.006, harmonics=((1, 1.0), (2.3, 0.4), (3.9, 0.15)))
        amp = np.sin(np.pi * frac) ** 0.6 * (0.6 + 0.4 * RNG.random())
        seg = click[: max(0, min(len(click), n - i))] * amp
        out[i:i + len(seg)] += seg
        t += 1.0 / rate * (0.7 + 0.6 * RNG.random())
    return out


def write(path: str, data: np.ndarray) -> None:
    ogg = OUT / f"{path}.ogg"
    ogg.parent.mkdir(parents=True, exist_ok=True)
    wav = ogg.with_suffix(".wav")
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "4", str(ogg)], check=True)
    wav.unlink()
    print("wrote", ogg.relative_to(ROOT))


def main():
    # arrive: rope strain gliding under a slow timber creak, far away
    rope = glide(95, 140, 4.5, 0.6, 3.0, harmonics=((1, 1.0), (2.01, 0.5), (3.02, 0.2)))
    wood = creak(4.5, 10, 26, 180)
    air = bandpass(noise(4.5), 300, 180) * np.hanning(int(4.5 * SR)) * 0.25
    write("driftwreck/arrive", normalize(tail(mix(rope * 0.5, wood, air), 1.2, 0.35), 0.8))
    write("driftwreck/creak", normalize(tail(creak(1.4, 14, 34, 240), 0.4), 0.7))
    # crumble: a few gravel bursts falling away (lowpass deepening)
    parts = [bandpass(noise(0.18), 900 - k * 120, 500) * np.hanning(int(0.18 * SR)) for k in range(5)]
    write("driftwreck/crumble", normalize(mix(*parts, offsets=[int(k * 0.09 * SR) for k in range(5)]), 0.75))
    groan = glide(70, 52, 2.0, 0.2, 1.4, harmonics=((1, 1.0), (1.5, 0.3), (2.02, 0.35)))
    pull = glide(420, 690, 1.6, 0.4, 2.0, harmonics=((1, 0.5), (2, 0.15)))
    write("driftwreck/warn_final", normalize(tail(mix(groan, pull * 0.35, offsets=[0, int(0.3 * SR)]), 0.8), 0.8))
    # unravel: snap, then nine rising partials
    snap = bandpass(noise(0.05), 2500, 1800) * np.exp(-np.arange(int(0.05 * SR)) / (0.008 * SR))
    shimmer = mix(*[tone(440 * 2 ** (k / 6), 1.4, 0.02, 0.5, harmonics=((1, 1.0), (2, 0.3))) * 0.3 for k in range(9)],
                  offsets=[int((0.08 + k * 0.12) * SR) for k in range(9)])
    write("driftwreck/unravel", normalize(tail(mix(snap * 1.5, shimmer), 0.9, 0.35), 0.85))
    # whisper: breathy noise through moving formants
    w = noise(3.0)
    wh = sum(bandpass(w, f, 120) * (0.5 + 0.5 * np.sin(np.linspace(0, 6 + k, len(w)))) for k, f in enumerate((700, 1150, 2400)))
    write("driftwreck/whisper", normalize(wh * np.hanning(len(wh)), 0.5))
    tick = mix(bandpass(noise(0.04), 1800, 900) * np.exp(-np.arange(int(0.04 * SR)) / (0.006 * SR)), tone(880, 0.08, 0.001, 0.02) * 0.2)
    write("tether/lay", normalize(tick, 0.6))
    twang = glide(160, 240, 0.35, 0.002, 0.18, harmonics=((1, 1.0), (2, 0.5), (3, 0.25)))
    thud = tone(70, 0.25, 0.002, 0.08, harmonics=((1, 1.0), (2.2, 0.3)))
    write("tether/catch", normalize(mix(twang, thud), 0.85))
    swell = glide(200, 600, 1.8, 1.4, 5.0, harmonics=((1, 1.0), (1.5, 0.4), (2, 0.3)))
    swell *= np.linspace(0, 1, len(swell)) ** 2
    chime = tone(880, 1.2, 0.002, 0.45, harmonics=((1, 1.0), (2.76, 0.4), (5.4, 0.15)))
    write("rift/open", normalize(tail(mix(swell, chime * 0.6, offsets=[0, int(1.7 * SR)]), 0.8), 0.85))
    found = mix(tone(660, 1.0, 0.002, 0.4, harmonics=((1, 1.0), (2.76, 0.35))), tone(990, 0.9, 0.002, 0.35, harmonics=((1, 0.6),)), offsets=[0, int(0.12 * SR)])
    write("keepsake/found", normalize(tail(found, 0.5), 0.7))
    page = bandpass(noise(0.25), 3200, 2000) * np.hanning(int(0.25 * SR))
    bell = tone(1320, 0.5, 0.002, 0.2, harmonics=((1, 1.0), (2.76, 0.3)))
    write("atlas/page", normalize(mix(page, bell * 0.3, offsets=[0, int(0.2 * SR)]), 0.6))


if __name__ == "__main__":
    main()
