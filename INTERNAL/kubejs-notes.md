# KubeJS scripts for Ninjacat Skies

- `startup_scripts/` — item modifications, event registration
- `server_scripts/` — recipes, tags, loot (Strand gates live here)
- `client_scripts/` — tooltips, JEI hide lists

## Voidloom stations (mod + tooltips)
- **Loomframe / Tension Barrel gameplay** lives in the `voidloom` Java mod (block entities). See `INTERNAL/voidloom-notes.md`.
- KubeJS still owns crafts/tags (`voidloom_recipes.js`) and client tooltips (`voidloom_tooltips.js`).


## Loom Braid (`braid_gates.js`)
- `ninjacatskies:braid_cord` from any pair of Clock/Swarm/Spark strand tokens (3 shapeless variants)
- Soft-gates AE2 `molecular_assembler` to require braid_cord
- **Tribal Power jar is present** (`tribalpower-2.0.1.jar` in `pack/mods`) — Hum recipes live in the jar
- Do **not** re-add KubeJS Hum lead-ins (JEI duplicates + progression bypass). Tribal chapter order: Chime → Shard → Copper → Chalk → Drumheart → Codex → …

## Strand gates (`strand_gates.js`)
- Distinct Strand token crafts (frayed_thread ×2 + flavored mats)
- Soft Create `precision_mechanism` and AE2 controller crafts require Voidloom binders
- **Spindle Loom Fragment** = all nine Strand tokens **+ `tribalpower:march_stone`** (March-attuned full clear)

## Loom Tension (`loom_tension.js`)
- Player `persistentData.ncs_tension` (int) — glue, not a nagging bar
- Strand token craft → +1; first `braid_cord` → +3; first `spindle_loom_fragment` → +5
- Soft unlocks: ≥5 Thread×4 · ≥9 Codex pages×2 · ≥14 spare braid×1

## Recover softlock recipes (`voidloom_recipes.js`)
- `1 Frayed Thread → 3 string`; `4 string → 2 Void Yarn` (early)
- Better yarn: 2 string + pearl/chorus; Tension Barrel string+pearl
- Early slime: 2 dirt + wheat seeds + bone meal → Binding Knot

Keep recipe changes documented in `docs/CHANGELOG.md`. Prefer tags over hardcoded mod item IDs when substituting Silent Gear / Nature's Aura.
