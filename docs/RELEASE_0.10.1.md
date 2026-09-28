# Ninjacat Skies 0.10.1 — The Fray

Pack CurseForge client file **9003974**, server additional **9003982**. Core 0.5.19 is CurseForge file **9003796**.

105 mods (101 on the server): Ninjacat Skies Core 0.5.19, Tribal Power 5.3.10, Chocobos Reborn 1.1.0, Shamanic Mounts
0.1.3. Existing saves load as they are; no quest ids change.

See `docs/cf-changelog-0.10.1.md` for the player-facing notes and `docs/cf-changelog-core-0.5.19.md` for Core. In the
repo:

- The Fray is a client sky feature now: `core/sky/FrayMath.java` (pure geometry, GameTested in `SkyGameTests`),
  `core/client/FrayRenderer.java` (drawn at `RenderLevelStageEvent` AFTER_SKY, each point projected onto the sky dome
  from the camera, soft ribbons, dark pass plus a violet rim that fades by day, gold lit thread; local lint motes),
  `core/client/ClientFray.java` (synced state, eased toward the server's value), `network/FraySyncPayload.java`.
- The server broadcasts the Fray every two seconds when it changes (`TensionEffects.broadcastFray`) and on login;
  `LoomTension.serverProgress` counts each online Clowder's nine seats plus its Reweave, so the thread lights on the
  last Fragment seat. `/skybound fray [<0..1>|off]` reads or holds it (`TensionEffects.frayOverride`).
- Config: `loom.frayDimension` (default `clowderhall:clowder_hall`) and `frayX/Y/Z` (default 0 63 -140, just past
  the gate-path's end at z -118 in `tools/hub_loomsend.py`). The cut is rooted 260 blocks below and frays 200 above.
- Verified on the guardians showcase pair (spectator, `clowder hub`, `execute in clowderhall:clowder_hall run tp`),
  day and night, open, half and lit; the screenshot driver lives in the session scratchpad, not the repo.
