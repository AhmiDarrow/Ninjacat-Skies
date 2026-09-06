# Voidloom (custom mod)

Pack-native Recover / Strand crafting. Enhances Ex Deorum; does not clone it.

## Items
- `void_yarn`, `binding_knot`, thread meshes (string/flint/iron), `spindle_hammer`, `spindle_crook`
- `loom_lint` (4 → yarn), `strand_filament` (iron-mesh rare catch; spun into Braid Cord at the Tension Post)
- Meshes tagged into `exdeorum:sieve_meshes` / `c:meshes`; share Ex Deorum tables **plus** their own lines (`voidloom_sieve.js`)

## Loomframe (`voidloom:loomframe`)
Block entity: 1 mesh slot, 1 input stack (≤64 dirt / coarse dirt / gravel), 4 output slots. Server tick, no GUI.

| Action | Result |
|--------|--------|
| Right-click with mesh | Stretches it (not consumed) |
| Right-click with grit | Loads the whole stack (up to 64) |
| Empty hand | Takes all scraps; else takes grit back; sneak also pulls the mesh |
| Hopper / pipe | Slot 0 insert (grit), slots 1–4 extract |

Every 50 ticks it sifts one grit: shuttle clack (`voidloom:loomframe_sift`), block dust while working, end-rod puff on a catch.
Scrap table rolls each line independently; mesh tier only adds lines:
- **Dirt:** flint 35%, clay 20%, Loom Lint 8%, Void Yarn 3%; flint+: iron nugget 10%, Frayed Thread 3%; iron+: iron nugget 12%, raw copper 6%, Strand Filament 2%; gold/diamond/netherite: Filament +4%
- **Gravel:** flint 30%, iron nugget 15%; flint+: gold nugget 6%, Thread 3%; iron+: raw copper 6%, Filament 2%; better: Filament +4%

## Tension Barrel (`voidloom:tension_barrel`)
Block entity: water charge (≤8; a bucket = 4, empty bucket handed straight back), dirt / string / pearls (≤8 each), 3 output slots.

| Inputs | Output | Time |
|--------|--------|------|
| 1 water measure + 1 dirt | 1 clay ball | 160t |
| 1 string + 1 ender pearl | 2 Void Yarn | 120t |

Teal ring particle turns on the rim while working; `voidloom:barrel_settle` + splash on finish. Empty hand takes outputs; sneak pulls dry inputs. Hopper: slot 0 insert (water buckets accepted, empty bucket goes to an output slot), outputs extract.

Sounds are synthesised originals from `tools/generate_sounds_loom.py`; textures from `tools/generate_textures_loom.py`.
