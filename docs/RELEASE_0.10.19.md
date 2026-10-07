# Ninjacat Skies 0.10.19 — Said Once

Pack CurseForge client file **TBD**, server additional **TBD**. Tribal Power 5.6.3 is CurseForge file **9091537**, Shamanic Mounts 0.1.15 is **9091546**, Chocobos Reborn 1.1.14 is **9091543** and Ninjacat Skies Core 0.5.23 is **9091550**. Lithium 0.15.4 (8330365) is unchanged.

106 mods (102 on the server). Existing saves load as they are.

See `docs/cf-changelog-0.10.19.md` for the player-facing notes.

- **Tribal Power 5.6.3** (sha1 `7b0c34dad694e3846167d847408f5e267b0b35be`): hint tooltips scoped to its own items; pouch pickups animate and count; `setChanged` on mesh/font/station/resonator switches; Seal Loom tests only its sealed recipe per beat; Ley Lens reuses the tick's `LeyField`; `copyTag` → `getUnsafe` on read paths; Ley sight HUD lang keys; duel-map and placing-snapshot leaks; null-face guards on pedestal and cache.
- **Shamanic Mounts 0.1.15** (sha1 `60f66758fa235cf22dacc4eb90033bfa9d449d91`): hint scope; ghost-rider dismount refusal fixed for removed or cross-level riders; `TrialPending` saves the trial saddle and hands it back on load; `mayPlace` on bag slots requires bags; herd `places` pruned on release.
- **Chocobos Reborn 1.1.14** (sha1 `eab0ee04d2c833f8cfffe91b260a290bf6a0c47a`): hint scope; `RaceFrameSender.reset()` on server stop; `Locale.ROOT` queue clock; `RemoteRaceFrames.clear()` resets stall tracking.
- **Ninjacat Skies Core 0.5.23** (sha1 `f17f06f8889adf1b1d1325e32698ca826d85762a`, source `b47a40107103e7d2b618db432594887677463a43`): Ninjacat Lib hint handler scoped to the companion namespaces; guardian reload fixes (First Cut gap timer, Sealbreaker glyphs, Tangle webs, Lint Golem void balls, Unwoven gravel tag, Hivemind count, Cogwright tile 0); Driftwrecks pillar AIOOBE, remnant stack sync, atlas channel guard, `Mob`-gated death hook; Loomframe progress clamp and save throttle; Tension Barrel save throttle; Clowder Hall `tryParse`, BE-only lookups, `TownPlan.reset()`; Craftweave `applyPick` by key and chip index cache; static `SavedData.Factory` hoists.
- **Pack**: `voidloom_tooltips.js` drops 22 Tribal Power lines (and their `ninjacatpack` lang keys) that restated or contradicted TP 5.6.2 hints; the no-op `assets/ninjacatskies/lang` override is removed and the codex gate asserts it stays gone; `check_reachability.py` no longer reads `sys.argv` at import (the gate scanned zero jars under `unittest discover`) and matches datapack paths with `as_posix()`; `export_curseforge.py` / `export_server_pack.py` read MC/NeoForge versions from `pack.toml`.
