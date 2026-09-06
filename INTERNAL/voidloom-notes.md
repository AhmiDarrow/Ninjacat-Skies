# Voidloom (custom mod)

Pack-native Recover / Strand crafting. Enhances Ex Deorum; does not clone it.

## Items
- `void_yarn`, `binding_knot`, thread meshes (string/flint/iron), `spindle_hammer`, `spindle_crook`
- Meshes tagged into `exdeorum:sieve_meshes` / `c:meshes` via KubeJS; share string/flint/iron sieve drop tables

## Loomframe (`voidloom:loomframe`)
Block entity, **1 mesh slot**, no GUI.

| Action | Result |
|--------|--------|
| Right-click with voidloom / Ex Deorum / `c:meshes` mesh | Inserts mesh (mesh not consumed by later sifts) |
| Empty-hand | Removes mesh |
| Right-click dirt / coarse dirt / gravel **while mesh present** | Consumes 1 grit; 3s cooldown; small bonus scrap |

Bonus table (not a full sieve):
- **Dirt / coarse dirt:** flint (common), clay ball (~25%), void yarn (~5%)
- **Gravel:** flint (common), iron nugget (~20%)

Place an Ex Deorum sieve beside it for real sieving; Loomframe is Recover flair + a trickle of early scraps.

## Tension Barrel (`voidloom:tension_barrel`)
Block entity, **2 input seals + 1 output**, server tick, no GUI.

| Inputs | Output | Time |
|--------|--------|------|
| Water bucket (iron or porcelain) + dirt/coarse dirt | Clay ball; empty bucket returned to last user | ~10s (200t) |
| String + ender pearl | Void yarn | ~8s (160t) |

- Right-click accepted items to insert (one each).
- Empty-hand takes finished output first, then last inserted input.
- Contents drop when the block breaks.

KubeJS still owns shaped/shapeless crafts for yarn/meshes/stations (`pack/overrides/kubejs/server_scripts/voidloom_recipes.js`).
