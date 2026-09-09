# Release verification notes (internal — never part of a public changelog)

## 0.7.1-alpha
### Verified
Gates: sanitized public surface, KubeJS-under-Rhino, quest item audit (1211 items, 0 missing, 0 dead ends), reachability, steward-cache id baseline, runtime ids, life rewards, CF distribution and export dry-run. GameTests: guardians 4/4, ninjacatskies 7/7, voidloom 5/5. Full-pack dedicated server: 39 chapters / 1567 quests load, 15,021 recipes, 11/11 KubeJS scripts, no loot-table or recipe errors from our data. Client: renderer, animation, facing (no `flipFacing` needed), arena loop (screenshots kept with the private art files).

### Still open
- Balance remains first-guess.
- The renderer was seen on llvmpipe at 1280×720; a real GPU has not drawn it yet, but the geometry, textures and emissive pass are confirmed.


### Tooling introduced
- `tools/gates/test_kubejs_rhino.py` + `tools/gates/rhino/RhinoCheck.java`: every KubeJS script parsed with the pack's Rhino; flags `const` inside loop/try blocks (Rhino throws "redeclaration" on re-execution).
- `tools/guardians_showcase.py` + `client/GuardianShowcase.java`, gradle runs `showcaseServer` / `showcaseClient` (Xvfb + `LIBGL_ALWAYS_SOFTWARE=1`): headless client play test; screenshots in `INTERNAL/guardians/playtest/`.
- `tools/export_server_pack.py` + `verify_server()` in `tools/gates/test_export_archive.py`; `upload_curseforge.py --parent-file-id` (an additional file must not carry gameVersions).
- Quest ids: `generate_quests.late_ids()` per-chapter 0x8000+ block; `test_steward_caches` checks the 0.6.1 id baseline as a subset.
- The two Create Dragons Plus loot-table overrides are deliberate log silencers — see `create_dragons_plus_loot_overrides.md`.

## 0.7.0-alpha
### Verified
Headless game tests in the build: every arena plan loads, all thirteen guardians run their fight for 400 ticks against a target and complete their death clip, and the totem loop (build → pull in → fight → win → relic → return) runs end to end. **The client renderer is compile-checked only** — no client could run in the build environment — so the first thing to check in-game is that the bosses render facing their targets; if they face away, launch with `-Dguardians.flipFacing=true` and tell me, it is a one-line export convention fix.

