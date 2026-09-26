# Ninjacat Skies 0.8.14 — Every drum sounds

Pack CurseForge client file **TBD**, server additional **TBD**.

Ninjacat Skies Core 0.5.16 and Tribal Power 5.3.7. Existing saves load as they are; no quest ids change, and
the mod list is unchanged at 104. Shamanic Mounts still waits for CurseForge's approval.

- **Ninjacat Skies Core 0.5.16** (project 1689718, file **8978706**): the twelve guardian oggs opened with a
  Theora stream (a cover picture ffmpeg kept) and never played; remuxed audio-only with identical durations.
  New gate `SoundFiles` (`tools/gates/test_sound_files.py`) refuses any shipped ogg that is not plain Vorbis.
- **Tribal Power 5.3.7** (project 1684851, file **8978709**): A S D F and the arrows always drum after the
  bound lane keys; guardian songs are listed only with Core 0.5.16 or later.
