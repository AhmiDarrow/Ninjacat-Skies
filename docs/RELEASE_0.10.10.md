# Ninjacat Skies 0.10.10 — In Their Element, and Lithium

Pack CurseForge client file **9043976**, server additional **9043980**. Chocobos Reborn 1.1.9 is CurseForge file
**9043833**; Lithium 0.15.4 is project 360438 file **8330365**. Ninjacat Skies Core 0.5.21 (9025453), Tribal Power
5.3.17 (9034294) and Shamanic Mounts 0.1.9 (9034426) are unchanged.

106 mods (102 on the server). Existing saves load as they are; no quest ids change.

See `docs/cf-changelog-0.10.10.md` for the player-facing notes.

- **Chocobos Reborn 1.1.9** (sha1 `9b7e383118932925725433850eabf6c2a4020da6`): every water / ridge / lava shortcut
  pays for the bird that suits it, a field floored off the best rider, remote birds drawn where they are,
  `COURSE_VERSION` 16 (courses re-lay on next use).
- **Lithium 0.15.4** (`lithium-neoforge-0.15.4+mc1.21.1.jar`, sha1 `97212e45c963730bbfc7c44780df99317814c21b`), both
  sides. `pack/overrides/config/lithium.properties` turns off four mixin groups that ModernFix or Saturn already
  overwrite (the boot logs printed "Method overwrite conflict ... Skipping method"): `collections.chunk_tickets`,
  `chunk.no_locking`, `world.temperature_cache`, `alloc.composter`.
- Measured on the hub world copy (`build/profile-server`, one real client, 120 s spark per spot, same mods with and
  without Lithium): median MSPT Loom's End 7.22 -> 6.23, Chocobo Square 3.14 -> 2.55, March wild 8.15 -> 4.95 (the
  March "without" run had heavy system load; treat that one as noisy). The 2-7 s stall on teleporting into the March
  happens with and without Lithium (chunk loading), as in earlier profiles. The full-pack client booted and joined
  with Lithium.
