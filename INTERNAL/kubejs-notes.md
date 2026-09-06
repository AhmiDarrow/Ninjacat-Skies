# KubeJS scripts for Ninjacat Skies

- `startup_scripts/` — item modifications, event registration
- `server_scripts/` — recipes, tags, loot (Strand gates live here)
- `client_scripts/` — tooltips, JEI hide lists

## Voidloom stations (mod + tooltips)
- **Loomframe / Tension Barrel gameplay** lives in the `voidloom` Java mod (block entities). See `INTERNAL/voidloom-notes.md`.
- KubeJS still owns crafts/tags (`voidloom_recipes.js`) and client tooltips (`voidloom_tooltips.js`).


## Loom Braid (`braid_gates.js`)
- Only the AE2 `molecular_assembler` soft gate remains here (needs `ninjacatskies:braid_cord` at centre)
- Braid Cord is **spun at the Tension Post** (Java): Strand Filament + two of Clock/Swarm/Spark seated
- **Tribal Power jar is present** — Hum recipes live in the jar; do not re-add KubeJS Hum lead-ins

## Strand gates (`strand_gates.js`)
- Tension Post recipe (logs + Binding Knot + Thread)
- Soft Create `precision_mechanism` and AE2 controller crafts require a Binding Knot
- Removes any stray token / braid / fragment recipes (tokens come from Knot quests only)

## Loom Tension
- Lives in Java now: `mods/ninjacatskies/src/main/java/com/ninjacat/skies/core/tension/` (team-scoped via FTB Teams)
- `loom_tension.js` and `steward_lines.js` were removed 2026-09-06

## Voidloom sieve identity (`voidloom_sieve.js`)
- Additive `exdeorum:sieve` / `compressed_sieve` lines for voidloom meshes only: Loom Lint (all), Frayed Thread (flint+), Strand Filament (iron)
- `4 Loom Lint → Void Yarn`

## Recover softlock recipes (`voidloom_recipes.js`)
- `1 Frayed Thread → 3 string`; `4 string → 2 Void Yarn` (early)
- Better yarn: 2 string + pearl/chorus; Tension Barrel string+pearl → 2 yarn
- Early slime: 2 dirt + wheat seeds + bone meal → Binding Knot

Keep recipe changes documented in `docs/CHANGELOG.md`. Prefer tags over hardcoded mod item IDs when substituting Silent Gear / Nature's Aura.
