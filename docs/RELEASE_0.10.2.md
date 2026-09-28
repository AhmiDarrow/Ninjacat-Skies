# Ninjacat Skies 0.10.2 — Fair Odds

Pack CurseForge client file **TBD**, server additional **TBD**. Chocobos Reborn 1.1.1 is CurseForge file **9004058**; Tribal Power 5.3.11 is **9004145**.

105 mods (101 on the server): Ninjacat Skies Core 0.5.19, Tribal Power 5.3.11, Chocobos Reborn 1.1.1, Shamanic Mounts
0.1.3. Existing saves load as they are; no quest ids change.

See `docs/cf-changelog-0.10.2.md` for the player-facing notes. In the repo this release only moves two pins (`pack/modlist-resolved.json`, `tools/gates/test_cf_distribution.py`).
Chocobos Reborn 1.1.1 (`docs/RELEASE_1.1.1.md` there): rider-versus-rider contact outside heats, Rook's stake cap of
purse / odds, duel stakes capped at the course purse, heats with any finisher settling every bet. Tribal Power 5.3.11
(`docs/RELEASE_5.3.11.md` there): the March crops' AgriCraft soil needs widened so strength-1 seeds grow on farmland
and March soil, wild patches every chunk. The FullPackServer gate is the only check that parses Tribal's AgriCraft
files on 4.0.17, so it ran for this release.
