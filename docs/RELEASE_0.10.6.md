# Ninjacat Skies 0.10.6 — Hearth and Wire, Close at Heel, Lighter Everywhere

Pack CurseForge client file **9025478**, server additional **9025480**. Ninjacat Skies Core 0.5.21 is CurseForge file
**9025453**; Tribal Power 5.3.15 is **9025414**; Chocobos Reborn 1.1.5 is **9025422**; Shamanic Mounts 0.1.7 is
**9025439**.

105 mods (101 on the server). Existing saves load as they are; no quest ids change.

See `docs/cf-changelog-0.10.6.md` for the player-facing notes. This release is the 2026-10-01 optimisation pass across
all four of the owner's mods, profiled on a copy of the live hub world (`build/profile-report.md`), plus the features
and fixes since 0.10.5.

- **Tribal Power 5.3.15** (`docs/RELEASE_5.3.15.md` there): Hearth Pot fare, wireless owned plates, reforged bows,
  distinct spawn eggs, Codex polish with real Pulse values, swimmers in open water, profile fixes (bench shapes,
  station recipe index, ley collector, conductors).
- **Chocobos Reborn 1.1.5**: resting-bird move replay, stewards ignore door swings, soft course plans, faster skinning.
- **Shamanic Mounts 0.1.6 + 0.1.7**: follow by default and across dimensions; back-face culling, batched eye glow,
  cached part cuts, lighter glow/hide, cached owner.
- **Core 0.5.21** (`docs/cf-changelog-core-0.5.21.md`): hub natural spawning off, TownPlan apply caching, idle machine
  fast paths, Fray in about half the time, Craftweave overlay caching.
- **Pack:** `kubejs/server_scripts/hub_life.js` called a method scripts cannot see, threw on every player tick and never
  ran its sweep; fixed and throttled to once a second in the hub. `dock_stalls.js` filters the keeper check to the two
  keeper types (about 4x cheaper, same behaviour).
