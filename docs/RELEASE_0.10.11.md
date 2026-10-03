# Ninjacat Skies 0.10.11 — Smooth Riding, a Cooler March, Small Foals

Pack CurseForge client file **TBD**, server additional **TBD**. Chocobos Reborn 1.1.10 is CurseForge file
**9050926**; Tribal Power 5.3.18 is **9048526**; Shamanic Mounts 0.1.11 is **9050339** (0.1.10, 9049935, was never
pinned). Ninjacat Skies Core 0.5.21 (9025453) and Lithium 0.15.4 (8330365) are unchanged.

106 mods (102 on the server). Existing saves load as they are; no quest ids change.

See `docs/cf-changelog-0.10.11.md` for the player-facing notes.

- **Chocobos Reborn 1.1.10** (sha1 `9761a6c212e7e3f6b6d8867da41ec37daf8603f5`): rider authority with acknowledged
  teleports (no "moved wrongly" snap-backs; Heartfield's dip snapped fast riders ~3x a lap), the field played back
  from batched tick-stamped frames (on the full pack vanilla's entity updates froze it 4-15 ticks), `Race rescue:`
  reasons in the server log, `Race frames stalled` on clients. New race_frames / rider_teleport channels: client and
  server must match.
- **Tribal Power 5.3.18** (sha1 `540ed7abc77a77bcc7a415ed9ef068bedcc4179f`): the Ember Wastes take only hot, dry March
  ground (Reed Fen, Highlands, Steppe reach warmer climates); explored land keeps its biomes.
- **Shamanic Mounts 0.1.11** (sha1 `89065d33713b0c16ede18df01979fb33faf1325d`), with 0.1.10: tame mounts never fight
  each other; foals are born under a third of grown size and grow to full size over twenty minutes.
