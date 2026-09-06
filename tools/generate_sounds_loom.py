#!/usr/bin/env python3
"""Synthesised Loom sounds for Ninjacat Skies — original, no samples.

Writes WAV with numpy, encodes to OGG Vorbis with ffmpeg. Sounds:
  strand_chime  — loom shuttle clack + a bell partial (pitched per Strand in code)
  post_seat     — wooden knock with a short thread "zip"
  loom_hum      — 4 s low wooden drone with slow beating, loops cleanly
  reweave       — 6 s swell: nine bell partials stacking into a chord, then a shuttle run
  page          — soft paper flick

Also the Voidloom pair:
  loomframe_sift — shuttle clack + grit hiss
  barrel_settle  — wet wooden thunk
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 44100


def env(n: int, attack: float, decay: float, sr: int = SR) -> np.ndarray:
    t = np.arange(n) / sr
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = np.exp(-t / max(decay, 1e-4))
    return a * d


def tone(freq: float, seconds: float, attack=0.005, decay=0.3, harmonics=((1, 1.0),), sr: int = SR) -> np.ndarray:
    n = int(seconds * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    for mult, amp in harmonics:
        out += amp * np.sin(2 * np.pi * freq * mult * t)
    return out * env(n, attack, decay, sr)


def noise(seconds: float, attack=0.001, decay=0.05, lowpass=0.0, sr: int = SR) -> np.ndarray:
    n = int(seconds * sr)
    rng = np.random.default_rng(7)
    x = rng.standard_normal(n)
    if lowpass > 0:
        k = int(lowpass)
        x = np.convolve(x, np.ones(k) / k, mode="same")
    return x * env(n, attack, decay, sr)


def clack(sr: int = SR) -> np.ndarray:
    """A wooden shuttle hitting the frame: short filtered noise burst + a low wood resonance."""
    body = noise(0.08, 0.001, 0.02, lowpass=6, sr=sr) * 0.9
    wood = tone(180, 0.12, 0.001, 0.04, harmonics=((1, 1.0), (2.7, 0.35)), sr=sr) * 0.8
    return mix(body, wood)


def mix(*parts: np.ndarray, offsets=None) -> np.ndarray:
    offsets = offsets or [0] * len(parts)
    n = max(len(p) + o for p, o in zip(parts, offsets))
    out = np.zeros(n)
    for p, o in zip(parts, offsets):
        out[o:o + len(p)] += p
    return out


def normalize(x: np.ndarray, peak=0.85) -> np.ndarray:
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def write(name: str, modid: str, data: np.ndarray, sr: int = SR) -> None:
    folder = ROOT / "mods" / modid / "src/main/resources/assets" / modid / "sounds"
    folder.mkdir(parents=True, exist_ok=True)
    wav = folder / f"{name}.wav"
    ogg = folder / f"{name}.ogg"
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "4", str(ogg)], check=True)
    wav.unlink()
    print("wrote", ogg.relative_to(ROOT))


# ---------------------------------------------------------------- ninjacatskies

# strand_chime: clack, then a bell (inharmonic partials) — code pitches it per Strand.
bell = tone(880, 1.6, 0.003, 0.5, harmonics=((1, 1.0), (2.0, 0.5), (2.76, 0.35), (5.4, 0.12))) * 0.7
chime = normalize(mix(clack(), bell, offsets=[0, int(0.06 * SR)]))
write("strand_chime", "ninjacatskies", chime)

# post_seat: knock + short upward zip (thread pulled taut).
knock = tone(140, 0.25, 0.001, 0.07, harmonics=((1, 1.0), (1.9, 0.4), (3.1, 0.2)))
n = int(0.18 * SR)
t = np.arange(n) / SR
zip_ = np.sin(2 * np.pi * (600 + 1400 * t / 0.18) * t) * env(n, 0.002, 0.06) * 0.35
write("post_seat", "ninjacatskies", normalize(mix(knock, zip_, offsets=[0, int(0.05 * SR)])))

# loom_hum: 4 s, three detuned low partials with slow beating, loop-safe (fade ends).
n = int(4.0 * SR)
t = np.arange(n) / SR
hum = (np.sin(2 * np.pi * 55.0 * t) + 0.6 * np.sin(2 * np.pi * 55.6 * t) + 0.3 * np.sin(2 * np.pi * 110.3 * t)
       + 0.15 * np.sin(2 * np.pi * 164.8 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t)))
fade = np.minimum(1, np.minimum(t / 0.4, (4.0 - t) / 0.4))
write("loom_hum", "ninjacatskies", normalize(hum * fade, 0.6))

# reweave: nine bell partials stacking into a chord over 4 s, then a shuttle run.
pitches = [0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30, 1.45, 1.60]
parts = []
offs = []
for i, p in enumerate(pitches):
    parts.append(tone(440 * p, 3.5, 0.01, 1.2, harmonics=((1, 1.0), (2.0, 0.4), (2.76, 0.25))) * 0.5)
    offs.append(int(i * 0.35 * SR))
chord = mix(*parts, offsets=offs)
run = mix(*[clack() * 0.6 for _ in range(8)], offsets=[int((4.2 + i * 0.09) * SR) for i in range(8)])
swell = tone(110, 6.0, 1.5, 2.5, harmonics=((1, 1.0), (2, 0.3), (3, 0.15))) * 0.5
write("reweave", "ninjacatskies", normalize(mix(chord, run, swell)))

# page: paper flick.
write("page", "ninjacatskies", normalize(noise(0.14, 0.004, 0.04, lowpass=3) * 0.6, 0.5))

# ---------------------------------------------------------------- voidloom

grit = noise(0.25, 0.01, 0.09, lowpass=2) * 0.5
write("loomframe_sift", "voidloom", normalize(mix(clack(), grit, offsets=[0, int(0.03 * SR)]), 0.7))

thunk = tone(120, 0.3, 0.001, 0.09, harmonics=((1, 1.0), (2.3, 0.3)))
wet = noise(0.2, 0.005, 0.07, lowpass=12) * 0.4
write("barrel_settle", "voidloom", normalize(mix(thunk, wet), 0.7))

print("done")
