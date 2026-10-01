# Ninjacat Skies 0.10.5 — Wildlife Returns and Wild Herds Stay

Pack CurseForge client file **TBD**, server additional **TBD**. Ninjacat Skies Core 0.5.20 is CurseForge file **9018084**
(unchanged); Tribal Power 5.3.14 is **9023760**; Chocobos Reborn 1.1.4 is **9022598** (unchanged); Shamanic Mounts
0.1.5 is **9023646**.

105 mods (101 on the server): Ninjacat Skies Core 0.5.20, Tribal Power 5.3.14, Chocobos Reborn 1.1.4, Shamanic Mounts
0.1.5. Existing saves load as they are; no quest ids change.

See `docs/cf-changelog-0.10.5.md` for the player-facing notes.

- **Tribal Power 5.3.14** (sha1 `a46a776014b97686c914512a523e375460d1f222`): March creature repopulation
  (`entity/MarchRepopulation.java`; `[wildlife]` config: 60 s per player, ring 32-96 blocks, cap 6 creatures in a
  32-block radius, biome CREATURE list so mod-added animals return); tidy button sorts the Deep Cache, Wayfarer Satchel
  and camp vault (`InventorySorter.StorageSlot`).
- **Shamanic Mounts 0.1.5** (sha1 `2b0505458abf9e7735a1fe1c0a56dcc89f7779ab`): untamed mounts no longer despawn
  (`removeWhenFarAway` false); they were removed before players reached them, so none were ever met in the March.
- **Pack:** pins only; store page says Tribal Power 5.3.14.
