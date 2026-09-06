# Island / Skyblock Builder notes (INTERNAL)

Original island templates for **Ninjacat Skies** on NeoForge 1.21.1 using MelanX **Skyblock Builder 21.1.31**.

Do not ship this file under `pack/overrides`.

## Mod paths (from jar `SkyPaths`)

Runtime config root: `config/skyblockbuilder/`

| Role | Path |
|------|------|
| Template registry | `config/skyblockbuilder/templates.json5` |
| Island structure NBTs | `config/skyblockbuilder/templates/islands/*.nbt` |
| Starter inventory (global) | `config/skyblockbuilder/starter_inventory.json5` |
| Void / island spacing | `config/skyblockbuilder/world.json5` |
| Dimension void mode | `config/skyblockbuilder/dimensions.json5` |
| Spawn protection / height | `config/skyblockbuilder/spawn.json5` |
| Inventory timing | `config/skyblockbuilder/inventory.json5` |
| Team permissions | `config/skyblockbuilder/permissions.json5` |
| Structure/feature allow lists | `config/skyblockbuilder/structures.json5` |
| Auto-generated dumps | `config/skyblockbuilder/data/*.txt` (created on world join) |

Packwiz ships these via:

- `pack/overrides/config/skyblockbuilder/**` → instance `config/skyblockbuilder/**`

Canonical NBTs live under the mod path above. A mirror also exists at `pack/overrides/structures/islands/` for tooling/reference; **Skyblock Builder does not read that folder**.

## Islands (original)

| Difficulty | Display name | File | Footprint |
|------------|--------------|------|-----------|
| Normal (default) | Ninjacat Pad | `ninjacat_pad.nbt` | 9×9 grass/dirt, oak-log posts, north fence, lantern, crafting table, modest chest |
| Easy | Dojo Cottage | `dojo_cottage.nbt` | 11×11 pad + roofed cottage (windows, bed, lantern, flower pot), rich chest |
| Hard | Frayed Thread | `frayed_thread.nbt` | broken 3×3 (one edge missing), cracked deepslate + hanging roots flair, sapling + ceremony chest (Codex/Charter/Hub Key/Thread/ice×2+lava) |
| Hub (spawn) | Clowder Dock | `clowder_dock.nbt` | 15×15 grass pad, deepslate runner, iron beacon frame, lectern + **How to Start** book, chest (charter/hub key/Codex/starter book), cyan/white banner posts, glowing plaques facing spawn, sea lanterns |

Spawn island at world center (`mainSpawnIsland`) uses dedicated **`clowder_dock.nbt`** (not a difficulty template). Spawn faces **north** toward the beacon/lectern from `[7, 2, 12]`; offset `[-7, 0, -7]`. Standing plaque uses sign **rotation 0 (south)** so text faces the spawn apron.

Structures were generated with `INTERNAL/_gen_islands.py` (nbtlib), DataVersion **3955** (1.21.1). Nothing was copied from other modpack instances.

## Spawn kits / difficulty

Skyblock Builder exposes **one** global `starter_inventory.json5` (not per-template). For difficulty differentiation:

- Global starter inventory is **empty**
- **Easy** kit → rich chest (tools, food, ice/lava, **filled water bucket**, seeds, Codex, Charter, Hub Key, How to Start)
- **Normal** kit → modest chest (food/logs/ice/lava/**empty bucket**/yarn/Thread, Codex, Charter, Hub Key, How to Start)
- **Hard** kit → sparse chest (Codex, Thread×6, seeds/meal×4, Charter, Hub Key, How to Start, ice×2 + lava + empty bucket)

`inventory.json5` uses `initialInventoryType: "team"` and `clearInitialInventory: true` (wipes login kit on claim — chests restore ceremony tools).

Server config `difficultyPreset` (ninjacatskies) only affects the wiped login kit; **island template** is the real Easy/Normal/Hard choice.

## How to select islands in-game

1. Create / open a world with world type **Skyblock** (`skyblockbuilder:skyblock`).
   - Client: More World Options → Skyblock.
   - Dedicated server: set level-type / world preset to `skyblockbuilder:skyblock` (see MelanX docs; NeoForge may use the world preset tag).
2. On first join you land on **Clowder Dock** (dedicated 15×15 hub at world center).
3. Claim a pad (guided): right-click Island Charter or press **C** (Sky GUIs) → Create Team → pick template. Advanced shortcut: `/skyblock create <name>` (skips pad picker, uses Ninjacat Pad).
4. When creating a team (or via the template selection screen **“Please select a template”**), pick:
   - **Ninjacat Pad** (Normal, default — first in `templateList`)
   - **Dojo Cottage** (Easy)
   - **Frayed Thread** (Hard)
5. Useful commands (permission-gated): `/skyblock` team, home, spawn, visit; `/clowder hub` → **Clowder Hall** dimension (`clowderhall:clowder_hall`); `/clowder return` leaves Hall to the saved pad pos; Hub Key right-click = hub travel; Island Charter on Dock opens Create Team; on a pad seals spawn. Overworld **Clowder Dock** remains the skyblock `mainSpawnIsland`. Dock spawn protection does **not** block chest/lectern/item use.

Island spacing: `world.json5` → `islandDistance: 4096`, `surface: false` (true void). Overworld/Nether/End use custom skyblock generators (`dimensions.json5`).

## Regenerating NBTs

```powershell
python INTERNAL/_gen_islands.py
```

Then re-run the Dojo Cottage overlap fix if that script is updated separately, or fold the fix back into `_gen_islands.py` before regenerating.

## Clowder Hall hub dimension

- ID: **`clowderhall:clowder_hall`** (datapack dim under `mods/clowderhall` — void flat, `minecraft:the_void`, no oceans).
- `/clowder hub` and Hub Key teleport here; arrival builds the ceremony pad once (`ModDimensions.ensureHubHall`) if the reinforced-deepslate marker is missing.
- Entering stores previous dimension/pos in player `persistentData.clowderhall.hub_return`; `/clowder return` restores it (fallback: overworld shared spawn).
- Separate from overworld skyblock islands / Clowder Dock — do not conflate Dock spawn with Hall travel.

## Blockers / follow-ups

1. **Per-template starter inventory** is not supported by the mod; kits are chest-based (documented above).
2. First world join will create `config/skyblockbuilder/data/` dump files; no need to ship those.
3. Research extracts under `INTERNAL/_skyblockbuilder_jar_extract/` and `INTERNAL/_sb_ref/` are local only — not pack content.

LibX (`LibX-1.21.1-6.0.15.jar`) and Sky GUIs are present in `pack/mods`.

## Originality

Island names, layouts, and configs were authored for Ninjacat Skies. Format reference only from public MelanX / ATM10Sky config *shape* (field names); no foreign NBT maps or pack prose were copied into overrides.
