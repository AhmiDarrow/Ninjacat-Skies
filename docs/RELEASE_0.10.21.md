# Ninjacat Skies 0.10.21 — Rod, Shard and a Meal

Pack CurseForge client file **9096325**, server additional **9096326**. Tribal Power 5.6.5 is CurseForge file **9096231** and Shamanic Mounts 0.1.16 is **9096218**. Ninjacat Skies Core 0.5.24 (9095225), Chocobos Reborn 1.1.14 (9091543) and Lithium 0.15.4 (8330365) are unchanged.

106 mods (102 on the server). Existing saves load as they are.

See `docs/cf-changelog-0.10.21.md` for the player-facing notes.

- **Tribal Power 5.6.5** (sha1 `f0f66fb1be121fe4ab82851adb66b7283e5ee807`): `wildlife/MarchFishing` cancels `ItemFishedEvent` in `tribalpower:the_march` and lands the haul itself (vanilla fish → Raw Glimmerfin, one in four Raw Silt Eel; an empty offhand bucket → Bucket of Glimmerfin, bucket spent; junk and treasure untouched); `recipe/lattice/amethyst_shards_from_block` (Echo Shatter, amethyst block → 4 shards, Earth, 4 s, 20 Pulse/s); Codex wildlife entry and hints; game test `marchRodLandsMarchFish` (546 tests).
- **Shamanic Mounts 0.1.16** (sha1 `25647c8b891c7f0c61f8bd1b0e8fa0192510732e`): `tack/FeedRules.mealHeal` (tame, meat, below full → heal by nutrition, floor 2, capped at max); `ShamanicMount.mobInteract` meat branch after the Diamond Apple (ItemTags.MEAT plus NeoForge raw/cooked meat tags, rotten flesh excluded); `MountEffects.fed` heart ring; Herd Book Keeping line; unit test `FeedRulesTest`.
- **Pack**: pins only.
