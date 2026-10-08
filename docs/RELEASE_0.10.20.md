# Ninjacat Skies 0.10.20 — Beans and Dirt

Pack CurseForge client file **pending**, server additional **pending**. Tribal Power 5.6.4 is CurseForge file **9095217** and Ninjacat Skies Core 0.5.24 is **9095225**. Shamanic Mounts 0.1.15 (9091546), Chocobos Reborn 1.1.14 (9091543) and Lithium 0.15.4 (8330365) are unchanged.

106 mods (102 on the server). Existing saves load as they are.

See `docs/cf-changelog-0.10.20.md` for the player-facing notes.

- **Tribal Power 5.6.4** (sha1 `9e7256c4d44b686907445a004ea94690a7b120d3`): `MarchCropBlock.mayPlaceOn` lets the Glimmer Bean root in Moonstone and Moss Agate (the Glimmer Ridge surface has no soil, so `wild_glimmer_bean` never passed its `would_survive` filter); `wild_glimmer_bean` added to the Crystal Fields' vegetal step; March Crops codex entry; game test `glimmerBeansRootInRidgeStone` (545 tests).
- **Ninjacat Skies Core 0.5.24** (sha1 `0923347d8880238b1559082e70400140f30ec4bd`, source `7ae1c8a8e8d7b76c23cbc7a0a883f031a3364a7a`): `guardians:frayed_totem_beddown` takes `minecraft:dirt` instead of `minecraft:rooted_dirt`.
- **Pack**: pins only.
