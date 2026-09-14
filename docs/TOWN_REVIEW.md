# Race town and Clowder village

Built in the project sources and previewed in the isolated Minecraft 1.21.1 world on the top-right monitor. These are block-built environments, not concept images. Changes and jars remain local and unpublished.

## Whiskerwind Race Town — Chocobo Square

- Replaces the sandstone atoll with a grass island, tapered stone underside and perimeter fencing.
- Feather Inn, Cloudhoof Stables, Tack & Thread workshop, Riders Lodge, four striped market stalls, lanterns, trees, named residents and cats.
- Cat-eared street arch, readable course signs, covered four-tier grandstand and infield garden.
- Buildings have accessible furnished interiors and usable crafting/storage stations. Northern entrances face the shared street.
- The new idle island displays the full championship circuit. Starting a race still paints the selected bird-class course; all eight course corridors remain clear.
- Arrival faces the town. Normal ticket travel successfully generated the hub and kept the rider mounted.
- Fixed water-course flooding by recessing water into the track surface with a solid floor. The preview remained contained after fluid updates. Surface-walking birds still receive their water-terrain speed bonus; the regression test covers that case.

## Lanternweave Village — Clowder Hall

- Warm spruce, birch and teal copper buildings around the existing ceremony square.
- Purring Hearth, Weavers Workshop, Clowder Commons and Lantern Library, plus two market stalls, a bell tower, picnic areas and nine-strand lantern walk.
- Workshop and library fixtures, named residents, cats, gardens and perimeter lighting.
- Preserves the original 15×15 ceremony area, including chest contents, welcome lectern, beacon and reweave ring. Existing inventory block entities are skipped during scenery upgrades.
- Normal `/clowder hub` travel generated and entered the village successfully; the original hub NPCs remained present.

## Validation and limits

- ChocoCraft: 72 automated tests passed; NeoForge and Fabric builds passed after the final water fix.
- Clowder Hall build passed with the final village plan.
- Spatial checks passed for all eight race corridors, gate/arrival clearance, village path continuity, ceremony preservation and resident spawn clearance.
- Final block-plan refinements were previewed through exported Minecraft functions from the same JSON plans, without another client restart. The final water-placement code compiled; the equivalent recessed-channel blocks were checked visually after fluid updates. A complete race and multiplayer session have not been rerun against the final jars.
- Existing unresolved distribution blocker: no available ChocoCraft release was returned by the pack's CurseForge API check. Local test jars do not fix the public release pin.

## Review files

- `race-town-in-game.png` and `clowder-village-in-game.png`: actual in-game overview screenshots.
- `town-review-builds/`: unpublished local NeoForge Core bundle and ChocoCraft builds for NeoForge/Fabric. Install only the ChocoCraft variant matching the loader.
- `town-review-evidence/`: build logs and spatial verification output.

The generators and spatial checks are checked into each working tree under `tools/generate_hub_towns.py` and `tools/verify_hub_town.py`. Runtime builders consume the generated JSON block plans once per managed-hub revision.
