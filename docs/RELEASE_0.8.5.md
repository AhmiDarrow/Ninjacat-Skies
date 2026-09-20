# Ninjacat Skies 0.8.5 — Frames to spare

Pack CurseForge client file **8933330**, server additional **8933332**.

Seven performance mods, Tribal Power 3.7.0, and a server pack that no longer ships the
client's renderer at it. Existing saves load as they are; no quest ids change and no
worldgen moves.

- **Sodium 0.8.13** (project 394468, file 8756580) with **Reese's Sodium Options**
  (511319, 8891797) for a settings screen that is not a wall of toggles. The pack had no
  rendering optimiser at all — no Embeddium, no Rubidium — so this is the first one, and
  it sits alongside the ImmediatelyFast, EntityCulling, FerriteCore and ModernFix that
  were already here.
- **BadOptimizations** (949555, 7338300) and **Dynamic FPS** (335493, 7546938): the first
  cuts work the client repeats for no reason, the second idles the game down when the
  window is not in front, which matters on a pack this size.
- **AI Improvements** (233019, 5426792) and **Saturn** (670986, 6139965) are the two that
  help a server: cheaper mob goal ticking and less garbage from chunk and entity work.
- **spark** (361579, 6225208) ships on both sides, so `/spark profiler` is available when
  someone reports a tick that will not come down instead of being a thing they have to go
  and install first.
- **Tribal Power 3.7.0 - The carried kit** (project 1684851, file **8933246**): Spiritgear
  Shears and Hoe, the Spirit Flask and Greater Spirit Flask, the Totem Wrench, the
  Weaver's Wand, and a Tidy button on player, cache and vanilla container screens. It also
  carries its own performance pass — neighbour lookups instead of cube scans around camps,
  and HUD and screen work moved off the frame. Changelog: the mod's `RELEASE_3.7.0.md`.
- **AgriCraft crossing is reachable now.** `mutation_chance_multiplier` goes to 3.0, so a
  cross crop ringed with parents seeds inside a play session rather than a weekend, and two
  quest lines explain the loop the mod never does: a second set of sticks makes a cross
  crop, and fertility decides which plants get picked as parents.

**The server pack leaves the client-only mods out.** Four of the seven are client-side, and
on a dedicated server that is not a harmless no-op: Sodium's service layer runs from
`ModDirTransformerDiscoverer`, before NeoForge reads any mod's side, and calls into LWJGL.
A server with `sodium` in `mods/` dies on `NoClassDefFoundError: org/lwjgl/Version` before
a single mod loads. `tools/cf_distribution.py` grew `is_client_only`, the server export
drops those four from `server-manifest.json`, and `tools/full_pack_server.py` now stages
what a server actually installs rather than everything in `pack/mods` — so the boot gate
tests the real thing. AppleSkin, Controlling and ImmediatelyFast stay in deliberately: they
have shipped in working server zips since 0.7, and AppleSkin syncs saturation server-side.
The client zip carries all 104 mods; the server zip installs 100.

Pins: Ninjacat Skies Core 0.5.4 (project 1689718, file **8927258**), Tribal Power 3.7.0
(project 1684851, file **8933246**), Chocobos Reborn 1.0.8 (project 1699008, file
**8926685**). Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
